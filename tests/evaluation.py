"""Reproducible evaluation runner for the Range-Aware Edge AI Quantization Compiler.

Evaluates the compiler pipeline across benchmarks covering:
- Provably safe INT8 arithmetic
- Control-flow join (SSA phi node range merges)
- Direct and intermediate overflow rejection
- Non-integral (fractional) value rejection
- Loop widening and conservative unknown fallback
- Exact INT8 boundary fits ([-128, 127])
- End-to-end simulation equivalence between original and quantized IR
- Absolute safety guarantee: ZERO false positives (no unsafe value quantized)

Run via:
    python -m tests.evaluation
    python evaluate.py
"""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from src.ast.types import Type
from src.pipeline import CompilationResult, compile_source
from src.quantization.safety import RejectKind


@dataclass
class BenchmarkCase:
    name: str
    category: str
    source: str
    inputs: Optional[List[Any]] = None
    narrow: bool = False
    prune_unreachable: bool = False


BENCHMARKS: List[BenchmarkCase] = [
    BenchmarkCase(
        name="safe_arithmetic",
        category="Provably Safe INT8",
        source="""
        int x = 10;
        int y = 20;
        int z = x + y;
        print z;
        """,
    ),
    BenchmarkCase(
        name="overflow_rejection",
        category="Overflow Rejection",
        source="""
        int x = 100;
        int y = 30;
        int z = x + y;
        print z;
        """,
    ),
    BenchmarkCase(
        name="non_integral_rejection",
        category="Non-Integral Rejection",
        source="""
        float x = 10.0;
        float y = 3.5;
        float z = x + y;
        print z;
        """,
    ),
    BenchmarkCase(
        name="if_else_phi",
        category="Control Flow / Phi Merge",
        source="""
        int x = 10;
        int y = 20;
        int max = 0;
        if (x > y) {
            max = x;
        } else {
            max = y;
        }
        print max;
        """,
    ),
    BenchmarkCase(
        name="while_loop_widening",
        category="Loop Widening Fallback",
        source="""
        int x = 5;
        int sum = 0;
        while (x > 0) {
            sum = sum + x;
            x = x - 1;
        }
        print sum;
        """,
        narrow=False,
    ),
    BenchmarkCase(
        name="bounded_loop_counter",
        category="Bounded Loop Narrowing",
        source="""
        int i = 0;
        while (i < 10) {
            i = i + 1;
        }
        print i;
        """,
        narrow=True,
    ),
    BenchmarkCase(
        name="stabilizing_loop",
        category="Stabilizing Loop",
        source="""
        int x = 0;
        int n = 4;
        while (n > 0) {
            x = 1 - x;
            n = n - 1;
        }
        print x;
        """,
        narrow=False,
    ),
    BenchmarkCase(
        name="branch_refinement",
        category="Branch Refinement",
        source="""
        int x = 15;
        int y = 0;
        if (x >= 10) {
            y = x - 5;
        } else {
            y = x + 5;
        }
        print y;
        """,
    ),
    BenchmarkCase(
        name="intermediate_overflow",
        category="Intermediate Overflow Block",
        source="""
        int a = 100;
        int b = 50;
        int c = a + b;
        int d = c - 50;
        print d;
        """,
    ),
    BenchmarkCase(
        name="boundary_fit_exact",
        category="Exact INT8 Boundaries",
        source="""
        int min_val = -128;
        int max_val = 127;
        print min_val;
        print max_val;
        """,
    ),
    BenchmarkCase(
        name="unsupported_op_rejection",
        category="Unsupported Operator",
        source="""
        int a = 20;
        int b = 4;
        float c = a / b;
        print c;
        """,
    ),
    BenchmarkCase(
        name="edge_linear_transform",
        category="Edge AI Linear Layer",
        source="""
        int weight = 3;
        int bias = 5;
        int feat = 15;
        int y = feat * weight + bias;
        print y;
        """,
    ),
]


@dataclass
class BenchmarkReport:
    name: str
    category: str
    total_ssa: int
    safe_count: int
    quantized_count: int
    blocked_count: int
    rejected_count: int
    rejection_reasons: Dict[str, int]
    sim_equivalent: bool
    sim_orig_out: List[Any]
    sim_quant_out: List[Any]
    safety_violations: int  # Must be 0


def evaluate_case(case: BenchmarkCase) -> BenchmarkReport:
    result = compile_source(
        case.source,
        inputs=case.inputs or [],
        narrow=case.narrow,
        prune_unreachable=case.prune_unreachable,
    )
    q = result.quantization
    r = result.ranges

    total_ssa = len(q.decisions)
    safe_count = sum(1 for d in q.decisions.values() if d.safe)
    quantized_count = len(q.quantized)
    blocked_count = len(q.blocked)
    rejected_count = total_ssa - safe_count

    reasons: Dict[str, int] = {}
    for d in q.decisions.values():
        for k in d.kinds:
            reasons[k.value] = reasons.get(k.value, 0) + 1

    sim = result.simulation
    sim_equivalent = sim.is_equivalent if sim is not None else False
    sim_orig = sim.original_output if sim is not None else []
    sim_quant = sim.quantized_output if sim is not None else []

    # Safety verification: ensure NO quantized value is unsafe
    violations = 0
    for v in q.quantized:
        fact = r.values[v]
        decision = q.decisions[v]
        if not decision.safe:
            violations += 1
        if fact.is_unknown or not fact.integral or fact.lo < -128 or fact.hi > 127:
            violations += 1

    return BenchmarkReport(
        name=case.name,
        category=case.category,
        total_ssa=total_ssa,
        safe_count=safe_count,
        quantized_count=quantized_count,
        blocked_count=blocked_count,
        rejected_count=rejected_count,
        rejection_reasons=reasons,
        sim_equivalent=sim_equivalent,
        sim_orig_out=sim_orig,
        sim_quant_out=sim_quant,
        safety_violations=violations,
    )


def run_evaluation() -> bool:
    print("================================================================================")
    print(" RANGE-AWARE EDGE AI QUANTIZATION COMPILER - REPRODUCIBLE EVALUATION REPORT")
    print("================================================================================")
    print()

    reports: List[BenchmarkReport] = []
    for case in BENCHMARKS:
        report = evaluate_case(case)
        reports.append(report)

    # Format evaluation table
    header = f"{'Benchmark':<26} | {'SSA':<4} | {'Safe':<4} | {'INT8':<4} | {'Block':<5} | {'Reject':<6} | {'Sim Eq':<6} | {'Safety'}"
    print(header)
    print("-" * len(header))

    total_ssa_all = 0
    total_safe_all = 0
    total_quant_all = 0
    total_blocked_all = 0
    total_rejected_all = 0
    total_violations_all = 0
    all_sim_equivalent = True

    for r in reports:
        total_ssa_all += r.total_ssa
        total_safe_all += r.safe_count
        total_quant_all += r.quantized_count
        total_blocked_all += r.blocked_count
        total_rejected_all += r.rejected_count
        total_violations_all += r.safety_violations
        if not r.sim_equivalent:
            all_sim_equivalent = False

        status_sim = "MATCH" if r.sim_equivalent else "DIFF"
        status_safety = "PASS (0)" if r.safety_violations == 0 else f"FAIL ({r.safety_violations})"

        row = (
            f"{r.name:<26} | {r.total_ssa:<4} | {r.safe_count:<4} | {r.quantized_count:<4} | "
            f"{r.blocked_count:<5} | {r.rejected_count:<6} | {status_sim:<6} | {status_safety}"
        )
        print(row)

    print("-" * len(header))
    print()
    print("--------------------------------------------------------------------------------")
    print(" EVALUATION SUMMARY & METRICS")
    print("--------------------------------------------------------------------------------")
    print(f"Total Benchmarks Evaluated:       {len(reports)}")
    print(f"Total SSA Variables Analyzed:     {total_ssa_all}")
    print(f"Variables Labelled SAFE:          {total_safe_all} ({total_safe_all / total_ssa_all * 100:.1f}%)")
    print(f"Variables Quantized to INT8:      {total_quant_all} ({total_quant_all / total_ssa_all * 100:.1f}%)")
    print(f"Variables Blocked / Kept FP32:    {total_blocked_all}")
    print(f"Variables Labelled REJECT:        {total_rejected_all} ({total_rejected_all / total_ssa_all * 100:.1f}%)")
    print(f"Simulation Equivalence Rate:      {'100.0%' if all_sim_equivalent else 'FAILED'}")
    print(f"Safety Violations (False Pos):    {total_violations_all} (No safety violations observed across these {len(reports)} evaluated benchmarks)")
    reduction_pct = (total_quant_all * 0.75 / total_ssa_all * 100) if total_ssa_all else 0
    print(f"Theoretical Storage Reduction:    {reduction_pct:.1f}% (INT8 8-bit vs FP32 32-bit baseline;")
    print("                                  static representation width only; does not claim")
    print("                                  hardware speedup, latency, or energy savings)")
    print("--------------------------------------------------------------------------------")

    passed = (total_violations_all == 0) and all_sim_equivalent
    if passed:
        print(f">> EVALUATION RESULT: ALL PASS (No safety violations observed across these {len(reports)} evaluated benchmarks)")
    else:
        print(">> EVALUATION RESULT: FAILURE")
    print("================================================================================")
    return passed


def main() -> int:
    success = run_evaluation()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
