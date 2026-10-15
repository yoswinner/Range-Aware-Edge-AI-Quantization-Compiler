"""End-to-end driver: source text -> every intermediate artefact.

Pipeline implemented in code::

    lexer -> parser -> AST -> semantic analysis -> TAC -> basic blocks / CFG
          -> SSA -> range + integrality analysis -> INT8 safety decision
          -> quantization rewrite (retyping) -> source-level diagnostics
          -> simulator / backend (executes original vs. quantized IR)
"""

from dataclasses import dataclass
from typing import Any, List, Optional

from src.analysis.range_analysis import DEFAULT_WIDEN_AFTER, RangeResult, analyze_ranges
from src.ast import nodes
from src.backend.simulator import SimulationResult, simulate_programs
from src.cfg.cfg import CFG, build_cfg
from src.diagnostics.report import ValueDiagnostic, build_diagnostics
from src.ir.lowering import generate_tac
from src.ir.tac import TACProgram
from src.lexer.lexer import tokenize
from src.lexer.tokens import Token
from src.parser.parser import Parser
from src.quantization.quantizer import QuantizationResult, quantize
from src.semantic.analyzer import SemanticResult, check
from src.ssa.construction import SSAProgram, build_ssa


@dataclass
class CompilationResult:
    source: str
    tokens: List[Token]
    ast: nodes.Program
    semantic: SemanticResult
    tac: TACProgram
    cfg: CFG
    ssa: SSAProgram
    ranges: RangeResult
    quantization: QuantizationResult
    diagnostics: List[ValueDiagnostic]
    simulation: Optional[SimulationResult] = None


def compile_source(
    source: str,
    widen_after: int = DEFAULT_WIDEN_AFTER,
    inputs: Optional[List[Any]] = None,
    run_simulation: bool = True,
) -> CompilationResult:
    """Run every compiler stage, including range analysis, quantization, and IR simulation.

    Raises ``LexError``, ``ParseError`` or ``SemanticError`` (each carrying
    line/column) if the program is invalid.
    """
    tokens = tokenize(source)
    program = Parser(tokens).parse_program()
    semantic = check(program)
    tac = generate_tac(program)
    cfg = build_cfg(tac)
    ssa = build_ssa(cfg)
    ranges = analyze_ranges(ssa, widen_after=widen_after)
    quant = quantize(ssa, ranges)
    diags = build_diagnostics(ssa, ranges, quant)

    simulation = None
    if run_simulation:
        simulation = simulate_programs(ssa, quant.program, inputs=inputs or [])

    return CompilationResult(
        source, tokens, program, semantic, tac, cfg, ssa,
        ranges, quant, diags, simulation
    )
