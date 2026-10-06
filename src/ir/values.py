"""IR operands.

* ``Const``  – an immediate numeric constant (exact ``Fraction``).
* ``Temp``   – a compiler temporary ``tN``; assigned exactly once by
  construction, so it is already an SSA name.
* ``Var``    – a source variable. ``version is None`` before SSA construction;
  afterwards every ``Var`` is versioned (``x.1``, ``x.2``, ...).

``Temp`` and versioned ``Var`` are the "SSA names" the analyses attach facts to.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Union

from src.ast.types import Type


def format_number(x: Fraction) -> str:
    """Exact, human-readable number: ``10``, ``1.5``, ``0.25`` or ``1/3``."""
    if x.denominator == 1:
        return str(x.numerator)
    d = x.denominator
    twos = fives = 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    if d != 1:  # not a terminating decimal
        return f"{x.numerator}/{x.denominator}"
    k = max(twos, fives)
    scaled = abs(x.numerator) * 10 ** k // x.denominator  # exact: denominator | 10**k
    digits = str(scaled).rjust(k + 1, "0")
    text = digits[:-k] + "." + digits[-k:]
    return ("-" if x < 0 else "") + text


@dataclass(frozen=True)
class Const:
    value: Fraction
    ty: Type = Type.INT

    def __str__(self) -> str:
        text = format_number(self.value)
        if self.ty == Type.FLOAT and "." not in text and "/" not in text:
            text += ".0"
        return text


@dataclass(frozen=True)
class Temp:
    index: int

    def __str__(self) -> str:
        return f"t{self.index}"


@dataclass(frozen=True)
class Var:
    name: str
    version: Optional[int] = None

    def __str__(self) -> str:
        return self.name if self.version is None else f"{self.name}.{self.version}"


Value = Union[Const, Temp, Var]


def is_ssa_name(v: Value) -> bool:
    """True for operands that denote a single static definition."""
    return isinstance(v, Temp) or (isinstance(v, Var) and v.version is not None)
