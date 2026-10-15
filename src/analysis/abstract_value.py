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
    unreachable: bool = False
    reason: Optional[str] = field(default=None, compare=False)
    div_zero: bool = field(default=False, compare=False)

    def __post_init__(self):
        if self.unreachable:
            if self.lo is not None or self.hi is not None:
                object.__setattr__(self, "lo", None)
                object.__setattr__(self, "hi", None)
            return
        if self.lo is not None and self.hi is not None and self.lo > self.hi:
            object.__setattr__(self, "unreachable", True)
            object.__setattr__(self, "lo", None)
            object.__setattr__(self, "hi", None)

    # -- constructors ------------------------------------------------------
    @staticmethod
    def const(value) -> "AbsVal":
        value = Fraction(value)
        return AbsVal(value, value, value.denominator == 1)

    @staticmethod
    def interval(lo, hi, integral: bool) -> "AbsVal":
        l = Fraction(lo) if lo is not None else None
        h = Fraction(hi) if hi is not None else None
        if l is not None and h is not None and l > h:
            return AbsVal(None, None, True, True)
        return AbsVal(l, h, integral)

    @staticmethod
    def bot() -> "AbsVal":
        return AbsVal(None, None, True, True)

    @staticmethod
    def make_unreachable() -> "AbsVal":
        return AbsVal(None, None, True, True)

    @staticmethod
    def unknown(integral: bool = False, reason: str = "range could not be bounded",
                div_zero: bool = False) -> "AbsVal":
        return AbsVal(None, None, integral, False, reason, div_zero)

    # -- queries -----------------------------------------------------------
    @property
    def is_unreachable(self) -> bool:
        return self.unreachable

    @property
    def is_bounded(self) -> bool:
        return not self.unreachable and self.lo is not None and self.hi is not None

    @property
    def is_unknown(self) -> bool:
        return not self.unreachable and (self.lo is None or self.hi is None)

    def join(self, other: "AbsVal") -> "AbsVal":
        """Least upper bound: cover both intervals, AND the integrality flags.
        Used at phi nodes. Unreachable is identity; UNKNOWN absorbs everything."""
        if self.unreachable:
            return other
        if other.unreachable:
            return self
        integral = self.integral and other.integral
        div_zero = self.div_zero or other.div_zero
        if self.is_unknown or other.is_unknown:
            new_lo = None if (self.lo is None or other.lo is None) else min(self.lo, other.lo)
            new_hi = None if (self.hi is None or other.hi is None) else max(self.hi, other.hi)
            src = self if self.is_unknown else other
            return AbsVal(new_lo, new_hi, integral, False, src.reason or "range could not be bounded", div_zero)
        return AbsVal(min(self.lo, other.lo), max(self.hi, other.hi), integral,
                      False, None, div_zero)

    def meet(self, other: "AbsVal") -> "AbsVal":
        """Greatest lower bound (interval intersection).
        If either is unreachable or intersection is empty, returns unreachable."""
        if self.unreachable or other.unreachable:
            return AbsVal.bot()

        new_lo = self.lo if other.lo is None else (other.lo if self.lo is None else max(self.lo, other.lo))
        new_hi = self.hi if other.hi is None else (other.hi if self.hi is None else min(self.hi, other.hi))

        if new_lo is not None and new_hi is not None and new_lo > new_hi:
            return AbsVal.bot()

        integral = self.integral or other.integral
        div_zero = self.div_zero or other.div_zero
        reason = self.reason if other.is_unknown else other.reason
        return AbsVal(new_lo, new_hi, integral, False, reason, div_zero)

    def format_range(self) -> str:
        if self.unreachable:
            return "UNREACHABLE"
        if self.lo is None and self.hi is None:
            return "UNKNOWN"
        if self.lo is None:
            return f"[-inf, {format_number(self.hi)}]"
        if self.hi is None:
            return f"[{format_number(self.lo)}, +inf]"
        return f"[{format_number(self.lo)}, {format_number(self.hi)}]"

    def __str__(self) -> str:
        if self.unreachable:
            return "UNREACHABLE"
        return f"{self.format_range()} integral={'yes' if self.integral else 'no'}"
