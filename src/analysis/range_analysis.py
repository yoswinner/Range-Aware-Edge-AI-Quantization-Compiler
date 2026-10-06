"""Range + integrality analysis over SSA, with bounded iteration and widening.

Algorithm (review Sections 4.6-4.8)
-----------------------------------
Kleene iteration from bottom. One *sweep* visits every block in reverse
postorder and every instruction in order, applying its transfer function to the
facts computed so far; a phi joins the facts of its already-known operands.
Sweeps repeat until a sweep changes nothing (fixed point reached).

Why this terminates / why widening is only needed at phis: every cycle of the
SSA def-use graph passes through a loop-header phi, so the phis are the only
places where information can circulate indefinitely. From sweep
``widen_after + 1`` onward, a phi whose result is still *changing* is widened
to **UNKNOWN** (the review's "extrapolate toward infinity, treated as UNKNOWN").
UNKNOWN cannot change any further except for its integrality flag, which can
only go True -> False, so after widening each phi changes at most twice more and
the iteration stops. A hard ``max_sweeps`` cap is a belt-and-braces guard: if it
is ever hit, *every* value is conservatively set to UNKNOWN/non-integral and
``converged`` is False.

Consequences: a loop-carried value whose range stabilises quickly keeps a
precise interval (e.g. ``x = 1 - x`` converges to [0, 1]); a counter such as
``i = i + 1`` grows every sweep, is widened and ends up UNKNOWN, so it is never
proposed for INT8. No branch-condition refinement is performed (``i < 100`` does
not narrow ``i`` inside the loop); that is a deliberate precision loss.

Bottom handling: an operand with no fact yet (only possible for a phi's
back-edge operand during the first sweeps) makes a non-phi instruction wait and
is skipped by a phi's join.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from functools import reduce
from typing import Dict, Optional, Set

from src.analysis.abstract_value import AbsVal
from src.analysis.transfer import apply_binop, neg
from src.ast.types import Type
from src.ir.tac import BinOp, Copy, Input, Phi, UnOp
from src.ir.values import Const, Value
from src.ssa.construction import SSAProgram

DEFAULT_WIDEN_AFTER = 3


@dataclass
class RangeResult:
    values: Dict[Value, AbsVal] = field(default_factory=dict)
    sweeps: int = 0
    converged: bool = True
    widened: Set[Value] = field(default_factory=set)
    widen_after: int = DEFAULT_WIDEN_AFTER

    def get(self, v: Value) -> AbsVal:
        """Fact for an SSA name or constant operand."""
        if isinstance(v, Const):
            return AbsVal.const(v.value)
        return self.values[v]


def analyze_ranges(ssa: SSAProgram, widen_after: int = DEFAULT_WIDEN_AFTER,
                   max_sweeps: Optional[int] = None) -> RangeResult:
    instrs = [ins for _, ins in _in_sweep_order(ssa)]
    if max_sweeps is None:
        max_sweeps = widen_after + 4 * len(instrs) + 10

    env: Dict[Value, AbsVal] = {}
    widened: Set[Value] = set()

    def get(v: Value) -> Optional[AbsVal]:
        if isinstance(v, Const):
            return AbsVal.const(v.value)
        return env.get(v)

    converged = False
    sweeps = 0
    while sweeps < max_sweeps:
        sweeps += 1
        changed = False
        for ins in instrs:
            if not ins.defs():
                continue
            new = _transfer(ins, get)
            if new is None:  # still bottom
                continue
            dest = ins.dest
            old = env.get(dest)
            if isinstance(ins, Phi) and old is not None and new != old and sweeps > widen_after:
                # Still moving after the allowed number of ordinary iterations:
                # widen to UNKNOWN instead of iterating forever.
                new = AbsVal.unknown(
                    new.integral,
                    f"loop widening: range did not stabilise within {widen_after} iterations",
                )
                widened.add(dest)
            if new != old:
                env[dest] = new
                changed = True
        if not changed:
            converged = True
            break

    if not converged:
        # Fixed point not reached: no fact is trustworthy -> everything UNKNOWN.
        env = {
            d: AbsVal.unknown(False, "analysis did not converge; conservative fallback")
            for d in ssa.defs
        }
    else:
        for d in ssa.defs:  # defensive: a def that never received a fact
            env.setdefault(d, AbsVal.unknown(False, "no information computed"))
    return RangeResult(env, sweeps, converged, widened, widen_after)


def _in_sweep_order(ssa: SSAProgram):
    for bid in ssa.cfg.reverse_postorder():
        for ins in ssa.cfg.blocks[bid].instrs:
            yield bid, ins


def _transfer(ins, get) -> Optional[AbsVal]:
    if isinstance(ins, Copy):
        return get(ins.src)
    if isinstance(ins, UnOp):
        a = get(ins.operand)
        return None if a is None else neg(a)
    if isinstance(ins, BinOp):
        a, b = get(ins.left), get(ins.right)
        if a is None or b is None:
            return None
        return apply_binop(ins.op, a, b)
    if isinstance(ins, Input):
        return AbsVal.unknown(
            integral=ins.dest_type == Type.INT,
            reason="externally supplied value (declared without initializer)",
        )
    if isinstance(ins, Phi):
        known = [a for a in (get(v) for v in ins.incoming.values()) if a is not None]
        if not known:
            return None
        return reduce(AbsVal.join, known)
    raise TypeError(f"no transfer function for {type(ins).__name__}")  # pragma: no cover
