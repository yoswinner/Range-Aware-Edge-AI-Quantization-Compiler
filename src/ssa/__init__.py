"""SSA construction (Cytron et al.) over the CFG."""

from src.ssa.construction import SSAProgram, build_ssa
from src.ssa.verify import verify_ssa

__all__ = ["SSAProgram", "build_ssa", "verify_ssa"]
