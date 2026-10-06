"""The INT8 safety predicate (review Section 4.9).

A value is SAFE for INT8 only if *all* hold:

1. its range is known (not UNKNOWN);
2. ``min >= -128``;
3. ``max <= 127``;
4. it is guaranteed integral;
5. it was produced by an operation the quantization pass supports;
6. no other violation was flagged (a possible division by zero).

The predicate consumes the analysis result (``AbsVal``) and a description of the
producing operation; it contains no special cases for particular inputs. It
returns *all* failed conditions so diagnostics can explain a rejection fully;
``primary_reason`` is the first one (UNKNOWN range > division by zero >
unsupported operation > overflow > non-integral).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from src.analysis.abstract_value import AbsVal
from src.ir.tac import BinOp, Copy, Input, Instr, Phi, UnOp
from src.ir.values import format_number

INT8_MIN = -128
INT8_MAX = 127

SAFE_REASON = "within INT8 bounds and integral on all paths"


class Verdict(Enum):
    SAFE = "SAFE"
    REJECT = "REJECT"


class RejectKind(Enum):
    UNKNOWN_RANGE = "unknown range"
    DIV_BY_ZERO = "possible division by zero"
    UNSUPPORTED_OP = "unsupported operation"
    OVERFLOW = "possible overflow"
    NON_INTEGRAL = "non-integral"


@dataclass(frozen=True)
class SafetyDecision:
    verdict: Verdict
    kinds: Tuple[RejectKind, ...]
    reasons: Tuple[str, ...]

    @property
    def safe(self) -> bool:
        return self.verdict is Verdict.SAFE

    @property
    def primary_kind(self) -> Optional[RejectKind]:
        return self.kinds[0] if self.kinds else None

    @property
    def primary_reason(self) -> str:
        return self.reasons[0] if self.reasons else SAFE_REASON


def check_int8_safety(value: AbsVal, op_supported: bool = True,
                      op_description: str = "operation") -> SafetyDecision:
    kinds = []
    reasons = []

    if value.is_unknown:
        kinds.append(RejectKind.UNKNOWN_RANGE)
        reasons.append(f"range unknown, safety cannot be proven ({value.reason})")
    if value.div_zero:
        kinds.append(RejectKind.DIV_BY_ZERO)
        reasons.append("possible division by zero was flagged")
    if not op_supported:
        kinds.append(RejectKind.UNSUPPORTED_OP)
        reasons.append(f"operation not supported by the quantization pass: {op_description}")
    if not value.is_unknown:
        if value.hi > INT8_MAX or value.lo < INT8_MIN:
            kinds.append(RejectKind.OVERFLOW)
            parts = []
            if value.hi > INT8_MAX:
                parts.append(f"{format_number(value.hi)} > {INT8_MAX}")
            if value.lo < INT8_MIN:
                parts.append(f"{format_number(value.lo)} < {INT8_MIN}")
            reasons.append("possible overflow: " + ", ".join(parts))
    if not value.integral:
        kinds.append(RejectKind.NON_INTEGRAL)
        reasons.append("not guaranteed integral (non-integral)")

    if kinds:
        return SafetyDecision(Verdict.REJECT, tuple(kinds), tuple(reasons))
    return SafetyDecision(Verdict.SAFE, (), ())


def describe_operation(instr: Instr) -> Tuple[bool, str]:
    """``(supported, description)`` for the instruction that defines a value.

    Supported: constant/variable copies, phi merges, ``+``, ``-``, ``*`` and
    unary negation. Not supported: division (never integral), relational
    comparisons (boolean-valued) and externally supplied inputs.
    """
    if isinstance(instr, (Copy, Phi)):
        return True, "copy" if isinstance(instr, Copy) else "phi"
    if isinstance(instr, UnOp):
        return True, "negation"
    if isinstance(instr, BinOp):
        if instr.op in ("+", "-", "*"):
            return True, instr.op
        if instr.op == "/":
            return False, "division '/'"
        return False, f"relational comparison '{instr.op}'"
    if isinstance(instr, Input):
        return False, "externally supplied input"
    return False, type(instr).__name__.lower()
