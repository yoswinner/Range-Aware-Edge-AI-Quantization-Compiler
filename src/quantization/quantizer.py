"""Quantization: decide (analysis labels) and then transform (retype).

The two steps are kept separate, as in the review (Section 4.10):

* :func:`decide_safety` labels every SSA value SAFE/REJECT from the analysis.
* :func:`quantize` rewrites only values that are SAFE *and* whose operands are
  also INT8-representable. An INT8 operation cannot silently consume an FP32
  operand, so a value that is labelled SAFE but has a rejected operand (or a
  constant operand that does not fit INT8) is **left unchanged** and recorded
  in ``blocked`` with the reason. The set of rewritten values is the greatest
  fixed point of "SAFE and all operands rewritten" (computed by iteration, so
  it is also correct through phi cycles).

The rewrite is a retyping: ``dest_type`` becomes ``INT8`` and constant
operands become ``INT8`` constants. The original SSA program is not modified.

Status: the transformation only retypes IR. It is *not* validated by executing
the quantized IR (the simulator/backend stage is not implemented yet).
"""

import copy
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, Set

from src.analysis.range_analysis import RangeResult
from src.ast.types import Type
from src.ir.tac import Phi
from src.ir.values import Const, Value
from src.quantization.safety import (
    INT8_MAX, INT8_MIN, SafetyDecision, check_int8_safety, describe_operation,
)
from src.ssa.construction import SSAProgram


@dataclass
class QuantizationResult:
    decisions: Dict[Value, SafetyDecision]       # every SSA value -> SAFE/REJECT
    quantized: Set[Value]                        # values actually retyped to INT8
    blocked: Dict[Value, str] = field(default_factory=dict)  # SAFE but not rewritten -> why
    program: SSAProgram = None                   # rewritten copy of the SSA program

    def is_quantized(self, v: Value) -> bool:
        return v in self.quantized


def decide_safety(ssa: SSAProgram, ranges: RangeResult) -> Dict[Value, SafetyDecision]:
    decisions: Dict[Value, SafetyDecision] = {}
    for name, (_, instr) in ssa.defs.items():
        supported, description = describe_operation(instr)
        decisions[name] = check_int8_safety(ranges.values[name], supported, description)
    return decisions


def _const_fits_int8(c: Const) -> bool:
    v = Fraction(c.value)
    return v.denominator == 1 and INT8_MIN <= v <= INT8_MAX


def quantize(ssa: SSAProgram, ranges: RangeResult) -> QuantizationResult:
    decisions = decide_safety(ssa, ranges)
    candidates = {v for v, d in decisions.items() if d.safe}
    blocked: Dict[Value, str] = {}

    changed = True
    while changed:
        changed = False
        for v in sorted(candidates, key=str):
            _, instr = ssa.defs[v]
            reason = None
            for operand in instr.uses():
                if isinstance(operand, Const):
                    if not _const_fits_int8(operand):
                        reason = f"constant operand {operand} is not an INT8 value"
                        break
                elif operand not in candidates:
                    reason = f"operand {operand} is not INT8-safe, so it stays in its original type"
                    break
            if reason is not None:
                candidates.discard(v)
                blocked[v] = reason
                changed = True
                break  # restart: removing v may invalidate other candidates

    out = copy.deepcopy(ssa)
    for name in candidates:
        _, instr = out.defs[name]
        instr.dest_type = Type.INT8
        if not isinstance(instr, Phi):
            instr.replace_uses(
                lambda o: Const(o.value, Type.INT8) if isinstance(o, Const) else o
            )
    return QuantizationResult(decisions, set(candidates), blocked, out)
