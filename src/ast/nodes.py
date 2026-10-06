"""AST node classes.

Every node records the ``SourceLocation`` of its first token. A binary
expression is located at its left operand (the first token of the
sub-expression) and additionally stores ``op_loc``, the operator's own position,
which semantic diagnostics use. Expression nodes carry a ``ty`` annotation and
identifiers/declarations/assignments carry a ``symbol`` annotation; both are
filled in by semantic analysis (``None`` until then).
"""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, List, Optional

from src.ast.types import Type
from src.diagnostics.location import SourceLocation


@dataclass(eq=False)
class Node:
    loc: SourceLocation


# -- expressions -----------------------------------------------------------
@dataclass(eq=False)
class Expr(Node):
    ty: Optional[Type] = field(default=None, kw_only=True)


@dataclass(eq=False)
class IntLiteral(Expr):
    value: Fraction  # always integral


@dataclass(eq=False)
class FloatLiteral(Expr):
    value: Fraction  # exact decimal value
    text: str


@dataclass(eq=False)
class Identifier(Expr):
    name: str
    symbol: Any = field(default=None, kw_only=True)


@dataclass(eq=False)
class UnaryExpr(Expr):
    op: str  # only '-'
    operand: Expr


@dataclass(eq=False)
class BinaryExpr(Expr):
    op: str  # + - * / < > <= >= == !=
    left: Expr
    right: Expr
    op_loc: SourceLocation


# -- statements ------------------------------------------------------------
@dataclass(eq=False)
class Declaration(Node):
    """``int x = e;`` / ``float x;``. ``loc`` is the type keyword; ``name_loc``
    is the declared identifier. A declaration without initializer introduces a
    variable holding an externally supplied (statically unknown) value."""

    var_type: Type
    name: str
    init: Optional[Expr]
    name_loc: SourceLocation
    symbol: Any = field(default=None, kw_only=True)


@dataclass(eq=False)
class Assignment(Node):
    """``x = e;`` — ``loc`` is the position of the target identifier."""

    name: str
    value: Expr
    symbol: Any = field(default=None, kw_only=True)


@dataclass(eq=False)
class Block(Node):
    statements: List[Node]


@dataclass(eq=False)
class IfStmt(Node):
    cond: Expr
    then_block: Block
    else_block: Optional[Block]


@dataclass(eq=False)
class WhileStmt(Node):
    cond: Expr
    body: Block


@dataclass(eq=False)
class PrintStmt(Node):
    value: Expr


@dataclass(eq=False)
class Program(Node):
    statements: List[Node]
