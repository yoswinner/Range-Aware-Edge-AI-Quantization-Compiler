"""Source-level diagnostics: one record per SSA value, in program order.

Report format follows the review (Section 4.11), e.g.::

    Line 3, Column 5
    Variable: y.1
    Inferred range: [15, 25]
    Integral: YES
    INT8 Safety: SAFE
    Reason: within INT8 bounds and integral on all paths
"""

from collections import Counter
from dataclasses import dataclass
from typing import List, Optional

from src.analysis.abstract_value import AbsVal
from src.analysis.range_analysis import RangeResult
from src.ast.types import Type
from src.diagnostics.location import SourceLocation
from src.ir.values import Temp, Value, Var
from src.quantization.quantizer import QuantizationResult
from src.quantization.safety import SAFE_REASON, SafetyDecision
from src.ssa.construction import SSAProgram


@dataclass(frozen=True)
class ValueDiagnostic:
    value: Value
    name: str
    source_variable: Optional[str]      # None for compiler temporaries
    loc: Optional[SourceLocation]
    original_type: Type
    abstract: AbsVal
    decision: SafetyDecision
    quantized: bool
    blocked_reason: Optional[str]

    @property
    def is_temporary(self) -> bool:
        return isinstance(self.value, Temp)


def build_diagnostics(ssa: SSAProgram, ranges: RangeResult,
                      quant: QuantizationResult) -> List[ValueDiagnostic]:
    result: List[ValueDiagnostic] = []
    for _, instr in ssa.instructions():
        for v in instr.defs():
            source = None
            if isinstance(v, Var):
                sym = ssa.symbols.get(v.name)
                source = sym.name if sym is not None else v.name
            result.append(ValueDiagnostic(
                value=v, name=str(v), source_variable=source, loc=instr.loc,
                original_type=_original_type(ssa, v),
                abstract=ranges.values[v], decision=quant.decisions[v],
                quantized=quant.is_quantized(v), blocked_reason=quant.blocked.get(v),
            ))
    return result


def _original_type(ssa: SSAProgram, v: Value) -> Type:
    # ``ssa`` here is the pre-rewrite program, so dest_type is still the source type.
    return ssa.defs[v][1].dest_type


def format_diagnostic(d: ValueDiagnostic) -> str:
    lines = []
    lines.append(f"Line {d.loc.line}, Column {d.loc.column}" if d.loc else "Line ?, Column ?")
    label = f"{d.name} (temporary)" if d.is_temporary else d.name
    lines.append(f"Variable: {label}")
    lines.append(f"Type: {d.original_type.display}")
    lines.append(f"Inferred range: {d.abstract.format_range()}")
    lines.append(f"Integral: {'YES' if d.abstract.integral else 'NO'}")
    if d.decision.safe:
        lines.append("INT8 Safety: SAFE")
        lines.append(f"Reason: {SAFE_REASON}")
    else:
        lines.append("INT8 Safety: REJECTED")
        for reason in d.decision.reasons:
            lines.append(f"Reason: {reason}")
    if d.quantized:
        lines.append(f"Transformation: {d.original_type.display} -> int8")
    elif d.decision.safe:
        lines.append(f"Transformation: none (kept {d.original_type.display}): {d.blocked_reason}")
    else:
        lines.append(f"Transformation: none (kept {d.original_type.display})")
    return "\n".join(lines)


def format_report(diags: List[ValueDiagnostic], include_temporaries: bool = True) -> str:
    blocks = [format_diagnostic(d) for d in diags if include_temporaries or not d.is_temporary]
    return "\n\n".join(blocks)


def summarize(diags: List[ValueDiagnostic]) -> str:
    """Counts over the diagnosed SSA values (all measured from the actual run)."""
    total = len(diags)
    safe = sum(1 for d in diags if d.decision.safe)
    rewritten = sum(1 for d in diags if d.quantized)
    reasons = Counter(k.value for d in diags for k in d.decision.kinds)
    lines = [
        f"SSA values analysed: {total}",
        f"  labelled SAFE:      {safe}",
        f"  rewritten to int8:  {rewritten}",
        f"  labelled REJECT:    {total - safe}",
    ]
    for reason, count in sorted(reasons.items()):
        lines.append(f"    rejection condition '{reason}': {count}")
    return "\n".join(lines)
