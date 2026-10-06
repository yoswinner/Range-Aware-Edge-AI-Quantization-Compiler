"""Token definitions for the mini numerical language."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional

from src.diagnostics.location import SourceLocation


class TokenKind(Enum):
    # literals / names
    INT_LIT = "integer literal"
    FLOAT_LIT = "floating-point literal"
    IDENT = "identifier"
    # keywords
    KW_INT = "'int'"
    KW_FLOAT = "'float'"
    KW_IF = "'if'"
    KW_ELSE = "'else'"
    KW_WHILE = "'while'"
    KW_PRINT = "'print'"
    # arithmetic
    PLUS = "'+'"
    MINUS = "'-'"
    STAR = "'*'"
    SLASH = "'/'"
    # relational
    LT = "'<'"
    GT = "'>'"
    LE = "'<='"
    GE = "'>='"
    EQ = "'=='"
    NE = "'!='"
    # assignment / punctuation
    ASSIGN = "'='"
    LPAREN = "'('"
    RPAREN = "')'"
    LBRACE = "'{'"
    RBRACE = "'}'"
    SEMI = "';'"
    EOF = "end of input"


KEYWORDS = {
    "int": TokenKind.KW_INT,
    "float": TokenKind.KW_FLOAT,
    "if": TokenKind.KW_IF,
    "else": TokenKind.KW_ELSE,
    "while": TokenKind.KW_WHILE,
    "print": TokenKind.KW_PRINT,
}


@dataclass(frozen=True)
class Token:
    """A lexeme plus the position of its first character.

    ``value`` holds the exact numeric value of literals as a ``Fraction`` (a
    decimal literal such as ``1.5`` is represented exactly, which keeps the
    later interval arithmetic free of binary rounding error).
    """

    kind: TokenKind
    lexeme: str
    loc: SourceLocation
    value: Optional[Fraction] = None

    def __str__(self) -> str:
        return f"{self.loc} {self.kind.name} {self.lexeme!r}"
