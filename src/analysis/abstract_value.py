"""Abstract domain: an interval with an integrality flag, plus UNKNOWN.

An ``AbsVal`` describes every value an SSA name can take at run time:

* ``lo``/``hi``  – exact (``Fraction``) closed interval bounds, or both ``None``
  when the range is **UNKNOWN** (no finite bound could be proven);
* ``integral``   – ``True`` only if the value is *guaranteed* to be a whole
  number on every execution path.

Exact rational bounds mean interval arithmetic never rounds, so a computed
bound is never tighter than the true one because of floating-point error.

UNKNOWN is the top element for the range. ``reason`` (why it is unknown) and
``div_zero`` (a possible division by zero was flagged on the way) are
diagnostic payload only and are excluded from equality, so they can never
affect fixed-point convergence.

*Bottom* (no information yet, used while iterating) is not an ``AbsVal``; the
analysis represents it by the absence of a dictionary entry.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional

from src.ir.values import format_number


@dataclass(frozen=True)
class AbsVal:
    lo: Optional[Fraction]
    hi: Optional[Fraction]
    integral: bool
    reason: Optional[str] = field(default=None, compare=False)
    div_zero: bool = field(default=False, compare=False)

    def __post_init__(self):
        if (self.lo is None) != (self.hi is None):
            raise ValueError("lo and hi must both be set or both be None")
        if self.lo is not None and self.lo > self.hi:
            raise ValueError(f"empty interval [{self.lo}, {self.hi}]")

    # -- constructors ------------------------------------------------------
    @staticmethod
    def const(value: Fraction) -> "AbsVal":
        value = Fraction(value)
        return AbsVal(value, value, value.denominator == 1)

    @staticmethod
    def interval(lo, hi, integral: bool) -> "AbsVal":
        return AbsVal(Fraction(lo), Fraction(hi), integral)

    @staticmethod
    def unknown(integral: bool = False, reason: str = "range could not be bounded",
                div_zero: bool = False) -> "AbsVal":
        return AbsVal(None, None, integral, reason, div_zero)

    # -- queries -----------------------------------------------------------
    @property
    def is_unknown(self) -> bool:
        return self.lo is None

    def join(self, other: "AbsVal") -> "AbsVal":
        """Least upper bound: cover both intervals, AND the integrality flags.
        Used at phi nodes. UNKNOWN absorbs everything (conservative)."""
        integral = self.integral and other.integral
        div_zero = self.div_zero or other.div_zero
        if self.is_unknown or other.is_unknown:
            src = self if self.is_unknown else other
            return AbsVal.unknown(integral, src.reason or "range could not be bounded", div_zero)
        return AbsVal(min(self.lo, other.lo), max(self.hi, other.hi), integral,
                      None, div_zero)

    def format_range(self) -> str:
        if self.is_unknown:
            return "UNKNOWN"
        return f"[{format_number(self.lo)}, {format_number(self.hi)}]"

    def __str__(self) -> str:
        return f"{self.format_range()} integral={'yes' if self.integral else 'no'}"
