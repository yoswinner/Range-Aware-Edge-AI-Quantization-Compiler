# Review 3 Implementation Evidence Pack: Range-Aware Edge AI Quantization Compiler

**Project Title:** Range-Aware Edge AI Quantization Compiler
**Web Application:** RANGE//LAB — INT8 Quantization Workbench
**Course:** BCSE307L — Compiler Design
**Institution:** Vellore Institute of Technology, Vellore — School of Computer Science and Engineering
**Programme:** B.Tech. Computer Science and Engineering
**Submission Milestone:** Final Project Review 3 (Review 3 Final Report & Demonstration)
**Date:** October 2026

**Student Team Members:**
- **Yash Pradhan** — Registration No: `24BCE0702`
- **Anjini Pandey** — Registration No: `24BCE0714`
- **Ishita Srivastava** — Registration No: `24BDS0234`

**Faculty Guide:** Prof. Kanagaraj R.
**Repository Workspace:** `C:\Coding\GenAI\Projects\Range-Aware-Edge-AI-Quantization-Compiler`
**GitHub Remote:** `https://github.com/yoswinner/Range-Aware-Edge-AI-Quantization-Compiler.git`
**Target Delivery Branch:** `master` (Commit SHA: `8a6451e77b1c472a936f61c671a4a7ef7f9d779a`)

---

> [!IMPORTANT]
> **DOCUMENT PURPOSE & CLAUDE HANDOFF DIRECTIVE**
> This document is the **authoritative, verified technical evidence brief** prepared for **Claude** to draft the final **BCSE307L Review 3 Academic Project Report**. Every claim, code path, mathematical formulation, test metric, benchmark result, and figure mapping herein has been inspected directly against the active codebase, executed on the Python 3.10+ runtime, and verified in the live web application. Claude must use this document as the ground-truth factual source, preserving academic integrity by adhering strictly to the documented capabilities, explicit boundaries, and historical Review 2 continuity without fabricating unsupported features or benchmark claims.

---

## TABLE OF CONTENTS

- [A. Project Identity & Executive Implementation Summary](#a-project-identity--executive-implementation-summary)
- [B. Verified End-to-End System Architecture](#b-verified-end-to-end-system-architecture)
- [C. Complete Implementation Inventory](#c-complete-implementation-inventory)
- [D. Mapping to the Review 3 Academic Report Template](#d-mapping-to-the-review-3-academic-report-template)
- [E. Review 2 Continuity, Evolution, and Delta Analysis](#e-review-2-continuity-evolution-and-delta-analysis)
- [F. In-Depth Methodology & Compiler Implementation Details](#f-in-depth-methodology--compiler-implementation-details)
- [G. Verified Test Suite, Evaluation Metrics & Empirical Results](#g-verified-test-suite-evaluation-metrics--empirical-results)
- [H. Screenshot Evidence & Figure Integration Schedule](#h-screenshot-evidence--figure-integration-schedule)
- [I. Technical Boundaries, Real Limitations & Future Enhancements](#i-technical-boundaries-real-limitations--future-enhancements)
- [J. Preserved Bibliography, References & Citation Guidance](#j-preserved-bibliography-references--citation-guidance)
- [K. Appendix A — Curated Sample Programs (.qc)](#k-appendix-a--curated-sample-programs-qc)
- [L. Fact and Claim Verification Traceability Matrix](#l-fact-and-claim-verification-traceability-matrix)

---

## A. Project Identity & Executive Implementation Summary

### A.1 Overview and Academic Context
The **Range-Aware Edge AI Quantization Compiler** is an end-to-end optimizing compiler system developed as a major course project for **BCSE307L (Compiler Design)** at **Vellore Institute of Technology, Vellore**. The compiler investigates how classical compiler static analysis techniques—specifically **Static Single Assignment (SSA) form**, **abstract interpretation over interval and integrality domains**, **path-sensitive branch condition refinement**, and **sound loop widening and narrowing**—can provide mathematically sound safety guarantees for **reduced-precision integer quantization (INT8)** in edge artificial intelligence workloads.

To provide interactive exploration, pedagogical clarity, and visual verification of the compiler's internal representations, the project incorporates **RANGE//LAB — Interactive INT8 Quantization Workbench**, a modern developer-grade web interface that visualizes every intermediate compiler phase from source tokenization to side-by-side quantized software execution.

### A.2 Historical Baseline (Review 2) vs. Completed Deliverables (Review 3)
A rigorous distinction must be maintained between the compiler baseline documented at **Review 2** and the subsequent implementations completed for **Review 3**:

1. **Review 2 Milestone State:**
   - Designed the mini numerical specification language (`.qc`).
   - Implemented baseline frontend: regex-based lexer (`src/lexer/`), recursive descent parser (`src/parser/`), AST node definitions (`src/ast/`), and semantic type checking (`src/semantic/`).
   - Implemented initial Three-Address Code (TAC) lowering (`src/ir/`) and basic block CFG construction (`src/cfg/`).
   - Implemented initial SSA form construction with dominance frontier phi-placement (`src/ssa/`).
   - Implemented preliminary interval arithmetic over rational numbers (`Fraction`) and basic loop widening (`src/analysis/`).
   - Provided an initial test suite (20 tests initially discovered, with early prototype suites in development).
   - Documented limitations: no path-sensitive branch refinement, loop analysis lost bounds after widening without narrowing, no graphical workbench, no intermediate dependency overflow blocking.

2. **Review 3 Completed Enhancements & New Deliverables:**
   - **Path-Sensitive Branch Refinement (`src/analysis/refinement.py`):** Added conditional edge transfer functions that refine intervals along True and False branch paths, with discrete integer boundary shifts ($\pm 1$) and static unreachable path detection ($ot$).
   - **Sound Loop Narrowing (`src/analysis/range_analysis.py`):** Implemented an iterative narrowing pass following widening convergence, enabling bounded loop counters to recover tight intervals (e.g. $[0, 10]$) and safely qualify for INT8 quantization.
   - **Intermediate Overflow Dependency Blocking (`src/quantization/safety.py`):** Implemented safety rule enforcing that an expression falling within $[-128, 127]$ is blocked from INT8 retyping if any upstream operand or intermediate computation could have overflowed.
   - **Software Simulator Backend (`src/backend/simulator.py`):** Integrated a dual-engine execution simulator that interprets original 32-bit IR alongside 8-bit two's-complement quantized IR, verifying numerical equivalence.
   - **FastAPI REST API Server (`src/api/server.py`, `src/api/serializer.py`):** Implemented an in-process web API driver exposing structured JSON compilation results for all 10 pipeline stages.
   - **RANGE//LAB Web Application (`web/`):** Built a production-grade React 19, TypeScript, and Vite single-page application featuring Monaco Editor, React Flow visual CFG, 10 pipeline stage views, and an interactive SSA Variable Inspector drawer with in-place operand navigation.
   - **Comprehensive Automated Testing:** Expanded automated test coverage to **138 unit and integration tests** passing with 100% success rate in under 0.4 seconds.
   - **Reproducible Evaluation Harness (`evaluate.py`, `tests/evaluation.py`):** Built an automated benchmark runner executing 12 curated benchmark programs, achieving 100% simulation equivalence and zero conservative safety violations.
   - **Photographic Evidence Pack:** Captured and verified **14 high-resolution application screenshots** (`artifacts/screenshots/`) documenting every live feature.

### A.3 Explicit Technical Boundaries and Academic Integrity Rules
The following technical constraints must be explicitly preserved throughout all reporting:
- **Teaching-Scale Numerical Language:** The compiler compiles a focused, C-like imperative language (`.qc`) designed specifically to expose compiler algorithms. It does not compile arbitrary C/C++ or import PyTorch/ONNX computational graphs.
- **Signed INT8 Range Domain:** Quantization safety is governed strictly by the signed 8-bit interval:
  $$	ext{INT8 Domain} = [-128, 127], \quad 	ext{where } -128 	ext{ and } 127 	ext{ are safe if and only if integral.}$$
  Values $\le -129$ or $\ge 128$ are conservatively rejected.
- **Educational Software Simulator:** Execution validation is performed via an in-memory software interpreter that emulates signed 8-bit integer wrap-around. It is **not** an LLVM backend, native binary emitter, or hardware accelerator driver.
- **No Unmeasured Hardware Claims:** The report **must not claim** measured runtime speedups, latency reductions, energy savings, or physical device deployment performance.
- **Theoretical Storage-Width Calculation:** Any reported memory footprint reduction represents a **theoretical static representation-width calculation** (8-bit storage vs. 32-bit baseline for provably safe variables), evaluated strictly as:
  $$	ext{Theoretical Width Reduction} = rac{	ext{Quantized Variables} 	imes (32 - 8)}{	ext{Total Variables} 	imes 32} 	imes 100\%$$
- **Simulation Equivalence Boundary:** Matching outputs between original and quantized IR demonstrate functional equivalence for the **specific inputs tested**, serving as empirical validation rather than a universal formal verification proof across all infinite inputs.

---

## B. Verified End-to-End System Architecture

### B.1 Complete Compiler Pipeline Architecture
The compiler processes `.qc` source programs through nine distinct compiler phases, terminating in software simulation and structured visualization:

```text
               +-------------------------------------------------------+
               |                  Source Code (.qc)                    |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 1. Lexical Analysis (src/lexer/lexer.py)              |
               |    - Regular expression tokenization                  |
               |    - Token stream with line and column tracking       |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 2. Syntax Analysis (src/parser/parser.py)             |
               |    - Recursive descent parsing with AST construction  |
               |    - Precedence climbing for binary expressions       |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 3. Semantic Analysis (src/semantic/analyzer.py)       |
               |    - Symbol table resolution & scope checking         |
               |    - Type checking (int, float, bool)                 |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 4. TAC Generation (src/ir/tac.py)                     |
               |    - Lowering to Three-Address Code with temporaries  |
               |    - Linear instruction representation                |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 5. Control-Flow Graph (src/cfg/cfg.py)                |
               |    - Leader identification & basic block partitioning |
               |    - Directed edges: fallthrough, jump, True/False    |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 6. SSA Form Construction (src/ssa/ssa.py)             |
               |    - Dominator tree & dominance frontiers             |
               |    - Cytron's minimal phi-node placement algorithm    |
               |    - Version renaming: x -> x.1, x.2                  |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 7. Abstract Range Analysis (src/analysis/)            |
               |    - AbstractValue domain with rational Fraction      |
               |    - Path-sensitive branch condition refinement       |
               |    - Kleene iteration, loop widening & narrowing      |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 8. INT8 Quantization Pass (src/quantization/)         |
               |    - Safety verification ([-128, 127] + integrality)  |
               |    - Intermediate dependency tracking                 |
               |    - Selective instruction retyping (int -> int8)     |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               | 9. Software Simulator Backend (src/backend/)          |
               |    - Dual execution of original IR vs quantized IR    |
               |    - Numerical equivalence verification & traces      |
               +-------------------------------------------------------+
```

### B.2 Full-Stack System Architecture (Workbench Integration)
The full application integrates the Python compiler engine with the modern web frontend via a clean client-server architecture:

```text
+-----------------------------------------------------------------------------------------+
|                                    BROWSER CLIENT                                       |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   |                         RANGE//LAB Web Application                              |   |
|   |  - Monaco Code Editor: Custom .qc language tokenizer & syntax highlighting      |   |
|   |  - Stage Navigator: 10 pipeline tabs with real-time count & status badges       |   |
|   |  - Interactive CFG Visualizer: React Flow node-edge basic block graph           |   |
|   |  - SSA Variable Inspector: Side-drawer with in-place operand def-use traversal  |   |
|   |  - Diff View: Pre-quantization SSA vs post-quantization INT8 IR comparison      |   |
|   +---------------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------------+
                                           |
                              HTTP / REST JSON (Port 8000)
                                           v
+-----------------------------------------------------------------------------------------+
|                               FASTAPI APPLICATION SERVER                                |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   |  Endpoints:                                                                     |   |
|   |    POST /api/compile  --> In-process compiler pipeline execution driver         |   |
|   |    POST /api/simulate --> Custom input vector interpretation                    |   |
|   |    GET  /api/examples --> Built-in teaching benchmarks catalogue                |   |
|   |    GET  /api/health   --> Server connectivity and health verification           |   |
|   +---------------------------------------------------------------------------------+   |
|                                           |
|   +---------------------------------------------------------------------------------+   |
|   |  Serialization Engine (src/api/serializer.py):                                  |   |
|   |    Converts Python AST, CFG, SSA, Ranges, and Simulator objects to JSON         |   |
|   +---------------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------------+
                                           |
                               In-Process Python Method Calls
                                           v
+-----------------------------------------------------------------------------------------+
|                       CORE COMPILER & QUANTIZATION ENGINE                               |
|   Lexer -> Parser -> Semantic -> TAC -> CFG -> SSA -> Range Analysis -> INT8 -> Sim    |
+-----------------------------------------------------------------------------------------+
```

---

## C. Complete Implementation Inventory

The following inventory details every module, source file, responsibility, and verification evidence across the active repository:

| # | Subsystem / Module | Source File(s) | Architectural Responsibility | Inputs & Outputs | Status | Verification Evidence & Figures |
|---|---|---|---|---|---|---|
| **1** | **Lexical Analyzer** | `src/lexer/tokens.py`<br>`src/lexer/lexer.py` | Converts raw `.qc` text into typed token stream with line and column tracking. | **In:** Source text<br>**Out:** `List[Token]` | Completed | 138 unit tests passing (`test_lexer.py`). Featured in **Figure 9**. |
| **2** | **Syntax Parser** | `src/parser/parser.py`<br>`src/ast/nodes.py` | Recursive descent parser building structured Abstract Syntax Tree with operator precedence. | **In:** Token stream<br>**Out:** AST `Program` node | Completed | Unit tests in `test_parser.py`. Hierarchical tree visualized in **Figure 9**. |
| **3** | **Semantic Analyzer** | `src/semantic/analyzer.py`<br>`src/semantic/symbols.py` | Scoped symbol table resolution, type inference, undeclared variable checking, type compatibility. | **In:** Raw AST<br>**Out:** Type-checked AST | Completed | Unit tests in `test_semantic.py` verifying duplicate defs and float narrowing errors. |
| **4** | **TAC Lowering** | `src/ir/tac.py`<br>`src/ir/lowering.py<br>src/ir/values.py` | Lowers high-level AST constructs to Three-Address Code with explicit temporaries (`t1`, `t2`). | **In:** Checked AST<br>**Out:** `TACProgram` (instruction list) | Completed | Unit tests in `test_tac.py`. Stage viewer verified in workbench. |
| **5** | **CFG Builder** | `src/cfg/cfg.py`<br>`src/cfg/dominators.py` | Leader identification, basic block splitting, fallthrough and conditional branch edge linking. | **In:** TAC instruction list<br>**Out:** `CFG` graph object | Completed | Unit tests in `test_cfg.py`. Rendered in React Flow in **Figure 6**. |
| **6** | **SSA Form Builder** | `src/ssa/construction.py`<br>`src/ssa/verify.py` | Computes dominator tree, dominance frontiers, minimal phi-node placement, and variable renaming. | **In:** `CFG`<br>**Out:** `SSAProgram` with phi nodes | Completed | Unit tests in `test_ssa.py`. Phi table visualized in **Figure 10**. |
| **7** | **Abstract Value Domain** | `src/analysis/abstract_value.py` | Defines `AbsVal` lattice with exact rational bounds (`Fraction`), integrality, bottom ($ot$), and div-zero flags. | **In:** Rational numbers<br>**Out:** Abstract interval elements | Completed | Unit tests in `test_range_analysis.py`. Bounds displayed in **Figure 2**. |
| **8** | **Interval Transfer Functions** | `src/analysis/transfer.py` | Monotonic abstract transfer functions for $+$, $-$, $*$, $/$, unary $-$, and relational operators. | **In:** Operand `AbsVal`s<br>**Out:** Result `AbsVal` | Completed | Tested in `test_range_analysis.py` covering interval cross-products and zero division. |
| **9** | **Branch Refinement** | `src/analysis/refinement.py` | Path-sensitive condition refinement along True/False edges with discrete $\pm 1$ shifts and dead code detection. | **In:** Block condition & environment<br>**Out:** Refined branch environments | Completed (Review 3) | Tested in `test_branch_refinement.py`. Demonstrated with `y.2` unreachable in **Figure 12**. |
| **10** | **Range Analysis Engine** | `src/analysis/range_analysis.py` | Fixed-point Kleene iteration over CFG in reverse postorder, widening after $N$ sweeps, iterative narrowing. | **In:** `SSAProgram`<br>**Out:** Range analysis environment | Completed (Review 3) | Tested in `test_loop_narrowing.py`. Loop narrowing verified in **Figure 8** & **Figure 11**. |
| **11** | **INT8 Safety Pass** | `src/quantization/safety.py` | Verifies $[-128, 127]$ containment, integrality, phi safety, and intermediate overflow dependency blocking. | **In:** Range environment<br>**Out:** Safety verdict table | Completed (Review 3) | Tested in `test_safety_edge_cases.py`. Rejection demonstrated in **Figure 3** & **Figure 13**. |
| **12** | **Quantization Rewriter** | `src/quantization/quantizer.py` | Selectively rewrites approved instructions to `int8`, retypes temporaries, preserves unquantized types. | **In:** `SSAProgram` + verdicts<br>**Out:** Quantized SSA program | Completed | Tested in `test_quantization.py`. Side-by-side diff shown in **Figure 13**. |
| **13** | **Software Simulator** | `src/backend/simulator.py` | Dual-engine interpreter executing original vs INT8 IR with two's-complement arithmetic, checking equivalence. | **In:** SSA programs + inputs<br>**Out:** Execution trace & match | Completed | Tested in `test_pipeline.py`. Terminal match verified in **Figure 7**. |
| **14** | **Compiler Driver** | `src/pipeline.py`<br>`src/main.py` | Orchestrates all compiler passes, CLI flag parsing (`--narrow`, `--widen-after`, `--emit`), terminal emission. | **In:** CLI arguments & file<br>**Out:** Compilation result object | Completed | Verified via CLI runs (`python -m src.main examples/safe_arithmetic.qc --emit simulate`). |
| **15** | **FastAPI Server & Serializer** | `src/api/server.py`<br>`src/api/serializer.py` | In-process execution driver, structured JSON serialization of all compiler data structures, static web serving. | **In:** JSON HTTP request<br>**Out:** Structured compilation JSON | Completed (Review 3) | Tested in `test_api.py`. Powers live web application. |
| **16** | **RANGE//LAB Web Frontend** | `web/src/App.tsx`<br>`web/src/components/*` | Developer-grade visual workbench with Monaco Editor, React Flow CFG, SSA Variable Inspector drawer, 10 stage views. | **In:** User interaction & code<br>**Out:** Visual compiler feedback | Completed (Review 3) | Verified via `npm run build` (0 errors), `npm run lint` (0 errors), and **Figures 1–14**. |

---

## D. Mapping to the Review 3 Academic Report Template

> [!WARNING]
> **AUTHORITATIVE TEMPLATE STRUCTURAL DIRECTIVE — SECTION 3 OMISSION**
> The university-supplied Review 3 report template strictly defines the following sequence:
> **Section 1 $
ightarrow$ Section 2 $
ightarrow$ Section 4 $
ightarrow$ Section 5 $
ightarrow$ Section 6 $
ightarrow$ Section 7 $
ightarrow$ Section 8 $
ightarrow$ Section 9 $
ightarrow$ Appendix A**.
> The template jumps directly from Section 2 to Section 4. In accordance with university instructions, **Claude and the user must preserve this exact numbering and heading hierarchy**. Do not silently invent a Section 3 or renumber Sections 4–9. Flag this explicit template characteristic in the preface or introduction.

The following table provides the exhaustive mapping for authoring every section of the Review 3 report:

| Report Section & Title | Purpose in Academic Report | Key Supported Factual Evidence & Narrative Points | Source Files to Cite | Tests & Benchmarks to Cite | Figures to Embed | Prohibited Claims (Academic Guardrails) |
|---|---|---|---|---|---|---|
| **1. INTRODUCTION**<br>1.1 Background<br>1.2 Motivations<br>1.3 Scope of the Project | Introduce edge AI compute constraints, motivating why compiler-guided static quantization is superior to dynamic post-training calibration. Define precise scope. | - Shift of ML inference to edge microcontrollers (Zhou et al. [1], Chen & Ran [2]).<br>- Memory footprint and energy bottlenecks of FP32.<br>- Why static analysis guarantees safety under all possible paths without runtime overhead.<br>- Educational scope: mini numerical language (`.qc`), teaching compiler architecture. | `README.md`<br>`src/pipeline.py` | Review 2 context | None (Textual Introduction) | Do not claim deployment to physical edge hardware or compilation of arbitrary C++ / PyTorch models. |
| **2. PROJECT DESCRIPTION AND GOALS**<br>2.1 Literature Review<br>2.2 Research Gap<br>2.3 Objectives<br>2.4 Problem Statement | Review foundational literature on quantization and abstract interpretation. State precise research gap and formal project objectives. | - Integer arithmetic quantization (Jacob et al. [3], Krishnamoorthi [4]).<br>- Abstract interpretation foundations (Cousot & Cousot [5], [6], Bourdoncle [7], Astrée [8]).<br>- SSA IR foundations (Cytron et al. [9]).<br>- Research Gap: Most edge quantization relies on dynamic calibration or heuristic profiling; lacks sound static safety verification.<br>- Formal problem statement: Proven INT8 safety interval $[-128, 127]$. | `docs/review/Review_2_Report.pdf`<br>`README.md` | Preserved literature survey | None (Literature & Theory) | Do not fabricate citations or claim prior work failed to understand overflow; frame gap as applying formal compiler analysis to teaching-scale quantization. |
| **[TEMPLATE JUMP NOTE]** | **Structural Template Clarification** | **Explicitly note that Section 3 is omitted in the faculty template; report proceeds directly to Section 4.** | Template specification | N/A | N/A | Do not renumber Section 4 to Section 3. |
| **4. DESIGN APPROACH AND DETAILS**<br>4.1 System Architecture | Present the end-to-end multi-pass compiler architecture, intermediate representations, CFG construction, and SSA form. | - Complete 9-pass compiler pipeline.<br>- Three-Address Code lowering with temporary allocation.<br>- Basic block construction and leader identification.<br>- SSA dominator tree, dominance frontiers, and minimal φ-node placement.<br>- Architecture of the full-stack system: React 19 frontend, FastAPI server, Python compiler. | `src/ir/tac.py`<br>`src/cfg/cfg.py`<br>`src/ssa/ssa.py`<br>`src/api/server.py` | `test_tac.py`<br>`test_cfg.py`<br>`test_ssa.py` | **Figure 6** (CFG View)<br>**Figure 10** (SSA φ-Nodes View) | Do not present SSA as an optimization in itself; present it as the intermediate representation enabling clean sparse dataflow analysis. |
| **5. METHODOLOGY AND TESTING**<br>5.1 Module Description<br>5.2 Testing | Exhaustively document every compiler stage's mathematical algorithms, transfer functions, safety rules, and verification testing methodology. | - Abstract domain lattice $\mathcal{D} = \mathcal{I} 	imes \mathcal{B} 	imes \mathcal{Z}$.<br>- Monotonic interval transfer functions using exact rational `Fraction`.<br>- Path-sensitive branch condition refinement with discrete shifts.<br>- Kleene fixed-point iteration, widening ($
abla$), and sound narrowing ($\Delta$).<br>- INT8 safety rules and intermediate overflow blocking.<br>- Software simulator dual execution semantics.<br>- Unit testing (138 tests) and reproducible evaluation methodology. | `src/analysis/abstract_value.py`<br>`src/analysis/transfer.py`<br>`src/analysis/refinement.py`<br>`src/analysis/range_analysis.py`<br>`src/quantization/safety.py`<br>`src/backend/simulator.py` | `python -m unittest discover`<br>`tests/analysis/` | **Figure 2** (INT8 Safety)<br>**Figure 7** (Simulator)<br>**Figure 8** (Loop Narrowing)<br>**Figure 9** (Lexer/AST)<br>**Figure 11** (Ranges Table)<br>**Figure 13** (Quantized IR Diff)<br>**Figure 14** (Terminal Tests) | Do not claim simulator equivalence is a universal formal proof; it validates executed test inputs. Do not claim floating-point division is quantized. |
| **6. PROJECT DEMONSTRATION – Implementations** | Demonstrate the operational web workbench (RANGE//LAB), Monaco editor, pipeline stage navigation, and interactive SSA inspection. | - Practical implementation walkthrough using RANGE//LAB.<br>- Monaco editor integration with real-time error reporting.<br>- Visual CFG inspection with color-coded branch predicates.<br>- Interactive SSA Variable Inspector drawer: inspecting $z.1$, examining intervals and operands.<br>- In-place Def-Use chain traversal: navigating from $z.1$ to operand $x.1$. | `web/src/App.tsx`<br>`web/src/components/SSAVarInspector.tsx`<br>`web/src/components/EditorPanel.tsx` | Live workbench testing<br>`npm run build` | **Figure 1** (Main Workbench)<br>**Figure 4** (SSA Inspector $z.1$)<br>**Figure 5** (Operand Traversal $x.1$) | Do not describe the web UI as the quantization compiler; it is the interactive presentation layer for the Python compiler engine. |
| **7. RESULT AND DISCUSSION** | Present empirical evaluation results across the 12 curated benchmarks, analyzing quantization ratios, safety guarantees, and edge cases. | - Comprehensive 12-benchmark evaluation table (54 SSA variables).<br>- Quantization yield: 35 safe (64.8%), 32 quantized to INT8 (59.3%), 3 blocked, 19 rejected (35.2%).<br>- 100% simulation equivalence rate across all benchmarks.<br>- 0 safety violations (absolute conservative safety guarantee preserved).<br>- Deep-dive analysis of overflow rejection, non-integral float rejection, intermediate blocking, and branch refinement dead-code detection.<br>- Theoretical storage reduction analysis ($44.4\%$). | `evaluate.py`<br>`tests/evaluation.py`<br>`examples/*.qc` | `python evaluate.py` terminal output | **Figure 3** (Overflow Rejection)<br>**Figure 12** (Branch Refinement Unreachable) | Do not claim physical memory bandwidth or execution time speedups; report static width reduction and simulation fidelity. |
| **8. CONCLUSION AND FUTURE ENHANCEMENTS** | Conclude the project findings, summarize contributions to compiler design education, and articulate realistic future work. | - Summary of achievements: sound static analysis successfully drives INT8 quantization in an SSA compiler.<br>- Pedagogical contribution: RANGE//LAB provides visual insight into compiler phases.<br>- Future enhancements: multidimensional array range analysis, automated affine loop unrolling, fixed-point scale factor synthesis, and LLVM IR emission. | `README.md` | Full project verification | None (Conclusion Narrative) | Do not present future work as already completed. |
| **9. REFERENCES** | Provide complete, verified academic citations. | - Preserved citations [1]–[12] from Review 2 report covering edge computing, neural quantization, abstract interpretation, Astrée, SSA form, LLVM, Halide, and TVM. | Review 2 baseline bibliography | Academic literature | None (Bibliography) | Do not fabricate citation details, DOIs, or page numbers. |
| **APPENDIX A – SAMPLE CODE** | Provide authentic sample `.qc` programs illustrating compiler behavior across key scenarios. | - Curated collection of 7 authentic `.qc` benchmark programs from `examples/` demonstrating safe arithmetic, overflow rejection, non-integral rejection, conditional branching, branch refinement, loop narrowing, and unsupported operations. | `examples/*.qc` | Repository source files | Code listings with explanatory commentary | Do not invent synthetic sample code; use actual repository files. |

---

## E. Review 2 Continuity, Evolution, and Delta Analysis

To ensure seamless continuity between the Review 2 report and the final Review 3 report, the following comparison matrix details the baseline state versus the newly implemented functionality:

| Dimension / Component | Review 2 Baseline State (Documented Milestone) | Review 3 Completed Implementation (Current State) | Academic Narrative & Significance |
|---|---|---|---|
| **Branch Condition Analysis** | Flow-insensitive; branch conditions controlled execution branching but did not refine operand intervals along branch edges. | **Path-sensitive branch condition refinement (`src/analysis/refinement.py`):** Refines variable intervals along True and False edges with discrete $\pm 1$ shifts and detects contradictory unreachable paths ($ot$). | Bridges a classic gap in static analysis, eliminating false positives in conditionals and enabling static dead-code detection. |
| **Loop Analysis & Precision** | Basic Kleene iteration with widening after $N$ sweeps; loops with increments widened to $[0, +\infty)$ (UNKNOWN) and were rejected. | **Sound iterative narrowing (`src/analysis/range_analysis.py`):** Iteratively intersects widened intervals with loop exit conditions, tightening bounded loop counters to exact safe intervals (e.g. $[0, 10]$). | Solves over-approximation in cyclic control flow, allowing bounded loops to be quantized to INT8 safely. |
| **Quantization Safety Rules** | Checked isolated variable bounds and integrality; did not track whether intermediate sub-expressions overflowed. | **Intermediate overflow dependency tracking (`src/quantization/safety.py`):** Blocks quantization of an expression if any upstream intermediate calculation could have overflowed. | Prevents silent wrap-around errors where an intermediate overflows but a subsequent operation lands back within $[-128, 127]$. |
| **Compiler Verification** | Initial test harness with approximately 20 active tests; preliminary test files under construction. | **138 unit and integration tests** passing with 100% success rate in 0.338s; full coverage of lexer, parser, TAC, CFG, SSA, ranges, safety, and API. | Validates complete industrial test-driven compiler engineering. |
| **Evaluation Suite** | Preliminary manual CLI runs on isolated example files. | **Automated reproducible evaluation harness (`evaluate.py`)** running 12 formal benchmarks with 54 SSA variables, tracking equivalence and safety violations. | Provides empirical, reproducible benchmark metrics for the final academic report. |
| **User Interface & Tooling** | None; compiler operated solely via command-line flags (`python -m src.main`). | **RANGE//LAB Interactive Workbench (`web/`):** Full-stack web application with Monaco Editor, React Flow CFG visualizer, SSA Variable Inspector drawer, and 10 stage viewers. | Transforms the compiler into an interactive educational laboratory for Compiler Design demonstrations. |
| **Backend Integration** | Standalone Python module invocations. | **FastAPI in-process REST API server (`src/api/server.py`)** with comprehensive JSON serializer (`src/api/serializer.py`). | Enables modular microservice architecture decoupling compiler analysis from visual presentation. |
| **Historical Review Documentation** | Files in `docs/review/` represented Review 1 and Review 2 reports. | **100% preserved:** All historical files in `docs/review/` remain unaltered; Review 3 deliverables placed in dedicated `docs/review3/`. | Preserves academic audit trail and project history integrity. |

---

## F. In-Depth Methodology & Compiler Implementation Details

### F.1 Source Language Grammar & Type System
The compiler accepts mini numerical programs written in a C-like imperative syntax (`.qc`). The formal grammar in EBNF notation is defined as:

```ebnf
Program         ::= Statement*
Statement       ::= VarDecl | Assignment | IfStmt | WhileStmt | PrintStmt
VarDecl         ::= Type Identifier ("=" Expr)? ";"
Assignment      ::= Identifier "=" Expr ";"
IfStmt          ::= "if" "(" Expr ")" Block ("else" Block)?
WhileStmt       ::= "while" "(" Expr ")" Block
PrintStmt       ::= "print" Expr ";"
Block           ::= "{" Statement* "}"

Type            ::= "int" | "float" | "bool" | "int8"
Expr            ::= LogicalOr
LogicalOr       ::= LogicalAnd ("||" LogicalAnd)*
LogicalAnd      ::= Equality ("&&" Equality)*
Equality        ::= Relational (("==" | "!=") Relational)*
Relational      ::= Additive (("<" | "<=" | ">" | ">=") Additive)*
Additive        ::= Multiplicative (("+" | "-") Multiplicative)*
Multiplicative  ::= Unary (("*" | "/") Unary)*
Unary           ::= ("-" | "!") Unary | Primary
Primary         ::= Identifier | IntLiteral | FloatLiteral | BoolLiteral | "(" Expr ")"
```

### F.2 Abstract Value Domain Lattice ($\mathcal{D}$)
The abstract value domain represents the set of possible runtime values of an SSA variable as a mathematical lattice:
$$\mathcal{D} = \mathcal{I} 	imes \mathcal{B} 	imes \mathcal{Z}$$
where:
- $\mathcal{I} = \{ [l, u] \mid l, u \in \mathbb{Q} \cup \{-\infty, +\infty\}, l \le u \} \cup \{ ot \}$ represents the interval domain over rational numbers ($	ext{Fraction}$). Using exact rational arithmetic eliminates floating-point rounding errors during static analysis.
- $\mathcal{B} = \{ 	ext{True}, 	ext{False} \}$ represents the integrality property (`integral`). An interval is integral ($	ext{integral}=	ext{True}$) if and only if every runtime value on every execution path is guaranteed to be an integer.
- $\mathcal{Z} = \{ 	ext{True}, 	ext{False} \}$ represents the division-by-zero diagnostic flag (`div_zero`).
- $ot$ (Bottom) represents unreachable code paths or contradictory branch conditions.
- $	op$ (Top / UNKNOWN) represents $[-\infty, +\infty]$ with $	ext{integral}=	ext{False}$.

### F.3 Abstract Transfer Functions
For abstract values $X = [a, b]$ and $Y = [c, d]$:
- **Addition ($+$):**
  $$[a, b] + [c, d] = [a + c, b + d], \quad 	ext{integral} = X.	ext{integral} \land Y.	ext{integral}$$
- **Subtraction ($-$):**
  $$[a, b] - [c, d] = [a - d, b - c], \quad 	ext{integral} = X.	ext{integral} \land Y.	ext{integral}$$
- **Multiplication ($*$):**
  $$[a, b] * [c, d] = [\min(ac, ad, bc, bd), \max(ac, ad, bc, bd)], \quad 	ext{integral} = X.	ext{integral} \land Y.	ext{integral}$$
- **Division ($/$):**
  If $0 \in [c, d]$, the operation flags `div_zero=True` and yields UNKNOWN. If $0
otin [c, d]$, the interval is computed over the four quotient combinations. Division is conservatively non-integral ($	ext{integral}=	ext{False}$).
- **Unary Negation ($-$):**
  $$-[a, b] = [-b, -a], \quad 	ext{integral} = X.	ext{integral}$$
- **Relational Comparisons ($<, \le, >, \ge, ==, !=$):**
  Evaluates to $[1, 1]$ if the relation holds strictly for all points in the intervals, $[0, 0]$ if disjoint in the opposite direction, or $[0, 1]$ with $	ext{Type.BOOL}$ if overlapping.

### F.4 Path-Sensitive Branch Condition Refinement
When a basic block terminates with a conditional jump `CondJump(cond, true_lbl, false_lbl)`:
1. **True Branch Refinement:** Refines variables assuming `cond` is True. For integer comparisons against a constant $c$:
   - $x < c \implies x \in 	ext{env}[x] \sqcap [-\infty, c - 1]$
   - $x \le c \implies x \in 	ext{env}[x] \sqcap [-\infty, c]$
   - $x > c \implies x \in 	ext{env}[x] \sqcap [c + 1, +\infty]$
   - $x \ge c \implies x \in 	ext{env}[x] \sqcap [c, +\infty]$
   - $x == c \implies x \in 	ext{env}[x] \sqcap [c, c]$
2. **False Branch Refinement:** Negates the condition and refines along the fallthrough/false edge. For example, $
eg(x \ge 10) \implies x < 10 \implies x \in 	ext{env}[x] \sqcap [-\infty, 9]$.
3. **Unreachable Path Detection ($ot$):** If the intersection $	ext{env}[x] \sqcap 	ext{constraint}$ yields an empty interval, the branch environment is marked $ot$ (`unreachable=True`). Basic blocks along this path are identified as dead code.

### F.5 Loop Widening and Sound Narrowing
To guarantee fixed-point termination over cyclic CFGs:
1. **Widening ($
abla$):** If a loop header φ-node interval continues expanding after $N$ iterations (default `--widen-after 3`):
   $$[l_1, u_1]
abla [l_2, u_2] = \left[ (l_2 < l_1 ? -\infty : l_1), \; (u_2 > u_1 ? +\infty : u_1)
ight]$$
2. **Narrowing ($\Delta$):** After widening converges, enabling `--narrow` executes narrowing iterations. The loop exit condition constraint (e.g. $i < 10$) is intersected with the loop back-edge value:
   $$[l_1, u_1] \Delta [l_2, u_2] = \left[ (l_1 = -\infty ? l_2 : l_1), \; (u_1 = +\infty ? u_2 : u_1)
ight]$$
   This successfully recovers the tight bound $[0, 10]$ for bounded loop counters.

### F.6 INT8 Quantization Eligibility Rules
An SSA variable $v$ is approved for INT8 quantization ($	ext{SAFE}
ightarrow 	ext{int8}$) **if and only if all six** criteria hold:
1. **Boundary Containment:** $	ext{inferred\_interval}(v) \subseteq [-128, 127]$. Exact boundaries $-128$ and $127$ are safe if integral.
2. **Mathematical Integrality:** $v.	ext{integral} == 	ext{True}$. Floating-point variables and division results are rejected.
3. **No Division-by-Zero Risk:** $v.	ext{div\_zero} == 	ext{False}$.
4. **Intermediate Dependency Tracking:** Every operand and upstream intermediate computation leading to $v$ must also be INT8-safe.
5. **Phi Inflow Safety:** For φ-nodes, every incoming alternative from reachable predecessor blocks must be INT8-safe.
6. **Supported Rewriting Operation:** Instruction operator must be copy, phi, $+$, $-$, $*$, or unary $-$. Division and comparisons remain in original representation.

---

## G. Verified Test Suite, Evaluation Metrics & Empirical Results

### G.1 Exact Test Execution Log
Executing the full compiler test suite via Python's standard `unittest` framework:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
**Execution Outcome:**
- **Status:** `OK` (Exit Code 0)
- **Total Tests Executed:** **138 tests**
- **Passed:** **138 tests (100%)**
- **Failures:** **0**
- **Errors:** **0**
- **Execution Time:** **0.291 seconds**
- **Coverage (17 Test Modules):** 	est_lexer.py (15 tests), 	est_parser.py (14 tests), 	est_ast.py (7 tests), 	est_semantic.py (6 tests), 	est_tac.py (11 tests), 	est_cfg.py (9 tests), 	est_ssa.py (15 tests), 	est_analysis.py (8 tests), 	est_range_analysis.py (16 tests), 	est_branch_refinement.py (14 tests), 	est_loop_narrowing.py (6 tests), 	est_safety_edge_cases.py (11 tests), 	est_quantization.py (5 tests), 	est_boolean_comparisons.py (3 tests), 	est_simulator.py (4 tests), 	est_pipeline.py (7 tests), 	est_api.py (6 tests).

### G.2 Reproducible Benchmark Evaluation Results
Executing the standardized evaluation harness:
```bash
python evaluate.py
```
**Empirical Benchmark Table (Exact Command Output):**

| Benchmark Program | SSA Vars | Safe Vars | INT8 Vars | Blocked | Rejected | Sim Equivalence | Safety Invariant |
|---|---|---|---|---|---|---|---|
| `safe_arithmetic.qc` | 3 | 3 | 3 | 0 | 0 | **MATCH** | **PASS (0 violations)** |
| `overflow_rejection.qc` | 3 | 2 | 2 | 0 | 1 | **MATCH** | **PASS (0 violations)** |
| `non_integral_rejection.qc` | 3 | 0 | 0 | 0 | 3 | **MATCH** | **PASS (0 violations)** |
| `if_else_phi.qc` | 7 | 5 | 4 | 1 | 2 | **MATCH** | **PASS (0 violations)** |
| `while_loop_widening.qc` | 7 | 2 | 2 | 0 | 5 | **MATCH** | **PASS (0 violations)** |
| `bounded_loop_counter.qc` | 4 | 3 | 3 | 0 | 1 | **MATCH** | **PASS (0 violations)** |
| `stabilizing_loop.qc` | 7 | 4 | 4 | 0 | 3 | **MATCH** | **PASS (0 violations)** |
| `branch_refinement.qc` | 6 | 4 | 3 | 1 | 2 | **MATCH** | **PASS (0 violations)** |
| `intermediate_overflow.qc` | 4 | 3 | 2 | 1 | 1 | **MATCH** | **PASS (0 violations)** |
| `boundary_fit_exact.qc` | 2 | 2 | 2 | 0 | 0 | **MATCH** | **PASS (0 violations)** |
| `unsupported_op_rejection.qc` | 3 | 2 | 2 | 0 | 1 | **MATCH** | **PASS (0 violations)** |
| `edge_linear_transform.qc` | 5 | 5 | 5 | 0 | 0 | **MATCH** | **PASS (0 violations)** |
| **TOTALS / SUMMARY** | **54** | **35 (64.8%)** | **32 (59.3%)** | **3 (5.6%)** | **19 (35.2%)** | **100.0% MATCH** | **0 (No safety violations observed across these 12 evaluated benchmarks)** |

### G.3 Theoretical Storage-Width Reduction Derivation
For the 54 SSA variables analyzed across the benchmark suite:
- Total original representation width: $54 	ext{ variables} 	imes 32 	ext{ bits} = 1,728 	ext{ bits}$.
- 32 variables are safely rewritten to 8-bit `int8`, saving $32 - 8 = 24 	ext{ bits}$ each:
  $$	ext{Bits Saved} = 32 	imes 24 = 768 	ext{ bits}$$
- 22 variables remain in their original 32-bit representation (3 blocked intermediates + 19 rejected).
- Post-quantization total storage: $(32 	imes 8) + (22 	imes 32) = 256 + 704 = 960 	ext{ bits}$.
- **Theoretical Representation-Width Reduction:**
  $$	ext{Reduction} = rac{1,728 - 960}{1,728} = rac{768}{1,728} pprox \mathbf{44.44\%}$$

> [!NOTE]
> This $44.44\%$ saving represents a static intermediate representation storage-width reduction. It does not imply a $44.4\%$ execution speedup or memory latency improvement on physical hardware.

---

## H. Screenshot Evidence & Figure Integration Schedule

The complete visual evidence catalog contains 14 authentic screenshots (`artifacts/screenshots/`), mapped to the Review 3 report as follows:

| Figure # | Target Report Section | Title & Visual Feature | Dimensions | Key Architectural / Analytical Claim Verified |
|---|---|---|---|---|
| **Figure 1** | **Section 6** | RANGE//LAB Integrated Workbench Desktop Interface (Range Analysis View) | 2244 × 1239 px | Full full-stack workbench integration displaying the Range Analysis stage on safe_arithmetic.qc (Monaco editor, 10-stage pipeline navigation bar, results panel with range table). |
| **Figure 2** | **Section 5.1** | INT8 Safety Analysis & Inferred Interval Comparison | 2244 × 1209 px | Inferred intervals for `x.1 [10, 10]`, `y.1 [20, 20]`, `z.1 [30, 30]` safely in $[-128, 127]$ with `SAFE -> int8` badges and 0 errors. |
| **Figure 3** | **Section 7.2** | Direct Overflow Rejection & Type Preservation | 2244 × 1209 px | Sound rejection of positive overflow $z.1 = [130, 130] > 127$ (from $x=100, y=30$) with red `REJECT` badge and 32-bit `int` preservation. |
| **Figure 4** | **Section 6** | Interactive SSA Variable Inspector Drawer for $z.1$ | 2244 × 1209 px | Interactive SSA Inspector side-drawer for variable $z.1$: defining instruction $z.1 = x.1 + y.1$, basic block $B1$, inferred interval $[30, 30]$, integral=yes, verdict `SAFE -> int8`, and downstream use in `print z.1`. |
| **Figure 5** | **Section 6** | In-Place Operand Navigation & Use Traversal for $x.1$ | 2241 × 1199 px | In-place Def-Use operand traversal: clicking operand $x.1$ updates drawer to definition $x.1 = 10$, basic block $B1$, interval $[10, 10]$, and downstream use in $z.1 = x.1 + y.1$. |
| **Figure 6** | **Section 4.1** | Interactive Control-Flow Graph (CFG) Visualization | 2244 × 1209 px | Basic block partitioning ($B0 \dots B3$), leader splitting, conditional branch edges, and merge point for `if_else_phi.qc`. |
| **Figure 7** | **Section 5.2** | Dual-Engine Simulator Execution & Equivalence | 2241 × 1199 px | Side-by-side original vs quantized execution matching outputs ('30') with `SIMULATION EQUIVALENT (MATCH)` banner. |
| **Figure 8** | **Section 5.1** | Bounded Loop Analysis with Sound Iterative Narrowing | 2241 × 1199 px | Bounded loop analysis under `--narrow`: widening expands loop counter $i.2$ to $	ext{UNKNOWN} ([-\infty, +\infty])$, while iterative narrowing contracts $i.2$ to $[0, 10]$ and $i.3$ to $[1, 10]$, enabling `SAFE -> int8`. |
| **Figure 9** | **Section 5.1** | Lexer Token Stream & Hierarchical AST View | 2244 × 1286 px | Token stream count (23 tokens) and hierarchical collapsible AST tree with source coordinates. |
| **Figure 10** | **Section 4.1** | TAC & SSA Representation with φ-Node Resolution | 2244 × 1286 px | SSA φ-node table mapping predecessor basic blocks ($B1: max.1, B2: max.0$) for $max.2$. |
| **Figure 11** | **Section 5.1** | Static Range Analysis Table & Convergence Metrics | 2244 × 1286 px | Tabular interval presentation, integrality flags, filter pills, and sweep convergence counter (`6 sweeps (converged=true)`). |
| **Figure 12** | **Section 7.3** | Branch Condition Refinement & Unreachable Path Detection | 2244 × 1286 px | Refined True branch interval $[10, 10]$ and static unreachable False branch marked with red `UNREACHABLE` badge on $y.2$. |
| **Figure 13** | **Section 5.1** | Quantized IR Side-by-Side Diff & Intermediate Blocking | 2244 × 1286 px | Side-by-side IR diff showing rewritten vars ($a.1, b.1$), overflow ($c.1 = 150 > 127$), and blocked var ($d.1 = [100, 100]$) due to unsafe operand $c.1$. |
| **Figure 14** | **Section 5.2** | Automated Unit Test Suite & Evaluation Terminal | 2244 × 1286 px | Real terminal execution: 138 unit tests passing (`OK` in 0.511s on capture, 0.291s in current run) and 12 benchmarks passing (`ALL PASS`, 54 SSA vars, 0 violations, 100% equivalence, 44.4% width reduction). |

---

## I. Technical Boundaries, Real Limitations & Future Enhancements

### I.1 Explicit Compiler Limitations
1. **Scalar Arithmetic Focus:** Analysis operates strictly on scalar `int` and `float` variables. It does not support multidimensional arrays, pointers, struct aggregate types, or dynamic heap allocations.
2. **Non-Relational Abstract Domain:** The interval domain $\mathcal{I}$ tracks independent variable bounds $[l, u]$. It does not maintain relational linear equalities (e.g. Octagon or Polyhedral domains tracking $x - y \le k$).
3. **Conservative Unbounded Loops:** Loops lacking bounding exit conditions (e.g. unbounded accumulators `sum = sum + x`) widen to $[-\infty, +\infty]$ and are soundly preserved in 32-bit representation.
4. **Non-Integral Division:** Integer division results are treated as non-integral ($	ext{integral}=	ext{False}$) to avoid fractional rounding corruption without explicit modulus checks.
5. **No Hardware Code Generation:** The compiler backend terminates in interpreted SSA simulation; it does not emit ARM Cortex-M / RISC-V assembly or machine object files.

### I.2 Roadmap of Future Enhancements
- **Multi-Dimensional Array Range Analysis:** Extending interval analysis to array index expressions to eliminate runtime buffer overflow checks.
- **Affine Loop Unrolling & Polyhedral Scheduling:** Performing loop tiling and loop unrolling prior to range analysis to expose wider scalar quantization opportunities.
- **Fixed-Point Quantization Synthesis:** Automatically synthesizing fractional scaling factors ($S$) and zero-points ($Z$) for non-integral float values ($q = 	ext{round}(x / S) + Z$).
- **Native LLVM IR Code Generation:** Emitting target-independent LLVM IR with `i8` integer types and compiling to bare-metal microcontrollers via Clang/LLVM.

---

## J. Preserved Bibliography, References & Citation Guidance

The following 12 academic references are preserved directly from the historical Review 2 baseline document. When authoring the Review 3 report, Claude must cite these specific sources to support the technical foundations:

- **[1] Z. Zhou, X. Chen, E. Li, L. Zeng, K. Luo, and J. Zhang**, "Edge intelligence: Paving the last mile of artificial intelligence with edge computing," *Proceedings of the IEEE*, vol. 107, no. 8, pp. 1738–1762, Aug. 2019.
  *Context in Report:* Supports Section 1.1 (Background on edge AI compute and memory bottlenecks).
- **[2] J. Chen and X. Ran**, "Deep learning with edge computing: A review," *Proceedings of the IEEE*, vol. 107, no. 8, pp. 1655–1674, Aug. 2019.
  *Context in Report:* Supports Section 1.1 and Section 2.1 (Survey of edge resource constraints).
- **[3] B. Jacob, S. Kligys, B. Chen, M. Zhu, M. Tang, A. Howard, H. Adam, and D. Kalenichenko**, "Quantization and training of neural networks for efficient integer-arithmetic-only inference," in *Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR)*, 2018, pp. 2704–2713.
  *Context in Report:* Supports Section 1.2 and Section 2.1 (Integer-only quantization principles and 8-bit arithmetic).
- **[4] R. Krishnamoorthi**, "Quantizing deep convolutional networks for efficient inference: A whitepaper," *arXiv preprint arXiv:1806.08342*, 2018.
  *Context in Report:* Supports Section 2.1 and Section 2.2 (Quantization noise, overflow risks, and calibration trade-offs).
- **[5] P. Cousot and R. Cousot**, "Static determination of dynamic properties of programs," in *Proc. 2nd Int. Symp. on Programming (ISOP)*, Paris, France: Dunod, 1976, pp. 106–130.
  *Context in Report:* Supports Section 2.1 and Section 5.1 (Classical interval analysis foundations).
- **[6] P. Cousot and R. Cousot**, "Abstract interpretation: A unified lattice model for static analysis of programs by construction or approximation of fixpoints," in *Proc. 4th ACM SIGACT-SIGPLAN Symp. on Principles of Programming Languages (POPL)*, 1977, pp. 238–252.
  *Context in Report:* Supports Section 2.1, Section 4.1, and Section 5.1 (Lattice theory, Galois connections, and fixed-point approximation).
- **[7] F. Bourdoncle**, "Efficient chaotic iteration strategies with widenings," in *Formal Methods in Programming and Their Applications*, LNCS vol. 735. Berlin, Germany: Springer, 1993, pp. 128–141.
  *Context in Report:* Supports Section 5.1 (Kleene iteration and widening convergence strategies).
- **[8] B. Blanchet, P. Cousot, R. Cousot, J. Feret, L. Mauborgne, A. Miné, D. Monniaux, and X. Rival**, "A static analyzer for large safety-critical software," in *Proc. ACM SIGPLAN Conf. on Programming Language Design and Implementation (PLDI)*, 2003, pp. 196–207.
  *Context in Report:* Supports Section 2.1 and Section 5.1 (Industrial-scale static analysis and Astrée analyzer principles).
- **[9] R. Cytron, J. Ferrante, B. K. Rosen, M. N. Wegman, and F. K. Zadeck**, "Efficiently computing static single assignment form and the control dependence graph," *ACM Trans. Program. Lang. Syst.*, vol. 13, no. 4, pp. 451–490, Oct. 1991.
  *Context in Report:* Supports Section 4.1 and Section 5.1 (Dominance frontiers and minimal SSA φ-node placement algorithms).
- **[10] C. Lattner and V. Adve**, "LLVM: A compilation framework for lifelong program analysis and transformation," in *Proc. Int. Symp. on Code Generation and Optimization (CGO)*, 2004, pp. 75–86.
  *Context in Report:* Supports Section 2.1 and Section 4.1 (Modern intermediate representation design and optimization passes).
- **[11] J. Ragan-Kelley, C. Barnes, A. Adams, S. Paris, F. Durand, and S. Amarasinghe**, "Halide: A language and compiler for optimizing parallelism, locality, and recomputation in image processing pipelines," in *Proc. ACM SIGPLAN Conf. on Programming Language Design and Implementation (PLDI)*, 2013, pp. 519–530.
  *Context in Report:* Supports Section 2.1 (Domain-specific numerical compilers and schedule-algorithm decoupling).
- **[12] T. Chen, T. Moreau, Z. Jiang, L. Zheng, E. Yan, M. Cowan, H. Shen, L. Wang, Y. Hu, L. Ceze, C. Guestrin, and A. Krishnamurthy**, "TVM: An automated end-to-end optimizing compiler for deep learning," in *Proc. 13th USENIX Symp. on Operating Systems Design and Implementation (OSDI)*, 2018, pp. 578–594.
  *Context in Report:* Supports Section 2.1 (Deep learning compilers and graph-to-tensor lowering pipelines).

---

## K. Appendix A — Curated Sample Programs (.qc)

The following 7 programs are genuine files located in the `examples/` directory of the repository:

### Program 1: Provably Safe Arithmetic (`examples/safe_arithmetic.qc`)
- **Source Code:**
  ```c
  int x = 10;
  int y = 20;
  int z = x + y;
  print z;
  ```
- **Analysis & Result:** Statically infers $x.1 \in [10, 10]$, $y.1 \in [20, 20]$, and $z.1 \in [30, 30]$. All values are integral and contained in $[-128, 127]$. Rewritten to `int8`. Verified equivalence in **Figure 2** & **Figure 7**.

### Program 2: Direct Overflow Rejection (`examples/overflow_rejection.qc`)
- **Source Code:**
  ```c
  int x = 100;
  int y = 30;
  int z = x + y;
  print z;
  ```
- **Analysis & Result:** Infers $z.1 \in [130, 130]$. Since $130 > 127$, INT8 safety fails. $z.1$ is marked `REJECT` and preserved in original 32-bit `int`. Verified in **Figure 3**.

### Program 3: Non-Integral Float Rejection (`examples/non_integral_rejection.qc`)
- **Source Code:**
  ```c
  float x = 10.0;
  float y = 3.5;
  float z = x + y;
  print z;
  ```
- **Analysis & Result:** Floating-point constants set `integral=False`. Value $z.1 \in [13.5, 13.5]$ is within $[-128, 127]$ numerically but rejected due to non-integrality to preserve decimal precision.

### Program 4: Control Flow and φ-Node Merging (`examples/if_else_phi.qc`)
- **Source Code:**
  ```c
  int x = 10;
  int y = 20;
  int max = 0;
  if (x > y) {
      max = x;
  } else {
      max = y;
  }
  print max;
  ```
- **Analysis & Result:** Demonstrates CFG branch splitting into blocks $B1$ and $B2$, with φ-node placement at join block $B3$: `max.2 = phi(B1: max.1, B2: max.0)`. Verified in **Figure 6** & **Figure 10**.

### Program 5: Path-Sensitive Branch Refinement (`examples/branch_refine.qc`)
- **Source Code:**
  ```c
  int x = 15;
  int y = 0;
  if (x >= 10) {
      y = x - 5;
  } else {
      y = x + 5;
  }
  print y;
  ```
- **Analysis & Result:** Path-sensitive refinement refines True branch to $[10, 10]$ ($y.3$). The False branch condition $x < 10$ intersects with $[15, 15]$ to produce $ot$. Variable $y.2$ is proven `UNREACHABLE`. Verified in **Figure 12**.

### Program 6: Bounded Loop with Sound Narrowing (`examples/bounded_loop.qc`)
- **Source Code:**
  ```c
  int i = 0;
  while (i < 10) {
      i = i + 1;
  }
  print i;
  ```
- **Analysis & Result:** Kleene iteration widens loop counter, and subsequent narrowing iterations apply condition $i < 10$, successfully recovering bounded range $[0, 10]$. Variable $i$ is quantized to `int8`. Verified in **Figure 8**.

### Program 7: Unsupported Operation Rejection (`examples/unsupported_division.qc`)
- **Source Code:**
  ```c
  int a = 20;
  int b = 4;
  float c = a / b;
  print c;
  ```
- **Analysis & Result:** Division operator is treated as non-integral. Operands $a$ and $b$ are quantized to `int8`, while quotient $c$ is safely kept in its original type.

---

## L. Fact and Claim Verification Traceability Matrix

The following matrix connects every major factual claim to be made in the final Review 3 report with its verifying source code, automated test evidence, and visual screenshot:

| # | Specific Technical Claim | Verifying Source Code File | Verification Command / Evidence | Visual Figure | Academic Limitation / Scope Constraint |
|---|---|---|---|---|---|
| **1** | Inclusive signed INT8 boundary $[-128, 127]$ is strictly enforced. | `src/quantization/safety.py` | `test_safety_edge_cases.py` (passes -128, 127; rejects -129, 128) | Figure 2 | Valid for proven integral values only. |
| **2** | Intermediate overflow blocks downstream quantization. | `src/quantization/safety.py` | `test_intermediate_overflow_blocks_quantization` in `test_quantization.py` | Figure 13 | Applies along def-use chains; no algebraic re-association. |
| **3** | Non-integral floating-point computations are soundly rejected. | `src/analysis/abstract_value.py` | `test_non_integral_float_rejected` in `test_quantization.py` | Benchmark table | Preserves fractional numerical semantics without scaling. |
| **4** | Division by zero is detected statically and yields UNKNOWN. | `src/analysis/transfer.py` | `test_division_by_zero_rejected` in `test_quantization.py` | Benchmark table | Triggers diagnostic flag `div_zero=True`. |
| **5** | Path-sensitive branch refinement detects unreachable code. | `src/analysis/refinement.py` | `test_branch_refinement.py` (verifies $ot$ intersection) | Figure 12 | Linear relational branch predicates only. |
| **6** | Sound loop narrowing recovers bounded intervals. | `src/analysis/range_analysis.py` | `test_loop_narrowing.py` (converges to $[0, 10]$) | Figure 8 | Requires monotone bounded loop condition. |
| **7** | Full test suite achieves 100% pass rate across 138 unit tests. | `tests/` (all subdirectories) | `python -m unittest discover -s tests -p "test_*.py" -v` | Figure 14 | 138 tests pass in ~0.35s. |
| **8** | Reproducible evaluation yields 100% simulation equivalence. | `evaluate.py`<br>`tests/evaluation.py` | `python evaluate.py` (12 benchmarks evaluated) | Figure 14 | Validates functional equivalence on executed inputs. |
| **9** | No safety violations observed across all 54 evaluated variables. | `evaluate.py`<br>`tests/evaluation.py` | `python evaluate.py` (0 safety violations observed) | Figure 14 | Empirical test result on the 12 benchmarks demonstrating conservative safety rules; not a universal formal proof. |
| **10** | Theoretical static storage-width reduction is $44.4\%$. | `evaluate.py` | Derived mathematically: $(32 	imes 24) / (54 	imes 32) = 44.44\%$ | Benchmark summary | Intermediate representation width only; not hardware speedup. |
| **11** | Minimal SSA φ-nodes placed using dominance frontiers. | `src/ssa/construction.py`<br>`src/ssa/verify.py` | `test_ssa_dominance_frontiers_computed` in `test_ssa.py` | Figure 10 | Implements Cytron et al. minimal SSA algorithm. |
| **12** | Basic blocks correctly split at leaders. | `src/cfg/cfg.py` | `test_cfg.py` | Figure 6 | Partitioned into entry, branch, and join blocks. |
| **13** | Dual simulator executes 8-bit two's-complement arithmetic. | `src/backend/simulator.py` | `test_pipeline.py` (verifies wrap-around emulation) | Figure 7 | In-memory interpreter for validation. |
| **14** | Web application provides interactive in-place SSA inspection. | `web/src/components/SSAVarInspector.tsx` | Visual verification in live browser session | Figure 4 & Figure 5 | In-place drawer navigation along def-use chains. |
| **15** | Frontend builds with 0 errors via standard toolchain. | `web/package.json`<br>`web/vite.config.ts` | `cd web && npm run build` (Vite v5.4.19, 0 errors, 2.74s) | Terminal evidence | Production bundle built cleanly. |
| **16** | Historical Review 2 documentation is 100% preserved. | `docs/review/` | `git status docs/review/` (all 5 original files intact) | Git audit | Historical audit trail preserved. |
