# CLAUDE HANDOFF DIRECTIVE: Review 3 Academic Project Report Generation

**Project Title:** Range-Aware Edge AI Quantization Compiler
**Web Application:** RANGE//LAB — INT8 Quantization Workbench
**Course:** BCSE307L — Compiler Design
**Institution:** Vellore Institute of Technology, Vellore
**Programme:** B.Tech. Computer Science and Engineering
**Submission Milestone:** Final Project Review 3 (Review 3 Final Report & Demonstration)
**Date of Pack Preparation:** October 2026

**Authoring Team:**
- **Yash Pradhan** (Registration No: `24BCE0702`)
- **Anjini Pandey** (Registration No: `24BCE0714`)
- **Ishita Srivastava** (Registration No: `24BDS0234`)

**Faculty Guide:** Prof. Kanagaraj R.
**Primary Source Documents Provided:**
1. `Review3_Implementation_Evidence_Pack.docx` / `Review3_Implementation_Evidence_Pack.md` (Authoritative technical specification & verified test results)
2. `RANGE_LAB_Screenshot_Catalog.docx` / `RANGE_LAB_Screenshot_Catalog.md` (Visual evidence, academic captions & figure schedule)
3. `Review_2_Report.pdf` (Historical baseline context & literature survey)

---

## 1. Prime Directive and Role for Claude

You are tasked with writing the **authoritative, complete, academic final Review 3 Project Report** for the students' **BCSE307L Compiler Design** course project at **VIT Vellore**.

You do not need to guess, invent, or reverse-engineer the compiler implementation. All facts, mathematical formulations, grammar definitions, transfer functions, test metrics, benchmark tables, and screenshot references are fully verified and documented in the accompanying **`Review3_Implementation_Evidence_Pack.md`** and **`RANGE_LAB_Screenshot_Catalog.md`**.

Your role is to transform this technical evidence pack into a formal, beautifully phrased, publication-grade academic report that adheres strictly to the required university structure.

---

## 2. Structural Template Directive (Mandatory Section Numbering)

The university-supplied Review 3 report template strictly defines the following table of contents:

```text
1. INTRODUCTION
   1.1 BACKGROUND
   1.2 MOTIVATIONS
   1.3 SCOPE OF THE PROJECT
2. PROJECT DESCRIPTION AND GOALS
   2.1 LITERATURE REVIEW
   2.2 RESEARCH GAP
   2.3 OBJECTIVES
   2.4 PROBLEM STATEMENT
[FLAGGED: Section 3 is omitted in the faculty template — preserve jump from 2 to 4]
4. DESIGN APPROACH AND DETAILS
   4.1 SYSTEM ARCHITECTURE
5. METHODOLOGY AND TESTING
   5.1 Module Description
   5.2 Testing
6. PROJECT DEMONSTRATION – Implementations
7. RESULT AND DISCUSSION
8. CONCLUSION AND FUTURE ENHANCEMENTS
9. REFERENCES
APPENDIX A – SAMPLE CODE
```

> [!WARNING]
> **DO NOT SILENTLY RENUMBER OR INVENT SECTION 3**
> The official template jumps directly from Section 2 to Section 4. You must preserve this exact numbering and heading hierarchy. In the introductory remarks or preface, explicitly include a footnote or editorial note: *"Note: In accordance with the official course template guidelines, Section 3 is omitted in this report structure."*

---

## 3. Core Academic Guardrails & Boundaries

To preserve strict academic integrity, you must adhere to the following technical boundaries:

1. **Center on Compiler Construction, Not Just the Web App:**
   - The primary contribution of this project is the **SSA-based static analysis compiler**, **abstract range interpretation**, **path-sensitive branch refinement**, **loop narrowing**, and **INT8 safety verification**.
   - The web application (**RANGE//LAB**) is the interactive demonstration workbench that visualizes these compiler phases. It does not replace the compiler's analytical contributions.
2. **Strict Range & Integrality Boundaries:**
   - The signed INT8 interval is strictly $[-128, 127]$.
   - Values $\le -129$ or $\ge 128$ are conservatively rejected for overflow risk.
   - Values must be mathematically integral (`integral=True`) on all execution paths. Float variables and division results are safely rejected.
3. **No Unmeasured Hardware Performance Claims:**
   - The compiler includes a **software simulation backend** (`src/backend/simulator.py`) for validation.
   - It is **not** an LLVM backend, an on-device deployment runtime, or a hardware accelerator.
   - **Do not claim** measured execution speedups, latency reductions, energy savings, or physical device deployment performance.
4. **Theoretical Representation-Width Derivation:**
   - Report the memory reduction strictly as a **theoretical static representation-width calculation**:
     $$\text{Theoretical Width Reduction} = \frac{32 \times (32 - 8)}{54 \times 32} \times 100\% \approx 44.44\%$$
   - Clearly state that this reflects static bit-width savings across provably safe intermediate representations, not physical memory bandwidth.
5. **Empirical Safety & Equivalence Boundaries:**
   - Replace any absolute claims like "Absolute conservative guarantee" with: *"No safety violations were observed across the 12 evaluated benchmarks."*
   - Explicitly clarify that this absence of violations is an empirical benchmark evaluation result demonstrating that the compiler's static analysis safety rules behaved conservatively on tested workloads, and not by itself a universal formal proof of compiler correctness across infinite programs.
   - Describe simulator matches (`SIMULATION EQUIVALENT (MATCH)`) as empirical validation confirming that 8-bit two's-complement arithmetic reproduces 32-bit semantics on the executed benchmark inputs. (`SIMULATION EQUIVALENT (MATCH)`) as empirical validation confirming that 8-bit two's-complement arithmetic reproduces 32-bit semantics on the **executed benchmark inputs**, rather than as an absolute universal formal verification proof across all infinite program inputs.
6. **Zero Citation Fabrication:**
   - Cite only the 12 authentic academic papers preserved from Review 2 (listed in Section 7 of this directive). Never invent authors, conference venues, DOIs, or page numbers.

---

## 4. Section-by-Section Authoring Guide

Use the following mapping to author each section of the Review 3 report using `Review3_Implementation_Evidence_Pack.md`:

### Section 1: Introduction (1.1 Background, 1.2 Motivations, 1.3 Scope)
- **Content:** Shift of AI inference to edge devices; resource constraints (compute, memory, power); pitfalls of heuristic post-training calibration (PTQ); why a compiler static analysis approach provides provable safety guarantees.
- **Scope:** Mini numerical language (`.qc`), teaching-scale multi-pass compiler, signed INT8 quantization.
- **Source in Pack:** Sections A.1, A.3, F.1.

### Section 2: Project Description and Goals (2.1 Literature Review, 2.2 Research Gap, 2.3 Objectives, 2.4 Problem Statement)
- **Content:** Literature review synthesizing edge AI (Zhou et al. [1], Chen & Ran [2]), integer quantization (Jacob et al. [3], Krishnamoorthi [4]), abstract interpretation (Cousot & Cousot [5], [6], Bourdoncle [7], Astrée [8]), and SSA intermediate representations (Cytron et al. [9]).
- **Research Gap:** Existing edge quantization frameworks rely on dynamic calibration datasets or profiling; they lack static formal safety checks during intermediate code optimization.
- **Objectives:** Formal grammar specification, SSA construction, path-sensitive interval analysis, sound loop narrowing, intermediate overflow dependency blocking, and visual workbench demonstration.
- **Source in Pack:** Sections A.2, D, E, J.

### Section 4: Design Approach and Details (4.1 System Architecture)
- **Content:** End-to-end multi-pass pipeline architecture. Three-Address Code (TAC) generation, basic block partitioning and leader identification, Control-Flow Graph construction, and minimal SSA form construction via dominance frontiers.
- **Full-Stack Architecture:** Decoupled client-server design connecting React 19 frontend to FastAPI backend server via structured JSON serialization.
- **Figures to Embed:** **Figure 6** (CFG View) and **Figure 10** (SSA φ-Nodes View).
- **Source in Pack:** Sections B.1, B.2, F.1–F.4.

### Section 5: Methodology and Testing (5.1 Module Description, 5.2 Testing)
- **Content (5.1 Module Description):**
  - Abstract value domain lattice $\mathcal{D} = \mathcal{I} \times \mathcal{B} \times \mathcal{Z}$ with exact rational arithmetic (`Fraction`).
  - Monotonic interval transfer functions for arithmetic and relational operations.
  - Path-sensitive branch condition refinement with discrete integer shifts ($\pm 1$).
  - Kleene iteration with widening threshold ($\nabla$) and sound narrowing iterations ($\Delta$).
  - INT8 quantization safety rules and intermediate overflow dependency blocking.
  - Software simulator execution model.
- **Content (5.2 Testing):**
  - Unit testing methodology: 138 tests passing (`OK`) with 0 failures in ~0.35s.
  - Reproducible benchmark evaluation suite (`evaluate.py`) running 12 benchmarks.
  - Frontend production build verification (`npm run build`, 0 errors).
- **Figures to Embed:** **Figure 2** (INT8 Safety), **Figure 7** (Simulator), **Figure 8** (Loop Narrowing), **Figure 9** (Lexer/AST), **Figure 11** (Ranges Table), **Figure 13** (Quantized IR Diff), and **Figure 14** (Terminal Test Suite).
- **Source in Pack:** Sections C, F.2–F.7, G.1–G.3.

### Section 6: Project Demonstration – Implementations
- **Content:** Practical demonstration of the RANGE//LAB workbench interface. Monaco Editor with live syntax checking, multi-stage pipeline bar, interactive CFG inspection, and deep SSA Variable Inspector drawer. Walk through inspecting $z.1$ and traversing in-place to operand $x.1$.
- **Figures to Embed:** **Figure 1** (Main Workbench), **Figure 4** (SSA Inspector $z.1$), and **Figure 5** (Operand Navigation $x.1$).
- **Source in Pack:** Sections B.2, F.8, H.

### Section 7: Result and Discussion
- **Content:** Detailed analysis of the 12 reproducible benchmarks. Present the comprehensive evaluation table (54 SSA variables, 35 safe, 32 quantized to INT8, 3 blocked, 19 rejected).
- **Discussion Points:**
  - 100% simulation equivalence rate across all benchmarks.
  - No safety violations observed across the 12 evaluated benchmarks (empirical validation of conservative safety rules).
  - Theoretical storage-width reduction ($44.44\%$) derivation and boundary.
  - Analysis of overflow rejection (`overflow_rejection.qc`).
  - Analysis of branch refinement and unreachable path detection (`branch_refine.qc`).
  - Analysis of intermediate overflow blocking (`intermediate_overflow.qc`).
- **Figures to Embed:** **Figure 3** (Overflow Rejection) and **Figure 12** (Branch Refinement Unreachable Path).
- **Source in Pack:** Sections G.2, G.3, L.

### Section 8: Conclusion and Future Enhancements
- **Content:** Summary of compiler contributions; proven viability of static range analysis for INT8 quantization.
- **Future Work:** Multidimensional array bounds, affine polyhedral loop unrolling, automated fixed-point scale factor synthesis, native LLVM IR code emission.
- **Source in Pack:** Section I.

### Section 9: References
- **Content:** Exact bibliography entries [1]–[12] formatted in standard IEEE academic style.
- **Source in Pack:** Section J.

### Appendix A: Sample Code
- **Content:** Complete source code listings and analytical walkthroughs for the 7 key `.qc` benchmark programs: `safe_arithmetic.qc`, `overflow_rejection.qc`, `non_integral_rejection.qc`, `if_else_phi.qc`, `branch_refine.qc`, `bounded_loop.qc`, and `unsupported_division.qc`.
- **Source in Pack:** Section K.

---

## 5. Master Figure Integration Schedule

Claude must embed or reference the 14 verified screenshots exactly according to this schedule:

| Figure ID | Target Report Section | Recommended Caption | Dimensions | Source Filename |
|---|---|---|---|---|
| **Figure 1** | Section 6 | Figure 1: RANGE//LAB Integrated Compiler Workbench Desktop Interface (Range Analysis View) (`safe_arithmetic.qc`) | 2244 × 1239 px | `artifacts/screenshots/01-main-workbench.png` |
| **Figure 2** | Section 5.1 | Figure 2: INT8 Safety Inferred Interval vs Signed Boundary Comparison (`safe_arithmetic.qc`) | 2244 × 1209 px | `artifacts/screenshots/02-int8-safety.png` |
| **Figure 3** | Section 7.2 | Figure 3: Direct Overflow Rejection ($z.1 = [130, 130] > 127$) and Type Preservation (`overflow_rejection.qc`) | 2244 × 1209 px | `artifacts/screenshots/03-overflow-rejection.png` |
| **Figure 4** | Section 6 | Figure 4: Interactive SSA Variable Inspector Side Drawer Displaying $z.1 = x.1 + y.1$ ($[30, 30]$) | 2244 × 1209 px | `artifacts/screenshots/04-ssa-inspector-z1.png` |
| **Figure 5** | Section 6 | Figure 5: In-Place Operand Traversal and Def-Use Navigation Updating Drawer to $x.1 = 10$ | 2241 × 1199 px | `artifacts/screenshots/05-ssa-inspector-x1.png` |
| **Figure 6** | Section 4.1 | Figure 6: Interactive Control-Flow Graph (CFG) Basic Block Visualization with Branch Refinement Reachability (`if_else_phi.qc`) | 2241 × 1199 px | `artifacts/screenshots/06-control-flow-graph.png` |
| **Figure 7** | Section 5.2 | Figure 7: Dual-Engine Simulator Execution and Equivalence Verification (Match '30') | 2241 × 1199 px | `artifacts/screenshots/07-simulation-equivalence.png` |
| **Figure 8** | Section 5.1 | Figure 8: Bounded Loop Interval Convergence under Sound Iterative Narrowing ($[0, 10]$) | 2241 × 1199 px | `artifacts/screenshots/08-loop-narrowing.png` |
| **Figure 9** | Section 5.1 | Figure 9: Lexer Token Stream Count (23 tokens) and Hierarchical Abstract Syntax Tree (AST) View | 2244 × 1286 px | `artifacts/screenshots/09-lexer-ast.png` |
| **Figure 10** | Section 4.1 | Figure 10: Three-Address Code and SSA Intermediate Representation with φ-Node Resolution | 2244 × 1286 px | `artifacts/screenshots/10-tac-ssa-phi.png` |
| **Figure 11** | Section 5.1 | Figure 11: Static Range Analysis Table with Integrality Flags and Fixed-Point Convergence | 2244 × 1286 px | `artifacts/screenshots/11-range-analysis.png` |
| **Figure 12** | Section 7.3 | Figure 12: Path-Sensitive Branch Refinement and Static Unreachable Path Detection (`branch_refine.qc`) | 2244 × 1286 px | `artifacts/screenshots/12-branch-refinement.png` |
| **Figure 13** | Section 5.1 | Figure 13: Side-by-Side Quantized IR Diff and Intermediate Overflow Dependency Blocking | 2244 × 1286 px | `artifacts/screenshots/13-quantized-ir-diagnostics.png` |
| **Figure 14** | Section 5.2 | Figure 14: Automated Unit Test Suite (138 Tests OK) and Reproducible Benchmark Terminal Summary | 2244 × 1286 px | `artifacts/screenshots/14-verification-results.png` |

---

## 6. Exact Verified Test and Benchmark Metrics for Inclusion

When reporting empirical results in Section 5.2 and Section 7, cite these exact figures:
- **Unit Test Total:** **138 tests** executed, **138 passed (100%)**, 0 failures, 0 errors, run time: **~0.35s**.
- **Verified Module Breakdown (17 Test Modules, Sum = 138 Tests):**
  - `tests/range_analysis/test_range_analysis.py`: 27 tests
  - `tests/analysis/test_branch_refinement.py`: 15 tests
  - `tests/backend/test_simulator.py`: 11 tests
  - `tests/integration/test_pipeline.py`: 10 tests
  - `tests/quantization/test_quantization.py`: 10 tests
  - `tests/api/test_api.py`: 9 tests (includes new CFG reachability regression test `test_cfg_reachability_if_else_phi`)
  - `tests/quantization/test_safety_edge_cases.py`: 9 tests
  - `tests/analysis/test_analysis.py`: 8 tests
  - `tests/parser/test_parser.py`: 7 tests
  - `tests/ssa/test_ssa.py`: 7 tests
  - `tests/analysis/test_loop_narrowing.py`: 6 tests
  - `tests/cfg/test_cfg.py`: 4 tests
  - `tests/ir/test_tac.py`: 4 tests
  - `tests/lexer/test_lexer.py`: 4 tests
  - `tests/semantic/test_semantic.py`: 4 tests
  - `tests/integration/test_boolean_comparisons.py`: 2 tests
  - `tests/ast_tests/test_ast.py`: 1 test
  *(Exact check: 27 + 15 + 11 + 10 + 10 + 9 + 9 + 8 + 7 + 7 + 6 + 4 + 4 + 4 + 4 + 2 + 1 = 138 tests)*
- **Evaluated Benchmark Programs:** **12 programs** (`safe_arithmetic`, `overflow_rejection`, `non_integral_rejection`, `if_else_phi`, `while_loop_widening`, `bounded_loop_counter`, `stabilizing_loop`, `branch_refinement`, `intermediate_overflow`, `boundary_fit_exact`, `unsupported_op_rejection`, `edge_linear_transform`).
- **Total Analyzed SSA Variables:** **54 variables**.
- **Quantization Classification:**
  - **Proven Safe Variables:** **35 (64.8%)**
  - **Quantized to INT8:** **32 (59.3%)**
  - **Blocked Intermediate Variables:** **3 (5.6%)**
  - **Rejected Variables:** **19 (35.2%)**
- **Simulation Numerical Equivalence Rate:** **100.0%** across all 12 benchmarks.
- **Observed Safety Violations:** **No safety violations were observed across the 12 evaluated benchmarks** (0 false positives on evaluated SSA variables; empirical finding, not universal proof).
- **Theoretical Representation-Width Reduction:** **44.44%** ($768 / 1,728$ bits saved).

---

## 7. Authoritative Academic Bibliography

Include these exact 12 citations in Section 9:

```bibtex
[1] Z. Zhou, X. Chen, E. Li, L. Zeng, K. Luo, and J. Zhang, "Edge intelligence: Paving the last mile of artificial intelligence with edge computing," Proceedings of the IEEE, vol. 107, no. 8, pp. 1738–1762, Aug. 2019.

[2] J. Chen and X. Ran, "Deep learning with edge computing: A review," Proceedings of the IEEE, vol. 107, no. 8, pp. 1655–1674, Aug. 2019.

[3] B. Jacob, S. Kligys, B. Chen, M. Zhu, M. Tang, A. Howard, H. Adam, and D. Kalenichenko, "Quantization and training of neural networks for efficient integer-arithmetic-only inference," in Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR), 2018, pp. 2704–2713.

[4] R. Krishnamoorthi, "Quantizing deep convolutional networks for efficient inference: A whitepaper," arXiv preprint arXiv:1806.08342, 2018.

[5] P. Cousot and R. Cousot, "Static determination of dynamic properties of programs," in Proc. 2nd Int. Symp. on Programming (ISOP), Paris, France: Dunod, 1976, pp. 106–130.

[6] P. Cousot and R. Cousot, "Abstract interpretation: A unified lattice model for static analysis of programs by construction or approximation of fixpoints," in Proc. 4th ACM SIGACT-SIGPLAN Symp. on Principles of Programming Languages (POPL), 1977, pp. 238–252.

[7] F. Bourdoncle, "Efficient chaotic iteration strategies with widenings," in Formal Methods in Programming and Their Applications, LNCS vol. 735. Berlin, Germany: Springer, 1993, pp. 128–141.

[8] B. Blanchet, P. Cousot, R. Cousot, J. Feret, L. Mauborgne, A. Miné, D. Monniaux, and X. Rival, "A static analyzer for large safety-critical software," in Proc. ACM SIGPLAN Conf. on Programming Language Design and Implementation (PLDI), 2003, pp. 196–207.

[9] R. Cytron, J. Ferrante, B. K. Rosen, M. N. Wegman, and F. K. Zadeck, "Efficiently computing static single assignment form and the control dependence graph," ACM Trans. Program. Lang. Syst., vol. 13, no. 4, pp. 451–490, Oct. 1991.

[10] C. Lattner and V. Adve, "LLVM: A compilation framework for lifelong program analysis and transformation," in Proc. Int. Symp. on Code Generation and Optimization (CGO), 2004, pp. 75–86.

[11] J. Ragan-Kelley, C. Barnes, A. Adams, S. Paris, F. Durand, and S. Amarasinghe, "Halide: A language and compiler for optimizing parallelism, locality, and recomputation in image processing pipelines," in Proc. ACM SIGPLAN Conf. on Programming Language Design and Implementation (PLDI), 2013, pp. 519–530.

[12] T. Chen, T. Moreau, Z. Jiang, L. Zheng, E. Yan, M. Cowan, H. Shen, L. Wang, Y. Hu, L. Ceze, C. Guestrin, and A. Krishnamurthy, "TVM: An automated end-to-end optimizing compiler for deep learning," in Proc. 13th USENIX Symp. on Operating Systems Design and Implementation (OSDI), 2018, pp. 578–594.
```

---

## 8. Final Checklist for Claude

Before concluding report generation, verify:
- [ ] Section numbering strictly follows $1 \rightarrow 2 \rightarrow 4 \rightarrow 5 \rightarrow 6 \rightarrow 7 \rightarrow 8 \rightarrow 9 \rightarrow \text{Appendix A}$.
- [ ] Section 3 omission is noted without breaking the template numbering.
- [ ] All 14 figures are referenced and placed in their designated sections with accurate captions.
- [ ] Exact test metrics (138 tests passing, 0 failures, 12 benchmarks, 54 vars, 0 violations) are cited.
- [ ] Theoretical storage reduction ($44.44\%$) is clearly derived and distinguished from hardware speedups.
- [ ] All 12 literature references [1]–[12] are integrated into the text and listed in Section 9.
- [ ] The academic tone is formal, rigorous, and appropriate for an upper-level undergraduate Compiler Design capstone.
