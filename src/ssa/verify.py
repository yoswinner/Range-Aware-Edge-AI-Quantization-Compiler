"""Structural SSA verifier (used by the test-suite and available to callers)."""

from typing import List

from src.cfg.dominators import dominates
from src.ir.tac import Phi
from src.ir.values import Const, Temp, Var
from src.ssa.construction import SSAProgram


def verify_ssa(ssa: SSAProgram) -> List[str]:
    """Return a list of violated SSA invariants (empty list = well-formed).

    Checked: (1) each name is defined exactly once; (2) no unversioned source
    variable remains; (3) every use refers to a defined name; (4) a definition
    dominates each of its uses (for a phi operand: dominates the end of the
    corresponding predecessor); (5) each phi has exactly one operand per CFG
    predecessor.
    """
    problems: List[str] = []
    cfg, idom = ssa.cfg, ssa.dom.idom

    seen = {}
    position = {}
    for bid in sorted(cfg.blocks):
        for idx, ins in enumerate(cfg.blocks[bid].instrs):
            for d in ins.defs():
                if d in seen:
                    problems.append(f"{d} defined more than once")
                seen[d] = bid
                position[d] = (bid, idx)
                if isinstance(d, Var) and d.version is None:
                    problems.append(f"unversioned definition {d}")

    for bid in sorted(cfg.blocks):
        for idx, ins in enumerate(cfg.blocks[bid].instrs):
            if isinstance(ins, Phi):
                if set(ins.incoming) != set(cfg.preds(bid)):
                    problems.append(
                        f"phi {ins.dest} in B{bid} has operands for {sorted(ins.incoming)} "
                        f"but predecessors are {sorted(cfg.preds(bid))}"
                    )
                for pred, v in ins.incoming.items():
                    if isinstance(v, (Temp, Var)):
                        if v not in position:
                            problems.append(f"phi operand {v} is undefined")
                        elif not dominates(idom, position[v][0], pred):
                            problems.append(f"phi operand {v} does not dominate end of B{pred}")
                continue
            for v in ins.uses():
                if isinstance(v, Const):
                    continue
                if isinstance(v, Var) and v.version is None:
                    problems.append(f"unversioned use {v} in B{bid}")
                    continue
                if v not in position:
                    problems.append(f"use of undefined {v} in B{bid}")
                    continue
                dbid, didx = position[v]
                if dbid == bid:
                    if didx >= idx:
                        problems.append(f"{v} used before its definition in B{bid}")
                elif not dominates(idom, dbid, bid):
                    problems.append(f"definition of {v} (B{dbid}) does not dominate use in B{bid}")
    return problems
