"""Hand-written lexer for the mini numerical language.

Design notes
------------
* Positions are 1-based (line, column) and refer to the first character of the
  token. A newline resets the column to 1.
* A numeric literal is an integer (``42``) or a decimal float (``1.5``). A float
  needs digits on both sides of the dot; ``1.``, ``.5``, ``1.2.3`` and ``12ab``
  are reported as malformed rather than silently split into several tokens.
* Comments: ``// ...`` to end of line and ``/* ... */`` (not nested).
"""

from fractions import Fraction
from typing import List

from src.diagnostics.errors import LexError
from src.diagnostics.location import SourceLocation
from src.lexer.tokens import KEYWORDS, Token, TokenKind

_SINGLE_CHAR = {
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "/": TokenKind.SLASH,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    "{": TokenKind.LBRACE,
    "}": TokenKind.RBRACE,
    ";": TokenKind.SEMI,
}

_WHITESPACE = " \t\r\n\f\v"
_DIGITS = "0123456789"


def _is_digit(c: str) -> bool:
    # ``'' in "0123"`` is True in Python, so the emptiness guard matters.
    return bool(c) and c in _DIGITS


def _is_ident_start(c: str) -> bool:
    return bool(c) and c.isascii() and (c.isalpha() or c == "_")


def _is_ident_part(c: str) -> bool:
    return _is_ident_start(c) or _is_digit(c)


class Lexer:
    def __init__(self, source: str):
        self._src = source
        self._pos = 0
        self._line = 1
        self._col = 1

    # -- character helpers -------------------------------------------------
    def _peek(self, offset: int = 0) -> str:
        idx = self._pos + offset
        return self._src[idx] if idx < len(self._src) else ""

    def _advance(self) -> str:
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        return ch

    def _loc(self) -> SourceLocation:
        return SourceLocation(self._line, self._col)

    # -- driver ------------------------------------------------------------
    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            self._skip_trivia()
            if self._pos >= len(self._src):
                tokens.append(Token(TokenKind.EOF, "", self._loc()))
                return tokens
            tokens.append(self._next_token())

    def _skip_trivia(self) -> None:
        while self._pos < len(self._src):
            ch = self._peek()
            if ch in _WHITESPACE:
                self._advance()
            elif ch == "/" and self._peek(1) == "/":
                while self._pos < len(self._src) and self._peek() != "\n":
                    self._advance()
            elif ch == "/" and self._peek(1) == "*":
                start = self._loc()
                self._advance()
                self._advance()
                while True:
                    if self._pos >= len(self._src):
                        raise LexError("unterminated block comment", start)
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
            else:
                return

    def _next_token(self) -> Token:
        loc = self._loc()
        ch = self._peek()

        if _is_digit(ch):
            return self._number(loc)
        if _is_ident_start(ch):
            return self._identifier(loc)

        if ch in "=<>!":
            self._advance()
            if self._peek() == "=":
                self._advance()
                kind = {
                    "=": TokenKind.EQ,
                    "<": TokenKind.LE,
                    ">": TokenKind.GE,
                    "!": TokenKind.NE,
                }[ch]
                return Token(kind, ch + "=", loc)
            if ch == "!":
                raise LexError("unexpected character '!' (only '!=' is supported)", loc)
            kind = {"=": TokenKind.ASSIGN, "<": TokenKind.LT, ">": TokenKind.GT}[ch]
            return Token(kind, ch, loc)

        if ch in _SINGLE_CHAR:
            self._advance()
            return Token(_SINGLE_CHAR[ch], ch, loc)

        raise LexError(f"unexpected character {ch!r}", loc)

    def _identifier(self, loc: SourceLocation) -> Token:
        start = self._pos
        while _is_ident_part(self._peek()):
            self._advance()
        text = self._src[start:self._pos]
        return Token(KEYWORDS.get(text, TokenKind.IDENT), text, loc)

    def _number(self, loc: SourceLocation) -> Token:
        start = self._pos
        while _is_digit(self._peek()):
            self._advance()
        is_float = False
        if self._peek() == ".":
            if not _is_digit(self._peek(1)):
                raise LexError("malformed number: digits expected after '.'", loc)
            is_float = True
            self._advance()  # '.'
            while _is_digit(self._peek()):
                self._advance()
        nxt = self._peek()
        if nxt == "." or _is_ident_start(nxt):
            raise LexError(
                f"malformed number: unexpected {nxt!r} after "
                f"'{self._src[start:self._pos]}'",
                loc,
            )
        text = self._src[start:self._pos]
        kind = TokenKind.FLOAT_LIT if is_float else TokenKind.INT_LIT
        return Token(kind, text, loc, Fraction(text))


def tokenize(source: str) -> List[Token]:
    """Convenience wrapper: tokenize ``source`` and return the token list (ends with EOF)."""
    return Lexer(source).tokenize()
