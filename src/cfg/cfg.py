"""Leader-based basic-block construction and the control-flow graph.

Leaders (as in the review, Section 4.4)
---------------------------------------
1. the first instruction of the program;
2. the target of any jump (the ``Label`` instruction it names);
3. the instruction immediately following a ``Jump`` or ``CondJump``.

A basic block is a leader plus all instructions up to (not including) the next
leader. Edges:

* ``Jump``      -> one ``jump`` edge to the target block;
* ``CondJump``  -> a ``true`` edge to the target block and a ``false`` edge to
  the fall-through block (so a conditional branch has two successors);
* anything else -> a ``fallthrough`` edge to the next block.

A loop back-edge is simply a jump (or edge) whose target was already reached
earlier in a depth-first traversal; :meth:`CFG.back_edges` reports them.

A synthetic, empty **entry block (B0)** is always added in front of the first
real block. It guarantees that the entry has no predecessors, even when the
program starts with a loop header, which the SSA construction relies on.
Blocks unreachable from the entry are discarded.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.ir.tac import CondJump, Instr, Jump, Label, TACProgram


@dataclass
class Edge:
    src: int
    dst: int
    kind: str  # 'fallthrough' | 'jump' | 'true' | 'false'


@dataclass
class BasicBlock:
    id: int
    instrs: List[Instr] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"B{self.id}"

    @property
    def label(self) -> Optional[str]:
        if self.instrs and isinstance(self.instrs[0], Label):
            return self.instrs[0].name
        return None


class CFG:
    def __init__(self, blocks: Dict[int, BasicBlock], edges: List[Edge], entry: int,
                 symbols: Optional[dict] = None):
        self.blocks = blocks
        self.edges = edges
        self.entry = entry
        self.symbols = symbols if symbols is not None else {}
        self._reindex()

    def _reindex(self) -> None:
        self._succ: Dict[int, List[int]] = {b: [] for b in self.blocks}
        self._pred: Dict[int, List[int]] = {b: [] for b in self.blocks}
        for e in self.edges:
            self._succ[e.src].append(e.dst)
            self._pred[e.dst].append(e.src)

    def succs(self, block_id: int) -> List[int]:
        return self._succ[block_id]

    def preds(self, block_id: int) -> List[int]:
        return self._pred[block_id]

    def edge_kind(self, src: int, dst: int) -> str:
        for e in self.edges:
            if e.src == src and e.dst == dst:
                return e.kind
        raise KeyError((src, dst))

    # -- traversals ----------------------------------------------------------
    def reverse_postorder(self) -> List[int]:
        visited = {self.entry}
        post: List[int] = []
        stack = [(self.entry, iter(self.succs(self.entry)))]
        while stack:
            node, it = stack[-1]
            for s in it:
                if s not in visited:
                    visited.add(s)
                    stack.append((s, iter(self.succs(s))))
                    break
            else:
                post.append(node)
                stack.pop()
        return list(reversed(post))

    def back_edges(self) -> List[Tuple[int, int]]:
        """Edges ``(u, v)`` where ``v`` is on the DFS stack when ``u -> v`` is seen
        (``v`` is a loop header and ``u`` the end of the loop body)."""
        state = {self.entry: 1}  # 1 = on stack, 2 = finished
        found: List[Tuple[int, int]] = []
        stack = [(self.entry, iter(self.succs(self.entry)))]
        while stack:
            node, it = stack[-1]
            for s in it:
                st = state.get(s, 0)
                if st == 0:
                    state[s] = 1
                    stack.append((s, iter(self.succs(s))))
                    break
                if st == 1:
                    found.append((node, s))
            else:
                state[node] = 2
                stack.pop()
        return found

    def remove_unreachable(self) -> None:
        reachable = set(self.reverse_postorder())
        self.blocks = {b: blk for b, blk in self.blocks.items() if b in reachable}
        self.edges = [e for e in self.edges if e.src in reachable and e.dst in reachable]
        self._reindex()

    # -- display -------------------------------------------------------------
    def format(self, annotate: bool = False) -> str:
        back = set(self.back_edges())
        lines: List[str] = []
        for bid in sorted(self.blocks):
            blk = self.blocks[bid]
            succ = ", ".join(
                f"B{s}({self.edge_kind(bid, s)}{', back-edge' if (bid, s) in back else ''})"
                for s in self.succs(bid)
            )
            preds = ", ".join(f"B{p}" for p in self.preds(bid))
            tag = " (entry)" if bid == self.entry else ""
            lines.append(f"B{bid}{tag}:  preds=[{preds}]  succs=[{succ}]")
            for ins in blk.instrs:
                text = ins.format(annotate=annotate)
                lines.append(("  " if isinstance(ins, Label) else "    ") + text)
        return "\n".join(lines)


def build_cfg(program: TACProgram) -> CFG:
    instrs = program.instrs
    targets = {i.target for i in instrs if isinstance(i, (Jump, CondJump))}

    leaders = set()
    if instrs:
        leaders.add(0)
    for idx, ins in enumerate(instrs):
        if isinstance(ins, Label) and ins.name in targets:
            leaders.add(idx)
        if isinstance(ins, (Jump, CondJump)) and idx + 1 < len(instrs):
            leaders.add(idx + 1)

    starts = sorted(leaders)
    blocks: Dict[int, BasicBlock] = {0: BasicBlock(0, [])}  # synthetic entry
    order: List[int] = []
    for k, start in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(instrs)
        bid = k + 1
        blocks[bid] = BasicBlock(bid, list(instrs[start:end]))
        order.append(bid)

    label_to_block = {}
    for bid in order:
        lbl = blocks[bid].label
        if lbl is not None:
            label_to_block[lbl] = bid

    edges: List[Edge] = []

    def add_edge(src: int, dst: int, kind: str) -> None:
        if not any(e.src == src and e.dst == dst for e in edges):
            edges.append(Edge(src, dst, kind))

    if order:
        add_edge(0, order[0], "fallthrough")
    for k, bid in enumerate(order):
        last = blocks[bid].instrs[-1]
        nxt = order[k + 1] if k + 1 < len(order) else None
        if isinstance(last, Jump):
            add_edge(bid, label_to_block[last.target], "jump")
        elif isinstance(last, CondJump):
            add_edge(bid, label_to_block[last.target], "true")
            if nxt is not None:
                add_edge(bid, nxt, "false")
        elif nxt is not None:
            add_edge(bid, nxt, "fallthrough")

    cfg = CFG(blocks, edges, entry=0, symbols=dict(program.symbols))
    cfg.remove_unreachable()
    return cfg
