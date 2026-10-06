"""SSA construction.

Steps (review Section 4.5)
--------------------------
1. Compute dominators and dominance frontiers (``src.cfg.dominators``).
2. For every source variable ``v`` collect the blocks that define it and insert
   a phi for ``v`` at every block of the *iterated* dominance frontier of those
   blocks.
3. Rename: walk the dominator tree keeping, per variable, a stack of the
   current version; every definition pushes a fresh version, every use reads
   the top of the stack, and each successor's phis receive the current version
   as the operand for this predecessor.

Design decisions
----------------
* **Pruned SSA.** A phi is inserted only where the variable is live-in. Block
  scoping means a variable declared inside an ``if`` body has a definition on
  only one path; a minimal-SSA phi at the join would need an operand for the
  path where the variable does not exist. Liveness removes exactly those phis.
* Temporaries are assigned once by TAC generation, so only source variables are
  renamed. Versions start at 1 and are printed as ``x.1``, ``x.2``, ...
* The CFG passed in is deep-copied; the pre-SSA CFG stays untouched.
* The rename walk is iterative (explicit stack), so long programs do not hit
  Python's recursion limit.
"""

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from src.cfg.cfg import CFG
from src.cfg.dominators import DominatorInfo, analyze_dominance
from src.diagnostics.errors import SSAError
from src.ir.tac import Instr, Label, Phi
from src.ir.values import Value, Var


@dataclass
class SSAProgram:
    cfg: CFG
    dom: DominatorInfo
    defs: Dict[Value, Tuple[int, Instr]] = field(default_factory=dict)  # name -> (block id, instr)

    @property
    def symbols(self) -> dict:
        return self.cfg.symbols

    def instructions(self):
        """Yield ``(block_id, instr)`` in block-id order."""
        for bid in sorted(self.cfg.blocks):
            for ins in self.cfg.blocks[bid].instrs:
                yield bid, ins

    def phis(self) -> List[Phi]:
        return [i for _, i in self.instructions() if isinstance(i, Phi)]

    def format(self, annotate: bool = False) -> str:
        return self.cfg.format(annotate=annotate)


def _variables_live_in(cfg: CFG) -> Dict[int, Set[str]]:
    """Classic backward liveness over source variables (pre-SSA, so no phis)."""
    upward_use: Dict[int, Set[str]] = {}
    killed: Dict[int, Set[str]] = {}
    for bid, blk in cfg.blocks.items():
        used: Set[str] = set()
        defined: Set[str] = set()
        for ins in blk.instrs:
            for v in ins.uses():
                if isinstance(v, Var) and v.name not in defined:
                    used.add(v.name)
            for d in ins.defs():
                if isinstance(d, Var):
                    defined.add(d.name)
        upward_use[bid], killed[bid] = used, defined

    live_in = {bid: set(upward_use[bid]) for bid in cfg.blocks}
    order = list(reversed(cfg.reverse_postorder()))
    changed = True
    while changed:
        changed = False
        for bid in order:
            live_out: Set[str] = set()
            for s in cfg.succs(bid):
                live_out |= live_in[s]
            new = upward_use[bid] | (live_out - killed[bid])
            if new != live_in[bid]:
                live_in[bid] = new
                changed = True
    return live_in


def _insert_phis(cfg: CFG, dom: DominatorInfo) -> None:
    def_blocks: Dict[str, Set[int]] = {}
    for bid, blk in cfg.blocks.items():
        for ins in blk.instrs:
            for d in ins.defs():
                if isinstance(d, Var):
                    def_blocks.setdefault(d.name, set()).add(bid)

    live_in = _variables_live_in(cfg)
    phi_count = {bid: 0 for bid in cfg.blocks}

    for name in sorted(def_blocks):
        symbol = cfg.symbols.get(name)
        ty = symbol.ty if symbol is not None else None
        loc = symbol.decl_loc if symbol is not None else None
        has_phi: Set[int] = set()
        worklist = list(def_blocks[name])
        queued = set(worklist)
        while worklist:
            x = worklist.pop()
            for y in sorted(dom.frontiers[x]):
                if y in has_phi or name not in live_in[y]:
                    continue
                blk = cfg.blocks[y]
                pos = (1 if blk.instrs and isinstance(blk.instrs[0], Label) else 0) + phi_count[y]
                phi = Phi(dest=Var(name), var=name, incoming={}, dest_type=ty, loc=loc)
                blk.instrs.insert(pos, phi)
                phi_count[y] += 1
                has_phi.add(y)
                if y not in queued:  # the phi is itself a definition of ``name``
                    queued.add(y)
                    worklist.append(y)


def _rename(cfg: CFG, dom: DominatorInfo) -> None:
    stacks: Dict[str, List[Var]] = {}
    counters: Dict[str, int] = {}

    def fresh(name: str) -> Var:
        counters[name] = counters.get(name, 0) + 1
        v = Var(name, counters[name])
        stacks.setdefault(name, []).append(v)
        return v

    def current(name: str) -> Var:
        if not stacks.get(name):
            raise SSAError(f"variable '{name}' has no reaching definition (internal error)")
        return stacks[name][-1]

    def rename_use(v: Value) -> Value:
        if isinstance(v, Var) and v.version is None:
            return current(v.name)
        return v

    work: list = [("enter", cfg.entry)]
    while work:
        kind, payload = work.pop()
        if kind == "exit":
            for name in payload:
                stacks[name].pop()
            continue

        bid = payload
        blk = cfg.blocks[bid]
        pushed: List[str] = []
        for ins in blk.instrs:
            if not isinstance(ins, Phi):
                ins.replace_uses(rename_use)
            for d in ins.defs():
                if isinstance(d, Var) and d.version is None:
                    ins.dest = fresh(d.name)
                    pushed.append(d.name)
        for s in cfg.succs(bid):
            for ins in cfg.blocks[s].instrs:
                if isinstance(ins, Phi):
                    ins.incoming[bid] = current(ins.var)
        work.append(("exit", pushed))
        for child in reversed(dom.children[bid]):
            work.append(("enter", child))


def build_ssa(cfg: CFG) -> SSAProgram:
    ssa_cfg = copy.deepcopy(cfg)
    dom = analyze_dominance(ssa_cfg)
    _insert_phis(ssa_cfg, dom)
    _rename(ssa_cfg, dom)

    program = SSAProgram(ssa_cfg, dom)
    for bid in sorted(ssa_cfg.blocks):
        for ins in ssa_cfg.blocks[bid].instrs:
            for d in ins.defs():
                if d in program.defs:
                    raise SSAError(f"'{d}' is defined more than once (internal error)")
                program.defs[d] = (bid, ins)
    return program
