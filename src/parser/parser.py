"""Recursive-descent parser for the mini numerical language.

Grammar (all binary operators are left-associative)::

    program    := statement* EOF
    statement  := declaration | assignment | if | while | print | block
    declaration:= ("int" | "float") IDENT ("=" expr)? ";"
    assignment := IDENT "=" expr ";"
    if         := "if" "(" expr ")" body ("else" body)?
    while      := "while" "(" expr ")" body
    print      := "print" expr ";"
    block      := "{" statement* "}"
    body       := block | (non-declaration statement)   -- wrapped in a Block
    expr       := equality
    equality   := relational (("==" | "!=") relational)*
    relational := additive (("<" | ">" | "<=" | ">=") additive)*
    additive   := term (("+" | "-") term)*
    term       := unary (("*" | "/") unary)*
    unary      := "-" unary | primary
    primary    := INT | FLOAT | IDENT | "(" expr ")"

Precedence (loosest to tightest): equality, relational, additive,
multiplicative, unary minus. A dangling ``else`` binds to the nearest ``if``.
Declarations are not allowed as the unbraced body of ``if``/``while`` because
they would otherwise leak into the enclosing scope.
"""

from typing import List, Optional

from src.ast import nodes as n
from src.ast.types import Type
from src.diagnostics.errors import ParseError
from src.diagnostics.location import SourceLocation
from src.lexer.lexer import tokenize
from src.lexer.tokens import Token, TokenKind

_K = TokenKind


class Parser:
    def __init__(self, tokens: List[Token]):
        self._tokens = tokens
        self._i = 0

    # -- token helpers -----------------------------------------------------
    def _peek(self, offset: int = 0) -> Token:
        idx = min(self._i + offset, len(self._tokens) - 1)
        return self._tokens[idx]

    def _advance(self) -> Token:
        tok = self._tokens[self._i]
        if tok.kind != _K.EOF:
            self._i += 1
        return tok

    def _check(self, *kinds: TokenKind) -> bool:
        return self._peek().kind in kinds

    def _match(self, *kinds: TokenKind) -> Optional[Token]:
        return self._advance() if self._check(*kinds) else None

    def _expect(self, kind: TokenKind, context: str) -> Token:
        tok = self._peek()
        if tok.kind != kind:
            raise ParseError(
                f"expected {kind.value} {context}, found {self._describe(tok)}", tok.loc
            )
        return self._advance()

    @staticmethod
    def _describe(tok: Token) -> str:
        if tok.kind == _K.EOF:
            return "end of input"
        return f"'{tok.lexeme}'"

    # -- program / statements ---------------------------------------------
    def parse_program(self) -> n.Program:
        start = self._peek().loc
        stmts = []
        while not self._check(_K.EOF):
            stmts.append(self._statement())
        return n.Program(start, stmts)

    def _statement(self) -> n.Node:
        tok = self._peek()
        if tok.kind in (_K.KW_INT, _K.KW_FLOAT):
            return self._declaration()
        if tok.kind == _K.IDENT:
            return self._assignment()
        if tok.kind == _K.KW_IF:
            return self._if()
        if tok.kind == _K.KW_WHILE:
            return self._while()
        if tok.kind == _K.KW_PRINT:
            return self._print()
        if tok.kind == _K.LBRACE:
            return self._block()
        raise ParseError(f"unexpected {self._describe(tok)} at start of statement", tok.loc)

    def _declaration(self) -> n.Declaration:
        kw = self._advance()
        var_type = Type.INT if kw.kind == _K.KW_INT else Type.FLOAT
        name_tok = self._expect(_K.IDENT, f"after type '{kw.lexeme}'")
        init = None
        if self._match(_K.ASSIGN):
            init = self._expr()
        self._expect(_K.SEMI, "after declaration")
        return n.Declaration(kw.loc, var_type, name_tok.lexeme, init, name_tok.loc)

    def _assignment(self) -> n.Assignment:
        name_tok = self._advance()
        self._expect(_K.ASSIGN, f"after variable '{name_tok.lexeme}'")
        value = self._expr()
        self._expect(_K.SEMI, "after assignment")
        return n.Assignment(name_tok.loc, name_tok.lexeme, value)

    def _block(self) -> n.Block:
        lbrace = self._expect(_K.LBRACE, "to start a block")
        stmts = []
        while not self._check(_K.RBRACE):
            if self._check(_K.EOF):
                raise ParseError(
                    f"expected '}}' to close the block opened at {lbrace.loc.describe()}",
                    self._peek().loc,
                )
            stmts.append(self._statement())
        self._advance()
        return n.Block(lbrace.loc, stmts)

    def _body(self, construct: str) -> n.Block:
        tok = self._peek()
        if tok.kind == _K.LBRACE:
            return self._block()
        if tok.kind in (_K.KW_INT, _K.KW_FLOAT):
            raise ParseError(
                f"a declaration cannot be the unbraced body of '{construct}'; use '{{ }}'",
                tok.loc,
            )
        stmt = self._statement()
        return n.Block(stmt.loc, [stmt])

    def _paren_condition(self, construct: str) -> n.Expr:
        self._expect(_K.LPAREN, f"after '{construct}'")
        cond = self._expr()
        self._expect(_K.RPAREN, f"after the condition of '{construct}'")
        return cond

    def _if(self) -> n.IfStmt:
        kw = self._advance()
        cond = self._paren_condition("if")
        then_block = self._body("if")
        else_block = self._body("else") if self._match(_K.KW_ELSE) else None
        return n.IfStmt(kw.loc, cond, then_block, else_block)

    def _while(self) -> n.WhileStmt:
        kw = self._advance()
        cond = self._paren_condition("while")
        return n.WhileStmt(kw.loc, cond, self._body("while"))

    def _print(self) -> n.PrintStmt:
        kw = self._advance()
        value = self._expr()
        self._expect(_K.SEMI, "after print")
        return n.PrintStmt(kw.loc, value)

    # -- expressions -------------------------------------------------------
    def _expr(self) -> n.Expr:
        return self._binary_level(0)

    # Operator levels from loosest to tightest binding; the unary/primary
    # levels are handled separately below.
    _LEVELS = [
        {_K.EQ: "==", _K.NE: "!="},
        {_K.LT: "<", _K.GT: ">", _K.LE: "<=", _K.GE: ">="},
        {_K.PLUS: "+", _K.MINUS: "-"},
        {_K.STAR: "*", _K.SLASH: "/"},
    ]

    def _binary_level(self, level: int) -> n.Expr:
        if level == len(self._LEVELS):
            return self._unary()
        ops = self._LEVELS[level]
        left = self._binary_level(level + 1)
        while self._peek().kind in ops:
            op_tok = self._advance()
            right = self._binary_level(level + 1)
            # located at the first token of the left operand
            left = n.BinaryExpr(left.loc, ops[op_tok.kind], left, right, op_tok.loc)
        return left

    def _unary(self) -> n.Expr:
        if self._check(_K.MINUS):
            op = self._advance()
            return n.UnaryExpr(op.loc, "-", self._unary())
        return self._primary()

    def _primary(self) -> n.Expr:
        tok = self._peek()
        if tok.kind == _K.INT_LIT:
            self._advance()
            return n.IntLiteral(tok.loc, tok.value)
        if tok.kind == _K.FLOAT_LIT:
            self._advance()
            return n.FloatLiteral(tok.loc, tok.value, tok.lexeme)
        if tok.kind == _K.IDENT:
            self._advance()
            return n.Identifier(tok.loc, tok.lexeme)
        if tok.kind == _K.LPAREN:
            self._advance()
            inner = self._expr()
            self._expect(_K.RPAREN, "to close the parenthesized expression")
            return inner
        raise ParseError(f"expected an expression, found {self._describe(tok)}", tok.loc)


def parse(source: str) -> n.Program:
    """Lex and parse ``source`` into a ``Program`` AST."""
    return Parser(tokenize(source)).parse_program()
