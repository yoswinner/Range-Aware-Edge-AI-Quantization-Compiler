"""Command-line entry point.

    python -m src.main examples/if_else_phi.qc
    python -m src.main examples/while_loop.qc --emit ssa ranges diagnostics
    python -m src.main examples/safe_arithmetic.qc --emit all

Stages that can be inspected with ``--emit``: tokens, ast, tac, cfg, ssa,
ranges, quantized, diagnostics, summary (``all`` selects everything). The
default is ``diagnostics summary``.
"""

import argparse
import sys
from typing import List, Optional

from src.analysis.range_analysis import DEFAULT_WIDEN_AFTER
from src.ast.printer import dump
from src.diagnostics.errors import CompilerError
from src.diagnostics.report import format_report, summarize
from src.pipeline import CompilationResult, compile_source

STAGES = ["tokens", "ast", "tac", "cfg", "ssa", "ranges", "quantized", "diagnostics", "summary"]


def _format_ranges(res: CompilationResult) -> str:
    lines = []
    rr = res.ranges
    for _, instr in res.ssa.instructions():
        for v in instr.defs():
            fact = rr.values[v]
            note = "  (widened)" if v in rr.widened else ""
            lines.append(f"{str(v):<8} {fact.format_range():<14} "
                         f"integral={'yes' if fact.integral else 'no':<3}{note}")
    lines.append(
        f"-- {rr.sweeps} sweep(s), converged={rr.converged}, widen_after={rr.widen_after}"
    )
    return "\n".join(lines)


def render(res: CompilationResult, stage: str) -> str:
    if stage == "tokens":
        return "\n".join(str(t) for t in res.tokens)
    if stage == "ast":
        return dump(res.ast)
    if stage == "tac":
        return res.tac.format(show_loc=True)
    if stage == "cfg":
        return res.cfg.format()
    if stage == "ssa":
        dom = res.ssa.dom
        idom = ", ".join(f"B{b}<-B{p}" for b, p in sorted(dom.idom.items()) if p is not None)
        df = ", ".join(f"DF(B{b})={{{','.join('B%d' % x for x in sorted(s))}}}"
                       for b, s in sorted(dom.frontiers.items()) if s)
        return (res.ssa.format() + f"\n-- idom: {idom or '(none)'}"
                + f"\n-- dominance frontiers: {df or '(none)'}")
    if stage == "ranges":
        return _format_ranges(res)
    if stage == "quantized":
        return res.quantization.program.format(annotate=True)
    if stage == "diagnostics":
        return format_report(res.diagnostics)
    if stage == "summary":
        return summarize(res.diagnostics)
    raise ValueError(stage)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.main",
        description="Range-Aware Edge AI Quantization Compiler (static INT8 safety analysis)",
    )
    parser.add_argument("file", help="source file in the mini numerical language (.qc)")
    parser.add_argument("--emit", nargs="+", choices=STAGES + ["all"],
                        default=["diagnostics", "summary"], metavar="STAGE",
                        help="stages to print: " + ", ".join(STAGES) + ", all")
    parser.add_argument("--widen-after", type=int, default=DEFAULT_WIDEN_AFTER,
                        help="ordinary loop iterations before widening to UNKNOWN "
                             f"(default {DEFAULT_WIDEN_AFTER})")
    args = parser.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as fh:
            source = fh.read()
    except OSError as exc:
        print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
        return 2

    try:
        result = compile_source(source, widen_after=args.widen_after)
    except CompilerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    stages = STAGES if "all" in args.emit else args.emit
    for stage in stages:
        print(f"===== {stage} =====")
        print(render(result, stage))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
