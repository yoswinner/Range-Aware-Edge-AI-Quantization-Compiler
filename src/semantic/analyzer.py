"""Semantic analyzer.

Checks performed
----------------
* declaration before use (variables and assignment targets);
* duplicate declaration within one scope (block scoping, shadowing allowed);
* operand compatibility: arithmetic/relational operators need numeric
  (``int``/``float``) operands; a relational result is ``bool`` and cannot
  itself be an arithmetic operand;
* assignment/initializer compatibility: ``int`` accepts int and bool,
  ``float`` accepts int, float and bool, but a ``float`` value is never
  implicitly narrowed to ``int``;
* control-flow validity: ``if``/``while`` conditions must be ``int`` or ``bool``;
* ``print`` operands must be well-typed.

Typing of operators: ``+ - *`` give ``float`` if either operand is ``float``
else ``int``; ``/`` is real division and always gives ``float`` (this matches the
review's rule that division is not automatically integral); relational
operators give ``bool``.

An initializer is analysed *before* its variable is declared, so
``int x = x + 1;`` is an undeclared-variable error. All diagnostics are
collected (not just the first); an expression with a failed operand gets the
``ERROR`` type so one mistake does not cascade into many.
"""

from dataclasses import dataclass, field
from typing import List

from src.ast import nodes as n
from src.ast.types import Type
from src.diagnostics.errors import Diagnostic, SemanticError
from src.diagnostics.location import SourceLocation
from src.semantic.symbols import Symbol, SymbolTable

_ARITH = {"+", "-", "*"}
_RELATIONAL = {"<", ">", "<=", ">=", "==", "!="}


@dataclass
class SemanticResult:
    symbols: List[Symbol] = field(default_factory=list)
    diagnostics: List[Diagnostic] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _assignable(target: Type, source: Type) -> bool:
    if target == Type.INT:
        return source in (Type.INT, Type.BOOL)
    if target == Type.FLOAT:
        return source in (Type.INT, Type.FLOAT, Type.BOOL)
    return False


class SemanticAnalyzer:
    def __init__(self):
        self._table = SymbolTable()
        self._diags: List[Diagnostic] = []

    def analyze(self, program: n.Program) -> SemanticResult:
        self._table.push_scope()
        for stmt in program.statements:
            self._stmt(stmt)
        self._table.pop_scope()
        return SemanticResult(list(self._table.all_symbols), list(self._diags))

    def _error(self, message: str, loc: SourceLocation) -> None:
        self._diags.append(Diagnostic(message, loc))

    # -- statements --------------------------------------------------------
    def _stmt(self, stmt: n.Node) -> None:
        if isinstance(stmt, n.Block):
            self._table.push_scope()
            for s in stmt.statements:
                self._stmt(s)
            self._table.pop_scope()
        elif isinstance(stmt, n.Declaration):
            self._declaration(stmt)
        elif isinstance(stmt, n.Assignment):
            self._assignment(stmt)
        elif isinstance(stmt, n.IfStmt):
            self._condition(stmt.cond, "if")
            self._stmt(stmt.then_block)
            if stmt.else_block is not None:
                self._stmt(stmt.else_block)
        elif isinstance(stmt, n.WhileStmt):
            self._condition(stmt.cond, "while")
            self._stmt(stmt.body)
        elif isinstance(stmt, n.PrintStmt):
            self._expr(stmt.value)  # any well-typed expression may be printed
        else:  # pragma: no cover - parser cannot produce anything else
            raise TypeError(f"unknown statement {type(stmt).__name__}")

    def _declaration(self, decl: n.Declaration) -> None:
        init_ty = self._expr(decl.init) if decl.init is not None else None
        existing = self._table.lookup_current_scope(decl.name)
        if existing is not None:
            self._error(
                f"variable '{decl.name}' is already declared in this scope "
                f"(first declared at {existing.decl_loc.describe()})",
                decl.name_loc,
            )
            decl.symbol = None
        else:
            decl.symbol = self._table.declare(decl.name, decl.var_type, decl.name_loc)
        if init_ty is not None and init_ty != Type.ERROR:
            self._check_assignable(decl.var_type, init_ty, decl.name, decl.init.loc)

    def _assignment(self, stmt: n.Assignment) -> None:
        value_ty = self._expr(stmt.value)
        sym = self._table.lookup(stmt.name)
        if sym is None:
            self._error(f"assignment to undeclared variable '{stmt.name}'", stmt.loc)
            return
        stmt.symbol = sym
        if value_ty != Type.ERROR:
            self._check_assignable(sym.ty, value_ty, stmt.name, stmt.value.loc)

    def _check_assignable(self, target: Type, source: Type, name: str, loc) -> None:
        if not _assignable(target, source):
            self._error(
                f"cannot assign a '{source.value}' value to {target.value} "
                f"variable '{name}' (no implicit narrowing)",
                loc,
            )

    def _condition(self, cond: n.Expr, construct: str) -> None:
        ty = self._expr(cond)
        if ty not in (Type.INT, Type.BOOL, Type.ERROR):
            self._error(
                f"condition of '{construct}' must be int or bool, got '{ty.value}'",
                cond.loc,
            )

    # -- expressions -------------------------------------------------------
    def _expr(self, e: n.Expr) -> Type:
        ty = self._expr_type(e)
        e.ty = ty
        return ty

    def _expr_type(self, e: n.Expr) -> Type:
        if isinstance(e, n.IntLiteral):
            return Type.INT
        if isinstance(e, n.FloatLiteral):
            return Type.FLOAT
        if isinstance(e, n.Identifier):
            sym = self._table.lookup(e.name)
            if sym is None:
                self._error(f"use of undeclared variable '{e.name}'", e.loc)
                return Type.ERROR
            e.symbol = sym
            return sym.ty
        if isinstance(e, n.UnaryExpr):
            operand = self._expr(e.operand)
            if operand == Type.ERROR:
                return Type.ERROR
            if not operand.is_numeric():
                self._error(
                    f"unary '{e.op}' requires a numeric operand, got '{operand.value}'", e.loc
                )
                return Type.ERROR
            return operand
        if isinstance(e, n.BinaryExpr):
            lt = self._expr(e.left)
            rt = self._expr(e.right)
            if Type.ERROR in (lt, rt):
                return Type.ERROR
            if not (lt.is_numeric() and rt.is_numeric()):
                self._error(
                    f"operator '{e.op}' requires numeric operands, got "
                    f"'{lt.value}' and '{rt.value}'",
                    e.op_loc,
                )
                return Type.ERROR
            if e.op in _ARITH:
                return Type.FLOAT if Type.FLOAT in (lt, rt) else Type.INT
            if e.op == "/":
                return Type.FLOAT
            assert e.op in _RELATIONAL
            return Type.BOOL
        raise TypeError(f"unknown expression {type(e).__name__}")  # pragma: no cover


def analyze(program: n.Program) -> SemanticResult:
    """Annotate ``program`` in place and return the collected diagnostics."""
    return SemanticAnalyzer().analyze(program)


def check(program: n.Program) -> SemanticResult:
    """Like :func:`analyze` but raises :class:`SemanticError` if anything is wrong."""
    result = analyze(program)
    if not result.ok:
        raise SemanticError(result.diagnostics)
    return result
