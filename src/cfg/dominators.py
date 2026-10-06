"""Dominators and dominance frontiers.

Dominators use the iterative algorithm of Cooper, Harvey and Kennedy ("A Simple,
Fast Dominance Algorithm"): process blocks in reverse postorder and set
``idom(b)`` to the intersection (walk up the partially built dominator tree) of
the already-processed predecessors, until nothing changes.

Dominance frontiers follow the same paper's formulation of Cytron et al.'s
definition: for every join block ``b`` and each predecessor ``p``, every block on
the dominator-tree path from ``p`` up to (excluding) ``idom(b)`` has ``b`` in
its frontier.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from src.cfg.cfg import CFG


@dataclass
class DominatorInfo:
    idom: Dict[int, Optional[int]]            # entry maps to None
    children: Dict[int, List[int]]            # dominator-tree children
    frontiers: Dict[int, Set[int]]            # dominance frontier per block


def compute_dominators(cfg: CFG) -> Dict[int, Optional[int]]:
    rpo = cfg.reverse_postorder()
    number = {b: i for i, b in enumerate(rpo)}
    idom: Dict[int, int] = {cfg.entry: cfg.entry}

    def intersect(a: int, b: int) -> int:
        while a != b:
            while number[a] > number[b]:
                a = idom[a]
            while number[b] > number[a]:
                b = idom[b]
        return a

    changed = True
    while changed:
        changed = False
        for b in rpo:
            if b == cfg.entry:
                continue
            processed = [p for p in cfg.preds(b) if p in idom]
            new = processed[0]
            for p in processed[1:]:
                new = intersect(p, new)
            if idom.get(b) != new:
                idom[b] = new
                changed = True

    result: Dict[int, Optional[int]] = dict(idom)
    result[cfg.entry] = None
    return result


def dominates(idom: Dict[int, Optional[int]], a: int, b: int) -> bool:
    """True if ``a`` dominates ``b`` (every block dominates itself)."""
    node: Optional[int] = b
    while node is not None:
        if node == a:
            return True
        node = idom[node]
    return False


def dominance_frontiers(cfg: CFG, idom: Dict[int, Optional[int]]) -> Dict[int, Set[int]]:
    frontier: Dict[int, Set[int]] = {b: set() for b in cfg.blocks}
    for b in cfg.blocks:
        preds = cfg.preds(b)
        if len(preds) < 2:
            continue
        for p in preds:
            runner: Optional[int] = p
            while runner is not None and runner != idom[b]:
                frontier[runner].add(b)
                runner = idom[runner]
    return frontier


def analyze_dominance(cfg: CFG) -> DominatorInfo:
    idom = compute_dominators(cfg)
    children: Dict[int, List[int]] = {b: [] for b in cfg.blocks}
    for b in cfg.reverse_postorder():
        parent = idom[b]
        if parent is not None:
            children[parent].append(b)
    return DominatorInfo(idom, children, dominance_frontiers(cfg, idom))
