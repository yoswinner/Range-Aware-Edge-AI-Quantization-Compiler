# RANGE//LAB — Visual Application Screenshot Catalog

**Course:** BCSE307L — Compiler Design
**Project Title:** Range-Aware Edge AI Quantization Compiler
**Web Application:** RANGE//LAB — INT8 Quantization Workbench
**Institution:** Vellore Institute of Technology, Vellore
**Programme:** B.Tech. Computer Science and Engineering
**Team Members:** Yash Pradhan (24BCE0702), Anjini Pandey (24BCE0714), Ishita Srivastava (24BDS0234)
**Faculty Guide:** Prof. Kanagaraj R.
**Date:** October 2026

---

## Overview and Document Purpose

This catalog provides a verified inventory and visual reference for all 14 authentic application screenshots captured directly from the live **RANGE//LAB — INT8 Quantization Workbench** and its compiler execution pipeline. Every screenshot corresponds to a real, functioning state of the compiler and frontend, operating on genuine `.qc` test programs. This document serves as the photographic evidence base for the **Review 3 Final Project Report**, mapping each figure to its recommended report section with academic captions, technical descriptions, and explicit analytical boundaries.

---

## Figure Index & Report Placement Mapping

| Figure | Title | Relevant Stage / Example | Recommended Report Placement | File Size | Dimensions |
|---|---|---|---|---|---|
| **Figure 1** | RANGE//LAB Integrated Workbench Desktop Interface | Full Application / Stage Navigator | *Section 6: PROJECT DEMONSTRATION – Implementations* | `01-main-workbench.png` (270.6 KB) | 2244 × 1209 px |
| **Figure 2** | INT8 Safety Analysis and Inferred Interval Boundary Comparison | INT8 Safety Stage (SafetyView) | *Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Quantization Safety)* | `02-int8-safety.png` (267.9 KB) | 2244 × 1209 px |
| **Figure 3** | Direct Overflow Rejection and Type Preservation | INT8 Safety / Diagnostics (SafetyView) | *Section 7: RESULT AND DISCUSSION (7.2 Safety Rejection Cases)* | `03-overflow-rejection.png` (287.1 KB) | 2244 × 1209 px |
| **Figure 4** | Interactive SSA Variable Inspector Drawer for z.1 | INT8 Safety + SSAVarInspector Drawer | *Section 6: PROJECT DEMONSTRATION – Implementations (Interactive Exploration)* | `04-ssa-inspector-z1.png` (338.0 KB) | 2244 × 1209 px |
| **Figure 5** | In-Place Operand Navigation and Downstream Use Traversal for x.1 | INT8 Safety + SSAVarInspector Drawer | *Section 6: PROJECT DEMONSTRATION – Implementations (Operand Traversal)* | `05-ssa-inspector-x1.png` (312.8 KB) | 2241 × 1199 px |
| **Figure 6** | Interactive Control-Flow Graph (CFG) Visualization | CFG Stage (CFGView) | *Section 4: DESIGN APPROACH AND DETAILS (4.1 System Architecture – CFG)* | `06-control-flow-graph.png` (207.5 KB) | 2244 × 1209 px |
| **Figure 7** | Dual-Engine Simulator Execution and Equivalence Verification | Simulator Stage (SimulatorView) | *Section 5: METHODOLOGY AND TESTING (5.2 Testing – Simulation Validation)* | `07-simulation-equivalence.png` (207.1 KB) | 2241 × 1199 px |
| **Figure 8** | Bounded Loop Analysis with Sound Iterative Narrowing | Range Analysis / INT8 Safety (RangesView) | *Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Loop Analysis)* | `08-loop-narrowing.png` (195.5 KB) | 2241 × 1199 px |
| **Figure 9** | Lexer Token Stream and Hierarchical AST View | AST Stage (ASTView) & Pipeline Nav | *Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Lexical & Syntax Analysis)* | `09-lexer-ast.png` (202.0 KB) | 2244 × 1286 px |
| **Figure 10** | Three-Address Code and SSA Representation with φ-Node Resolution | SSA Stage (SSAView) – φ-Nodes Sub-tab | *Section 4: DESIGN APPROACH AND DETAILS (4.1 System Architecture – SSA & Phi Nodes)* | `10-tac-ssa-phi.png` (189.4 KB) | 2244 × 1286 px |
| **Figure 11** | Static Range Analysis Table with Integrality and Convergence Metrics | Range Analysis Stage (RangesView) | *Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Range Analysis)* | `11-range-analysis.png` (196.8 KB) | 2244 × 1286 px |
| **Figure 12** | Path-Sensitive Branch Refinement and Unreachable Path Detection | Range Analysis Stage (RangesView) | *Section 7: RESULT AND DISCUSSION (7.3 Branch Refinement and Unreachable Code)* | `12-branch-refinement.png` (226.3 KB) | 2244 × 1286 px |
| **Figure 13** | Quantized IR Side-by-Side Diff and Intermediate Overflow Blocking | Quantization Stage (QuantizedView) – Diff Mode | *Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Quantization Transformation)* | `13-quantized-ir-diagnostics.png` (203.2 KB) | 2244 × 1286 px |
| **Figure 14** | Automated Unit Test Suite and Reproducible Evaluation Terminal | Dual-Terminal Verification Console (verification.html) | *Section 5: METHODOLOGY AND TESTING (5.2 Testing – Verification Suite)* | `14-verification-results.png` (484.1 KB) | 2244 × 1286 px |

---

## Verified Screenshot Catalog Entries

### Figure 1: RANGE//LAB Integrated Workbench Desktop Interface

![RANGE//LAB Integrated Workbench Desktop Interface](../../artifacts/screenshots/01-main-workbench.png)

**Caption:** *Figure 1: RANGE//LAB Integrated Workbench Desktop Interface — safe_arithmetic.qc (Provably Safe Arithmetic)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/01-main-workbench.png` |
| **Image Dimensions** | 2244 × 1209 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 277,113 bytes (270.6 KB) |
| **Relevant Application Stage** | Full Application / Stage Navigator |
| **Test Program / Inputs** | `safe_arithmetic.qc (Provably Safe Arithmetic)` |
| **Recommended Report Location** | **Section 6: PROJECT DEMONSTRATION – Implementations** |

**Detailed Description:**
Complete desktop view of the RANGE//LAB interactive compiler workbench. Demonstrates the live Monaco editor on the left (with numerical C-like source code, line numbers, and syntax highlighting), compiler control switches (widen_after threshold input, --narrow iteration toggle, --prune unreachable toggle), the multi-stage pipeline navigation bar across the top with stage status badges, and the active results panel showing compilation metrics.

**Analytical Evidence (What It Proves):**
Proves the existence, operational status, and end-to-end integration of the web-based visual compiler workbench connected to the live Python compiler backend (src/api/server.py) via FastAPI.

**Technical Qualification & Boundary:**
> [!NOTE]
> Demonstrates UI workflow and system integration; does not by itself prove formal correctness of the underlying abstract interpretation algorithms.

---

### Figure 2: INT8 Safety Analysis and Inferred Interval Boundary Comparison

![INT8 Safety Analysis and Inferred Interval Boundary Comparison](../../artifacts/screenshots/02-int8-safety.png)

**Caption:** *Figure 2: INT8 Safety Analysis and Inferred Interval Boundary Comparison — safe_arithmetic.qc (x=10, y=20, z=x+y)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/02-int8-safety.png` |
| **Image Dimensions** | 2244 × 1209 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 274,292 bytes (267.9 KB) |
| **Relevant Application Stage** | INT8 Safety Stage (SafetyView) |
| **Test Program / Inputs** | `safe_arithmetic.qc (x=10, y=20, z=x+y)` |
| **Recommended Report Location** | **Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Quantization Safety)** |

**Detailed Description:**
Visual comparison of inferred variable intervals against the signed INT8 interval [-128, 127]. Displays variable rows for x.1 [10, 10], y.1 [20, 20], and z.1 [30, 30] alongside color-coded graphical range bars showing exact proportional positioning inside the safe INT8 region, accompanied by 'SAFE -> int8' green badges and zero errors.

**Analytical Evidence (What It Proves):**
Proves the implementation of the abstract interval evaluation pass and the INT8 safety classification rule, confirming that values mathematically contained within [-128, 127] and proven integral are approved for INT8.

**Technical Qualification & Boundary:**
> [!NOTE]
> Shows static interval bounds for a constant-propagated program; edge cases near boundaries require additional tests.

---

### Figure 3: Direct Overflow Rejection and Type Preservation

![Direct Overflow Rejection and Type Preservation](../../artifacts/screenshots/03-overflow-rejection.png)

**Caption:** *Figure 3: Direct Overflow Rejection and Type Preservation — overflow_rejection.qc (x=100, y=30, z=x+y)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/03-overflow-rejection.png` |
| **Image Dimensions** | 2244 × 1209 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 294,023 bytes (287.1 KB) |
| **Relevant Application Stage** | INT8 Safety / Diagnostics (SafetyView) |
| **Test Program / Inputs** | `overflow_rejection.qc (x=100, y=30, z=x+y)` |
| **Recommended Report Location** | **Section 7: RESULT AND DISCUSSION (7.2 Safety Rejection Cases)** |

**Detailed Description:**
Compilation of overflow_rejection.qc where x=100 and y=30 produce intermediate addition z.1 = [130, 130]. Since 130 > 127, the compiler soundly detects that the computation exceeds the signed INT8 upper boundary. The workbench displays a red 'REJECT' badge on variable z.1, visibly extending beyond the safe track, while retaining z in its original 32-bit int representation.

**Analytical Evidence (What It Proves):**
Demonstrates sound conservative rejection: computations that risk 8-bit overflow are blocked from quantization and preserved in their safe 32-bit representation.

**Technical Qualification & Boundary:**
> [!NOTE]
> Illustrates positive overflow (> 127); negative underflow (< -128) is verified in automated test suites.

---

### Figure 4: Interactive SSA Variable Inspector Drawer for z.1

![Interactive SSA Variable Inspector Drawer for z.1](../../artifacts/screenshots/04-ssa-inspector-z1.png)

**Caption:** *Figure 4: Interactive SSA Variable Inspector Drawer for z.1 — safe_arithmetic.qc (Variable z.1)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/04-ssa-inspector-z1.png` |
| **Image Dimensions** | 2244 × 1209 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 346,064 bytes (338.0 KB) |
| **Relevant Application Stage** | INT8 Safety + SSAVarInspector Drawer |
| **Test Program / Inputs** | `safe_arithmetic.qc (Variable z.1)` |
| **Recommended Report Location** | **Section 6: PROJECT DEMONSTRATION – Implementations (Interactive Exploration)** |

**Detailed Description:**
Inspection drawer opened upon clicking variable z.1 in the results table. The drawer displays deep static analysis metadata: variable name z.1, defining instruction z.1 = x.1 + y.1, basic block B1, inferred interval [30, 30] (from x.1 = [10, 10] and y.1 = [20, 20]), integrality status (integral=yes), safety verdict SAFE, quantized target type int8, downstream use in 'print z.1', and clickable interactive operand links for x.1 and y.1.

**Analytical Evidence (What It Proves):**
Demonstrates bidirectional traceability and interactive exploration of SSA variable definitions, operand dependencies, and static analysis verdicts within the compiler workbench.

**Technical Qualification & Boundary:**
> [!NOTE]
> Shows inspection for a single SSA definition; downstream use tracking is demonstrated upon operand traversal.

---

### Figure 5: In-Place Operand Navigation and Downstream Use Traversal for x.1

![In-Place Operand Navigation and Downstream Use Traversal for x.1](../../artifacts/screenshots/05-ssa-inspector-x1.png)

**Caption:** *Figure 5: In-Place Operand Navigation and Downstream Use Traversal for x.1 — safe_arithmetic.qc (Variable x.1 navigated via z.1)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/05-ssa-inspector-x1.png` |
| **Image Dimensions** | 2241 × 1199 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 320,298 bytes (312.8 KB) |
| **Relevant Application Stage** | INT8 Safety + SSAVarInspector Drawer |
| **Test Program / Inputs** | `safe_arithmetic.qc (Variable x.1 navigated via z.1)` |
| **Recommended Report Location** | **Section 6: PROJECT DEMONSTRATION – Implementations (Operand Traversal)** |

**Detailed Description:**
In-place drawer update resulting from clicking operand link x.1 inside the drawer of Figure 4. The inspector updates smoothly to display x.1's definition (x.1 = 10), basic block B1, inferred interval [10, 10], safety verdict SAFE, and lists its downstream use sites in instruction z.1 = x.1 + y.1 without navigating away or losing context.

**Analytical Evidence (What It Proves):**
Validates the Def-Use chain tracking and in-place navigation capabilities of the compiler's intermediate representation inspector.

**Technical Qualification & Boundary:**
> [!NOTE]
> Demonstrates def-use chaining in straight-line arithmetic; complex phi-node merging is examined in separate views.

---

### Figure 6: Interactive Control-Flow Graph (CFG) Visualization

![Interactive Control-Flow Graph (CFG) Visualization](../../artifacts/screenshots/06-control-flow-graph.png)

**Caption:** *Figure 6: Interactive Control-Flow Graph (CFG) Visualization — if_else_phi.qc (Control Flow & Phi Merging)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/06-control-flow-graph.png` |
| **Image Dimensions** | 2244 × 1209 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 212,525 bytes (207.5 KB) |
| **Relevant Application Stage** | CFG Stage (CFGView) |
| **Test Program / Inputs** | `if_else_phi.qc (Control Flow & Phi Merging)` |
| **Recommended Report Location** | **Section 4: DESIGN APPROACH AND DETAILS (4.1 System Architecture – CFG)** |

**Detailed Description:**
Interactive React Flow graph visualization for if_else_phi.qc. Depicts discrete basic blocks (entry block B0, True branch B1, False branch B2, and join block B3) connected by directed control-flow edges labeled with conditional branch predicates (True/False) and unconditional jumps. Instructions are cleanly formatted within each block.

**Analytical Evidence (What It Proves):**
Confirms correct basic block partitioning, leader identification, control-flow edge construction, and graph rendering from Three-Address Code.

**Technical Qualification & Boundary:**
> [!NOTE]
> Displays acyclic branching control flow; cyclic loop back-edges are handled via the same graph model.

---

### Figure 7: Dual-Engine Simulator Execution and Equivalence Verification

![Dual-Engine Simulator Execution and Equivalence Verification](../../artifacts/screenshots/07-simulation-equivalence.png)

**Caption:** *Figure 7: Dual-Engine Simulator Execution and Equivalence Verification — safe_arithmetic.qc (Simulation Backend)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/07-simulation-equivalence.png` |
| **Image Dimensions** | 2241 × 1199 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 212,100 bytes (207.1 KB) |
| **Relevant Application Stage** | Simulator Stage (SimulatorView) |
| **Test Program / Inputs** | `safe_arithmetic.qc (Simulation Backend)` |
| **Recommended Report Location** | **Section 5: METHODOLOGY AND TESTING (5.2 Testing – Simulation Validation)** |

**Detailed Description:**
Dual-engine interpretation view executing original 32-bit IR side-by-side with INT8 quantized IR under identical inputs. Displays matching terminal output '30', variable environment tables, instruction execution step traces, and the prominent 'SIMULATION EQUIVALENT (MATCH)' status banner.

**Analytical Evidence (What It Proves):**
Demonstrates functional equivalence between pre-quantization and post-quantization programs for the executed inputs, confirming that 8-bit two's-complement arithmetic reproduces original program behavior.

**Technical Qualification & Boundary:**
> [!NOTE]
> Empirical validation for tested inputs; constitutes functional validation rather than exhaustive formal verification of all paths.

---

### Figure 8: Bounded Loop Analysis with Sound Iterative Narrowing

![Bounded Loop Analysis with Sound Iterative Narrowing](../../artifacts/screenshots/08-loop-narrowing.png)

**Caption:** *Figure 8: Bounded Loop Analysis with Sound Iterative Narrowing — bounded_loop_counter.qc (i = 0; while (i < 10) i = i + 1)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/08-loop-narrowing.png` |
| **Image Dimensions** | 2241 × 1199 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 200,164 bytes (195.5 KB) |
| **Relevant Application Stage** | Range Analysis / INT8 Safety (RangesView) |
| **Test Program / Inputs** | `bounded_loop_counter.qc (i = 0; while (i < 10) i = i + 1)` |
| **Recommended Report Location** | **Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Loop Analysis)** |

**Detailed Description:**
Range analysis output for bounded_loop_counter.qc with the --narrow flag enabled. Illustrates Kleene iteration over the loop CFG: while widening alone expands loop header variable i.2 to UNKNOWN ([-inf, +inf]) causing rejection, enabling narrowing iterations intersects the widened interval with the loop condition i < 10 along the back-edge, successfully contracting i.2 to tight interval [0, 10] and i.3 to [1, 10]. Because [0, 10] is contained in [-128, 127] and integral, the loop variable converges safely and is approved for INT8 quantization (SAFE -> int8).

**Analytical Evidence (What It Proves):**
Proves the implementation of sound loop narrowing, demonstrating that loop conditions can refine extrapolated intervals back to safe, bounded ranges that qualify for INT8.

**Technical Qualification & Boundary:**
> [!NOTE]
> Requires monotonically bounded loop exit conditions; unconstrained loops (e.g. unbounded accumulators) remain UNKNOWN.

---

### Figure 9: Lexer Token Stream and Hierarchical AST View

![Lexer Token Stream and Hierarchical AST View](../../artifacts/screenshots/09-lexer-ast.png)

**Caption:** *Figure 9: Lexer Token Stream and Hierarchical AST View — safe_arithmetic.qc (Frontend Analysis)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/09-lexer-ast.png` |
| **Image Dimensions** | 2244 × 1286 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 206,875 bytes (202.0 KB) |
| **Relevant Application Stage** | AST Stage (ASTView) & Pipeline Nav |
| **Test Program / Inputs** | `safe_arithmetic.qc (Frontend Analysis)` |
| **Recommended Report Location** | **Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Lexical & Syntax Analysis)** |

**Detailed Description:**
Frontend syntax analysis view displaying the collapsible, hierarchical Abstract Syntax Tree alongside source code. Shows AST node badges (Program, Declaration, BinaryExpr, Identifier, IntLiteral), data types (:int), and exact source line/column coordinates (@line:col). The pipeline bar indicates 23 tokens generated by the lexer.

**Analytical Evidence (What It Proves):**
Validates lexical analysis, tokenization, grammar parsing, operator precedence, and AST construction with faithful source coordinate retention.

**Technical Qualification & Boundary:**
> [!NOTE]
> Shows AST structure for mini numerical syntax; language does not include pointers, structs, or dynamic heap allocation.

---

### Figure 10: Three-Address Code and SSA Representation with φ-Node Resolution

![Three-Address Code and SSA Representation with φ-Node Resolution](../../artifacts/screenshots/10-tac-ssa-phi.png)

**Caption:** *Figure 10: Three-Address Code and SSA Representation with φ-Node Resolution — if_else_phi.qc (max.2 = phi(B1: max.1, B2: max.0))*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/10-tac-ssa-phi.png` |
| **Image Dimensions** | 2244 × 1286 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 193,921 bytes (189.4 KB) |
| **Relevant Application Stage** | SSA Stage (SSAView) – φ-Nodes Sub-tab |
| **Test Program / Inputs** | `if_else_phi.qc (max.2 = phi(B1: max.1, B2: max.0))` |
| **Recommended Report Location** | **Section 4: DESIGN APPROACH AND DETAILS (4.1 System Architecture – SSA & Phi Nodes)** |

**Detailed Description:**
SSA intermediate representation view focusing on φ-node resolution for branching control flow. Displays target variable max.2 (type int), and interactive predecessor inflow buttons explicitly mapping basic block B1 to max.1 and basic block B2 to max.0, confirming dominance-frontier phi placement and variable renaming.

**Analytical Evidence (What It Proves):**
Validates dominance frontier calculation, minimal SSA φ-node placement, and version renaming for control-flow merge points.

**Technical Qualification & Boundary:**
> [!NOTE]
> Displays φ-nodes for forward conditional branches; loop header φ-nodes with back-edges are evaluated in loop analysis.

---

### Figure 11: Static Range Analysis Table with Integrality and Convergence Metrics

![Static Range Analysis Table with Integrality and Convergence Metrics](../../artifacts/screenshots/11-range-analysis.png)

**Caption:** *Figure 11: Static Range Analysis Table with Integrality and Convergence Metrics — bounded_loop_counter.qc (Full Ranges Table)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/11-range-analysis.png` |
| **Image Dimensions** | 2244 × 1286 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 201,568 bytes (196.8 KB) |
| **Relevant Application Stage** | Range Analysis Stage (RangesView) |
| **Test Program / Inputs** | `bounded_loop_counter.qc (Full Ranges Table)` |
| **Recommended Report Location** | **Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Range Analysis)** |

**Detailed Description:**
Comprehensive range analysis table displaying variable names, defining instructions, inferred intervals, integrality status (integral=yes), INT8 safety status, filter pills (all, safe, rejected, quantized, unknown, unreachable), search box, and the convergence metric indicator (e.g. '6 sweeps (converged=true)').

**Analytical Evidence (What It Proves):**
Proves the complete tabular presentation of abstract interpretation results, including integrality tracking and fixed-point convergence counters.

**Technical Qualification & Boundary:**
> [!NOTE]
> Interval domain does not capture relational invariants between variables (e.g. x - y = k); operates over independent intervals.

---

### Figure 12: Path-Sensitive Branch Refinement and Unreachable Path Detection

![Path-Sensitive Branch Refinement and Unreachable Path Detection](../../artifacts/screenshots/12-branch-refinement.png)

**Caption:** *Figure 12: Path-Sensitive Branch Refinement and Unreachable Path Detection — branch_refine.qc (x = 15; if (x >= 10) y = x - 5 else y = x + 5)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/12-branch-refinement.png` |
| **Image Dimensions** | 2244 × 1286 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 231,702 bytes (226.3 KB) |
| **Relevant Application Stage** | Range Analysis Stage (RangesView) |
| **Test Program / Inputs** | `branch_refine.qc (x = 15; if (x >= 10) y = x - 5 else y = x + 5)` |
| **Recommended Report Location** | **Section 7: RESULT AND DISCUSSION (7.3 Branch Refinement and Unreachable Code)** |

**Detailed Description:**
Path-sensitive interval refinement on branch_refine.qc. Since x=15, the branch condition x >= 10 is statically known to be True. The True branch computes y.3 = [10, 10], while the False branch condition x < 10 intersects with [15, 15] to produce the empty set (bottom element). Variable y.2 is authentically marked with the red 'UNREACHABLE' badge.

**Analytical Evidence (What It Proves):**
Proves path-sensitive abstract interpretation, branch condition refinement, and static detection of dead/unreachable control-flow paths without code fabrication.

**Technical Qualification & Boundary:**
> [!NOTE]
> Refinement operates on linear relational comparisons (<, <=, >, >=, ==, !=); non-linear branch conditions are not refined.

---

### Figure 13: Quantized IR Side-by-Side Diff and Intermediate Overflow Blocking

![Quantized IR Side-by-Side Diff and Intermediate Overflow Blocking](../../artifacts/screenshots/13-quantized-ir-diagnostics.png)

**Caption:** *Figure 13: Quantized IR Side-by-Side Diff and Intermediate Overflow Blocking — intermediate_overflow.qc (a=100, b=50, c=a+b, d=c-50)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/13-quantized-ir-diagnostics.png` |
| **Image Dimensions** | 2244 × 1286 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 208,103 bytes (203.2 KB) |
| **Relevant Application Stage** | Quantization Stage (QuantizedView) – Diff Mode |
| **Test Program / Inputs** | `intermediate_overflow.qc (a=100, b=50, c=a+b, d=c-50)` |
| **Recommended Report Location** | **Section 5: METHODOLOGY AND TESTING (5.1 Module Description – Quantization Transformation)** |

**Detailed Description:**
Side-by-side comparison of pre-quantization SSA IR against INT8 quantized IR. Demonstrates genuine INT8 transformation for a.1: int8 and b.1: int8 (2 variables rewritten), while c.1 overflows (150 > 127) and is kept in int. Crucially, d.1 evaluates to [100, 100] within bounds, but is soundly BLOCKED from quantization because its input operand c.1 was unsafe.

**Analytical Evidence (What It Proves):**
Validates intermediate dependency tracking: values falling within [-128, 127] are blocked from quantization if their upstream computations could have overflowed, preventing catastrophic numerical corruption.

**Technical Qualification & Boundary:**
> [!NOTE]
> Illustrates conservative blocking; does not perform algebraic re-association to circumvent intermediate overflow.

---

### Figure 14: Automated Unit Test Suite and Reproducible Evaluation Terminal

![Automated Unit Test Suite and Reproducible Evaluation Terminal](../../artifacts/screenshots/14-verification-results.png)

**Caption:** *Figure 14: Automated Unit Test Suite and Reproducible Evaluation Terminal — Test Suite (137 tests) & Reproducible Evaluation (12 benchmarks)*

| Metadata Attribute | Verification Detail |
|---|---|
| **Source Filename** | `artifacts/screenshots/14-verification-results.png` |
| **Image Dimensions** | 2244 × 1286 px (Rendered High-DPI; 1496 × 857 pt CSS Viewport) |
| **File Size** | 495,705 bytes (484.1 KB) |
| **Relevant Application Stage** | Dual-Terminal Verification Console (verification.html) |
| **Test Program / Inputs** | `Test Suite (137 tests) & Reproducible Evaluation (12 benchmarks)` |
| **Recommended Report Location** | **Section 5: METHODOLOGY AND TESTING (5.2 Testing – Verification Suite)** |

**Detailed Description:**
High-resolution terminal verification display captured from the live application environment. Left window shows the Python unittest runner completing all 137 unit tests with zero errors and zero failures (OK in 0.511s on capture, 0.291s in current run). Right window shows the reproducible evaluation suite (evaluate.py / tests.evaluation) executing all 12 benchmarks with 54 SSA variables, 35 safe (64.8%), 32 quantized (59.3%), 3 blocked, 19 rejected (35.2%), no safety violations observed across the 12 evaluated benchmarks, 100% simulation equivalence rate, 44.4% theoretical storage-width reduction, and ALL PASS status.

**Analytical Evidence (What It Proves):**
Provides authentic, unedited empirical evidence of comprehensive compiler test coverage (137 unit tests) and reproducible benchmark validation with 100% equivalence and no observed safety violations across the evaluation benchmarks.

**Technical Qualification & Boundary:**
> [!NOTE]
> Confirms software correctness across the 137 test cases and 12 benchmarks; theoretical storage reduction (44.4%) is an estimate of representation width, not measured hardware speedup.

---
