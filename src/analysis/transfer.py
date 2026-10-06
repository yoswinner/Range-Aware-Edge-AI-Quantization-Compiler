"""Interval transfer functions (review Section 4.6).

Every function is *sound*: for any concrete operands lying inside the abstract
operands, the concrete result lies inside the abstract result, and integrality
is claimed only when it is guaranteed. When no finite bound can be justified the
result is UNKNOWN; precision is never invented.

Rules
-----
* ``[a,b] + [c,d] = [a+c, b+d]``
* ``[a,b] - [c,d] = [a-d, b-c]``
* ``[a,b] * [c,d] = [min(ac,ad,bc,bd), max(ac,ad,bc,bd)]``
* ``/``  : if the divisor interval contains 0 (or is unknown) -> UNKNOWN and the
  possible division by zero is flagged; otherwise the min/max of the four
  endpoint quotients. Division is never integral.
* ``neg``: ``-[a,b] = [-b,-a]``.
* integrality of ``+ - *`` and ``neg``: AND of the operands' flags (a sum,
  difference or product of integers is an integer). Anything else is
  conservatively non-integral.
* relational operators produce 0 or 1: ``[0,1]`` unless the operand intervals
  decide the comparison; the result is always integral and never UNKNOWN.
"""

from fractions import Fraction
from typing import Callable, Dict

from src.analysis.abstract_value import AbsVal


def _unknown_from(a: AbsVal, b: AbsVal, integral: bool) -> AbsVal:
    """UNKNOWN result when an operand is UNKNOWN; keeps the first reason/flag."""
    src = a if a.is_unknown else b
    return AbsVal.unknown(
        integral, src.reason or "operand range unknown", a.div_zero or b.div_zero
    )


def add(a: AbsVal, b: AbsVal) -> AbsVal:
    integral = a.integral and b.integral
    if a.is_unknown or b.is_unknown:
        return _unknown_from(a, b, integral)
    return AbsVal(a.lo + b.lo, a.hi + b.hi, integral)


def sub(a: AbsVal, b: AbsVal) -> AbsVal:
    integral = a.integral and b.integral
    if a.is_unknown or b.is_unknown:
        return _unknown_from(a, b, integral)
    return AbsVal(a.lo - b.hi, a.hi - b.lo, integral)


def mul(a: AbsVal, b: AbsVal) -> AbsVal:
    integral = a.integral and b.integral
    if a.is_unknown or b.is_unknown:
        return _unknown_from(a, b, integral)
    products = [a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi]
    return AbsVal(min(products), max(products), integral)


def div(a: AbsVal, b: AbsVal) -> AbsVal:
    if b.is_unknown:
        return AbsVal.unknown(
            False, "divisor range unknown; division by zero cannot be excluded", True
        )
    if b.lo <= 0 <= b.hi:
        return AbsVal.unknown(
            False,
            f"possible division by zero (divisor range {b.format_range()} contains 0)",
            True,
        )
    if a.is_unknown:
        return AbsVal.unknown(False, a.reason or "dividend range unknown", a.div_zero)
    quotients = [a.lo / b.lo, a.lo / b.hi, a.hi / b.lo, a.hi / b.hi]
    return AbsVal(min(quotients), max(quotients), False)


def neg(a: AbsVal) -> AbsVal:
    if a.is_unknown:
        return AbsVal.unknown(a.integral, a.reason or "operand range unknown", a.div_zero)
    return AbsVal(-a.hi, -a.lo, a.integral)


_BOOL_TRUE = AbsVal(Fraction(1), Fraction(1), True)
_BOOL_FALSE = AbsVal(Fraction(0), Fraction(0), True)
_BOOL_ANY = AbsVal(Fraction(0), Fraction(1), True)


def compare(op: str, a: AbsVal, b: AbsVal) -> AbsVal:
    if a.is_unknown or b.is_unknown:
        return _BOOL_ANY
    if op == "<":
        always, never = a.hi < b.lo, a.lo >= b.hi
    elif op == "<=":
        always, never = a.hi <= b.lo, a.lo > b.hi
    elif op == ">":
        always, never = a.lo > b.hi, a.hi <= b.lo
    elif op == ">=":
        always, never = a.lo >= b.hi, a.hi < b.lo
    elif op == "==":
        always = a.lo == a.hi == b.lo == b.hi
        never = a.hi < b.lo or b.hi < a.lo
    elif op == "!=":
        always = a.hi < b.lo or b.hi < a.lo
        never = a.lo == a.hi == b.lo == b.hi
    else:
        raise ValueError(f"unknown relational operator {op!r}")
    if always:
        return _BOOL_TRUE
    if never:
        return _BOOL_FALSE
    return _BOOL_ANY


_ARITH: Dict[str, Callable[[AbsVal, AbsVal], AbsVal]] = {
    "+": add, "-": sub, "*": mul, "/": div,
}
_RELATIONAL = {"<", ">", "<=", ">=", "==", "!="}


def apply_binop(op: str, a: AbsVal, b: AbsVal) -> AbsVal:
    if op in _ARITH:
        return _ARITH[op](a, b)
    if op in _RELATIONAL:
        return compare(op, a, b)
    raise ValueError(f"unsupported operator {op!r}")
