"""Sound branch-condition interval refinement.

Implements edge-specific refinement across control-flow edges:
- Refines intervals on both 'true' and 'false' edges separately.
- Supports comparison operators: <, <=, >, >=, ==, !=.
- Handles variable-to-constant (with integer discrete step +-1 for strict inequalities).
- Handles variable-to-variable constraints.
- Detects impossible branches by producing unreachable state when intervals become empty.
"""

from fractions import Fraction
from typing import Dict, Optional

from src.analysis.abstract_value import AbsVal
from src.ast.types import Type
from src.ir.tac import BinOp, CondJump
from src.ir.values import Const, Value
from src.ssa.construction import SSAProgram

_NEGATED_OP = {
    "<": ">=",
    "<=": ">",
    ">": "<=",
    ">=": "<",
    "==": "!=",
    "!=": "==",
}

_FLIPPED_OP = {
    "<": ">",
    "<=": ">=",
    ">": "<",
    ">=": "<=",
    "==": "==",
    "!=": "!=",
}


def refine_condition(
    env: Dict[Value, AbsVal],
    op: str,
    left: Value,
    right: Value,
    is_true_edge: bool,
    ssa: Optional[SSAProgram] = None,
) -> Dict[Value, AbsVal]:
    """Refine variables in `env` according to `left op right` along true or false branch."""
    eff_op = op if is_true_edge else _NEGATED_OP.get(op, op)
    out: Dict[Value, AbsVal] = dict(env)

    # If any value is already unreachable, whole environment is unreachable
    if any(v.unreachable for v in out.values()):
        return {k: AbsVal.bot() for k in out}

    # Case 1: Variable and Constant
    if isinstance(left, Value) and not isinstance(left, Const) and isinstance(right, Const):
        _refine_var_const(out, left, eff_op, right, ssa)
    elif isinstance(left, Const) and isinstance(right, Value) and not isinstance(right, Const):
        flipped = _FLIPPED_OP.get(eff_op, eff_op)
        _refine_var_const(out, right, flipped, left, ssa)

    # Case 2: Variable and Variable
    elif (isinstance(left, Value) and not isinstance(left, Const) and
          isinstance(right, Value) and not isinstance(right, Const)):
        _refine_var_var(out, left, eff_op, right)

    # Case 3: Constant and Constant
    elif isinstance(left, Const) and isinstance(right, Const):
        lc = Fraction(left.value)
        rc = Fraction(right.value)
        cond_met = False
        if eff_op == "<": cond_met = (lc < rc)
        elif eff_op == "<=": cond_met = (lc <= rc)
        elif eff_op == ">": cond_met = (lc > rc)
        elif eff_op == ">=": cond_met = (lc >= rc)
        elif eff_op == "==": cond_met = (lc == rc)
        elif eff_op == "!=": cond_met = (lc != rc)

        if not cond_met:
            return {k: AbsVal.bot() for k in out}

    return out


def _refine_var_const(
    env: Dict[Value, AbsVal],
    var: Value,
    op: str,
    const_val: Const,
    ssa: Optional[SSAProgram] = None,
) -> None:
    c = Fraction(const_val.value)
    cur = env.get(var, AbsVal.unknown(integral=True))
    is_int = cur.integral
    if ssa is not None and var in ssa.defs:
        dest_ty = ssa.defs[var][1].dest_type
        if dest_ty in (Type.INT, Type.INT8):
            is_int = True

    is_integral_domain = is_int and (c.denominator == 1)

    if op == "<":
        hi_bound = (c - 1) if is_integral_domain else c
        constraint = AbsVal(None, hi_bound, is_int)
        env[var] = cur.meet(constraint)
    elif op == "<=":
        constraint = AbsVal(None, c, is_int)
        env[var] = cur.meet(constraint)
    elif op == ">":
        lo_bound = (c + 1) if is_integral_domain else c
        constraint = AbsVal(lo_bound, None, is_int)
        env[var] = cur.meet(constraint)
    elif op == ">=":
        constraint = AbsVal(c, None, is_int)
        env[var] = cur.meet(constraint)
    elif op == "==":
        constraint = AbsVal(c, c, is_int)
        env[var] = cur.meet(constraint)
    elif op == "!=":
        if cur.lo == c and cur.lo is not None:
            lo_bound = (c + 1) if is_integral_domain else c
            constraint = AbsVal(lo_bound, cur.hi, is_int)
            env[var] = cur.meet(constraint)
        elif cur.hi == c and cur.hi is not None:
            hi_bound = (c - 1) if is_integral_domain else c
            constraint = AbsVal(cur.lo, hi_bound, is_int)
            env[var] = cur.meet(constraint)


def _refine_var_var(env: Dict[Value, AbsVal], left: Value, op: str, right: Value) -> None:
    l_val = env.get(left, AbsVal.unknown(integral=True))
    r_val = env.get(right, AbsVal.unknown(integral=True))
    is_int = l_val.integral and r_val.integral

    if op == "<":
        if r_val.hi is not None:
            hi_bound = (r_val.hi - 1) if is_int else r_val.hi
            env[left] = l_val.meet(AbsVal(None, hi_bound, is_int))
        if l_val.lo is not None:
            lo_bound = (l_val.lo + 1) if is_int else l_val.lo
            env[right] = r_val.meet(AbsVal(lo_bound, None, is_int))
    elif op == "<=":
        if r_val.hi is not None:
            env[left] = l_val.meet(AbsVal(None, r_val.hi, is_int))
        if l_val.lo is not None:
            env[right] = r_val.meet(AbsVal(l_val.lo, None, is_int))
    elif op == ">":
        if l_val.hi is not None:
            hi_bound = (l_val.hi - 1) if is_int else l_val.hi
            env[right] = r_val.meet(AbsVal(None, hi_bound, is_int))
        if r_val.lo is not None:
            lo_bound = (r_val.lo + 1) if is_int else r_val.lo
            env[left] = l_val.meet(AbsVal(lo_bound, None, is_int))
    elif op == ">=":
        if l_val.hi is not None:
            env[right] = r_val.meet(AbsVal(None, l_val.hi, is_int))
        if r_val.lo is not None:
            env[left] = l_val.meet(AbsVal(r_val.lo, None, is_int))
    elif op == "==":
        both = l_val.meet(r_val)
        env[left] = both
        env[right] = both


def refine_edge(
    src_id: int,
    dst_id: int,
    env: Dict[Value, AbsVal],
    ssa: SSAProgram,
) -> Dict[Value, AbsVal]:
    """Refine `env` along control-flow edge `src_id -> dst_id`."""
    if not env:
        return {}
    if any(v.unreachable for v in env.values()):
        return {k: AbsVal.bot() for k in env}

    blk = ssa.cfg.blocks.get(src_id)
    if not blk or not blk.instrs:
        return dict(env)

    last_ins = blk.instrs[-1]
    if not isinstance(last_ins, CondJump):
        return dict(env)

    try:
        kind = ssa.cfg.edge_kind(src_id, dst_id)
    except KeyError:
        return dict(env)

    if kind not in ("true", "false"):
        return dict(env)

    cond = last_ins.cond
    is_true = (kind == "true")

    if cond in ssa.defs:
        _, def_ins = ssa.defs[cond]
        if isinstance(def_ins, BinOp) and def_ins.op in ("<", "<=", ">", ">=", "==", "!="):
            return refine_condition(env, def_ins.op, def_ins.left, def_ins.right, is_true, ssa)

    return dict(env)
