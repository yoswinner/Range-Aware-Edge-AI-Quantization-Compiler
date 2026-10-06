"""Basic blocks, control-flow graph and dominance analysis."""

from src.cfg.cfg import BasicBlock, CFG, Edge, build_cfg
from src.cfg.dominators import (
    DominatorInfo,
    compute_dominators,
    dominance_frontiers,
    dominates,
)

__all__ = [
    "BasicBlock", "CFG", "Edge", "build_cfg",
    "DominatorInfo", "compute_dominators", "dominance_frontiers", "dominates",
]
