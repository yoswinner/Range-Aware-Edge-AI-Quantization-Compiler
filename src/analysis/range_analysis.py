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
from src.analysis.refinement import refine_edge
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
    narrowed: Set[Value] = field(default_factory=set)
    block_in: Dict[int, Dict[Value, AbsVal]] = field(default_factory=dict)
    block_out: Dict[int, Dict[Value, AbsVal]] = field(default_factory=dict)

    def get(self, v: Value) -> AbsVal:
        """Fact for an SSA name or constant operand."""
        if isinstance(v, Const):
            return AbsVal.const(v.value)
        return self.values[v]


def analyze_ranges(
    ssa: SSAProgram,
    widen_after: int = DEFAULT_WIDEN_AFTER,
    max_sweeps: Optional[int] = None,
    narrow: bool = False,
    prune_unreachable: bool = False,
) -> RangeResult:
    rpo = ssa.cfg.reverse_postorder()
    total_instrs = sum(len(ssa.cfg.blocks[b].instrs) for b in ssa.cfg.blocks)
    if max_sweeps is None:
        max_sweeps = widen_after + 4 * total_instrs + 20

    env: Dict[Value, AbsVal] = {}
    widened: Set[Value] = set()
    narrowed: Set[Value] = set()
    block_in: Dict[int, Dict[Value, AbsVal]] = {b: {} for b in ssa.cfg.blocks}
    block_out: Dict[int, Dict[Value, AbsVal]] = {b: {} for b in ssa.cfg.blocks}

    converged = False
    sweeps = 0

    while sweeps < max_sweeps:
        sweeps += 1
        changed = False

        for bid in rpo:
            blk = ssa.cfg.blocks[bid]

            # 1. Compute block_in[bid] from incoming predecessor edges
            if bid == ssa.cfg.entry:
                block_in[bid] = {}
            else:
                preds = ssa.cfg.preds(bid)
                incoming_envs = []
                for p in preds:
                    p_env = block_out.get(p, {})
                    e_env = refine_edge(p, bid, p_env, ssa)
                    if prune_unreachable and any(v.unreachable for v in e_env.values()):
                        continue
                    incoming_envs.append(e_env)

                new_in: Dict[Value, AbsVal] = {}
                all_vars = set()
                for e in incoming_envs:
                    all_vars.update(e.keys())
                for v in all_vars:
                    facts = [e[v] for e in incoming_envs if v in e]
                    if facts:
                        new_in[v] = reduce(AbsVal.join, facts)
                block_in[bid] = new_in

            # 2. Iterate instructions within the block
            curr = dict(block_in[bid])

            def get_operand_fact(v: Value) -> Optional[AbsVal]:
                if isinstance(v, Const):
                    if v.ty == Type.FLOAT:
                        return AbsVal(Fraction(v.value), Fraction(v.value), False)
                    return AbsVal.const(v.value)
                if v in curr:
                    return curr[v]
                return env.get(v)

            for ins in blk.instrs:
                if not ins.defs():
                    continue

                dest = ins.dest
                if isinstance(ins, Phi):
                    known = []
                    for pred_b, val in ins.incoming.items():
                        if prune_unreachable:
                            e_env = refine_edge(pred_b, bid, block_out.get(pred_b, {}), ssa)
                            if any(v.unreachable for v in e_env.values()):
                                continue
                        if isinstance(val, Const):
                            if val.ty == Type.FLOAT:
                                known.append(AbsVal(Fraction(val.value), Fraction(val.value), False))
                            else:
                                known.append(AbsVal.const(val.value))
                        else:
                            pred_val = None
                            if pred_b in block_out and val in block_out[pred_b]:
                                pred_val = block_out[pred_b][val]
                            elif val in env:
                                pred_val = env[val]
                            if pred_val is not None:
                                known.append(pred_val)

                    if not known:
                        continue
                    new = reduce(AbsVal.join, known)
                    if hasattr(ins, "dest_type") and ins.dest_type == Type.FLOAT:
                        new = AbsVal(new.lo, new.hi, False, new.unreachable, new.reason, new.div_zero)
                    old = env.get(dest)

                    if old is not None and new != old and sweeps > widen_after:
                        if narrow:
                            new_lo = None if (old.lo is not None and new.lo is not None and new.lo < old.lo) else new.lo
                            new_hi = None if (old.hi is not None and new.hi is not None and new.hi > old.hi) else new.hi
                            new = AbsVal(new_lo, new_hi, new.integral, False, None, new.div_zero or old.div_zero)
                            widened.add(dest)
                        else:
                            new = AbsVal.unknown(
                                new.integral,
                                f"loop widening: range did not stabilise within {widen_after} iterations",
                            )
                            widened.add(dest)
                else:
                    new = _transfer(ins, get_operand_fact)
                    if new is None:
                        continue

                old = env.get(dest)
                curr[dest] = new
                if new != old:
                    env[dest] = new
                    changed = True

            block_out[bid] = curr

        if not changed:
            converged = True
            break

    # 3. Narrowing phase if enabled
    if narrow and converged and widened:
        for _ in range(5):
            narrow_changed = False
            for bid in rpo:
                blk = ssa.cfg.blocks[bid]
                curr = dict(block_in[bid])

                def get_narrow_fact(v: Value) -> Optional[AbsVal]:
                    if isinstance(v, Const):
                        if v.ty == Type.FLOAT:
                            return AbsVal(Fraction(v.value), Fraction(v.value), False)
                        return AbsVal.const(v.value)
                    if v in curr:
                        return curr[v]
                    return env.get(v)

                for ins in blk.instrs:
                    if not ins.defs():
                        continue
                    dest = ins.dest
                    if isinstance(ins, Phi) and dest in widened:
                        known = []
                        for pred_b, val in ins.incoming.items():
                            if isinstance(val, Const):
                                if val.ty == Type.FLOAT:
                                    known.append(AbsVal(Fraction(val.value), Fraction(val.value), False))
                                else:
                                    known.append(AbsVal.const(val.value))
                            else:
                                if pred_b in block_out and val in block_out[pred_b]:
                                    known.append(block_out[pred_b][val])
                                elif val in env:
                                    known.append(env[val])
                        if known:
                            candidate = reduce(AbsVal.join, known)
                            if hasattr(ins, "dest_type") and ins.dest_type == Type.FLOAT:
                                candidate = AbsVal(candidate.lo, candidate.hi, False, candidate.unreachable, candidate.reason, candidate.div_zero)
                            old = env.get(dest)
                            if old is not None:
                                narrowed_val = old.meet(candidate)
                                if narrowed_val != old:
                                    env[dest] = narrowed_val
                                    curr[dest] = narrowed_val
                                    narrowed.add(dest)
                                    narrow_changed = True
                    else:
                        new = _transfer(ins, get_narrow_fact)
                        if new is not None and new != env.get(dest):
                            env[dest] = new
                            curr[dest] = new
                            narrow_changed = True
                block_out[bid] = curr
            if not narrow_changed:
                break

    if not converged:
        env = {
            d: AbsVal.unknown(False, "analysis did not converge; conservative fallback")
            for d in ssa.defs
        }
    else:
        for d in ssa.defs:
            env.setdefault(d, AbsVal.unknown(False, "no information computed"))

    return RangeResult(env, sweeps, converged, widened, widen_after, narrowed, block_in, block_out)


def _transfer(ins, get) -> Optional[AbsVal]:
    dest_ty = getattr(ins, "dest_type", None)
    res: Optional[AbsVal] = None

    if isinstance(ins, Copy):
        res = get(ins.src)
    elif isinstance(ins, UnOp):
        a = get(ins.operand)
        res = None if a is None else neg(a)
    elif isinstance(ins, BinOp):
        a, b = get(ins.left), get(ins.right)
        if a is None or b is None:
            return None
        res = apply_binop(ins.op, a, b)
    elif isinstance(ins, Input):
        res = AbsVal.unknown(
            integral=ins.dest_type == Type.INT,
            reason="externally supplied value (declared without initializer)",
        )
    elif isinstance(ins, Phi):
        known = [a for a in (get(v) for v in ins.incoming.values()) if a is not None]
        if not known:
            return None
        res = reduce(AbsVal.join, known)
    else:
        raise TypeError(f"no transfer function for {type(ins).__name__}")

    if res is not None and dest_ty == Type.FLOAT:
        return AbsVal(res.lo, res.hi, False, res.unreachable, res.reason, res.div_zero)
    return res
