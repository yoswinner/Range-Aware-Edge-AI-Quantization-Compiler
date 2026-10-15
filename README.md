# Range-Aware Edge AI Quantization Compiler

**SSA-based static analysis compiler for safety-aware INT8 quantization.**

---

## Overview

This is a teaching-scale, end-to-end compiler pipeline that uses **Static Single Assignment (SSA) form**, **abstract range analysis**, and **integrality analysis** to determine whether numerical computations can safely be represented using signed 8-bit integers (`INT8`).

The compiler takes a small numerical C-like language as input, builds an intermediate representation in SSA form with explicit phi nodes, performs conservative abstract interpretation over interval and integrality domains, refines value ranges along control-flow branch edges, applies sound loop widening and narrowing, and selectively transforms only those computations for which INT8 safety can be statically proven. Computations that exceed bounds, have fractional values, depend on unsafe intermediates, or are unsupported remain unquantized in their original type (e.g. FP32).

---

## Motivation

Edge AI deployments benefit from reduced-precision representations like INT8 because 8-bit storage can reduce weight and activation memory footprint by up to 75% compared to 32-bit representations. However, uncontrolled quantization causes overflow and numerical degradation. Rather than relying on runtime sampling, dynamic calibration, or post-hoc heuristics, this compiler performs rigorous static analysis to guarantee that every quantized value is provably safe under all possible execution paths.

---

## Language Features and Operators

The compiler accepts mini numerical programs (`.qc`) with the following supported features:

- **Types:** `int` (32-bit integer), `float` (FP32), `bool` (Boolean result of comparisons), and `int8` (quantized IR type).
- **Arithmetic Operators:** Addition (`+`), subtraction (`-`), multiplication (`*`), division (`/`), and unary negation (`-`).
- **Relational & Equality Comparisons:** Less than (`<`), less than or equal (`<=`), greater than (`>`), greater than or equal (`>=`), equality (`==`), and inequality (`!=`).
- **Control Flow:** `if-else` conditionals and `while` loops.
- **I/O:** `print` statement for output and uninitialized declarations for external program inputs.

---

## Compiler Architecture & Pipeline

```text
Source Code (.qc)
       │
       ▼
┌──────────────┐      Tokens
│ Lexer        │ ─────────────────► Token stream
└──────────────┘
       │
       ▼
┌──────────────┐      AST
│ Parser       │ ─────────────────► Abstract Syntax Tree
└──────────────┘
       │
       ▼
┌──────────────┐      Semantic Validation
│ Type Checker │ ─────────────────► Scope-resolved AST with Type annotations
└──────────────┘
       │
       ▼
┌──────────────┐      TAC
│ Lowering     │ ─────────────────► Three Address Code with basic blocks & temps
└──────────────┘
       │
       ▼
┌──────────────┐      CFG
│ CFG Builder  │ ─────────────────► Basic blocks with fallthrough, jump, true, false edges
└──────────────┘
       │
       ▼
┌──────────────┐      SSA
│ SSA Builder  │ ─────────────────► Dominator Tree, Dominance Frontiers, Phi nodes, Renaming
└──────────────┘
       │
       ▼
┌──────────────┐      Abstract Domain
│ Range Anal.  │ ─────────────────► Interval analysis, Branch refinement, Widening & Narrowing
└──────────────┘
       │
       ▼
┌──────────────┐      Quantization Pass
│ Quantizer    │ ─────────────────► Safety decisions, Intermediate dependency tracking, Retyping
└──────────────┘
       │
       ▼
┌──────────────┐      Software Simulator
│ Simulator    │ ─────────────────► Executes original vs quantized IR, verifies equivalence
└──────────────┘
```

---

## Abstract Range and Integrality Analysis

### Abstract Value Domain (`AbsVal`)
The abstract domain represents the runtime values of SSA variables with exact rational arithmetic (`Fraction`) to eliminate floating-point rounding errors:
- `lo`, `hi`: Lower and upper bounds (`Fraction`), or `None` for unbounded ($-\infty$, $+\infty$).
- `integral`: `True` only when the value is mathematically guaranteed to be an integer on all execution paths.
- `unreachable`: Boolean bottom element ($\bot$) representing impossible control-flow paths or empty intervals.
- `div_zero`: Diagnostic flag indicating that division by zero could occur on an execution path.
- `reason`: Explanatory message for diagnostic reporting.

### Transfer Functions
- **Addition:** $[a, b] + [c, d] = [a+c, b+d]$; integral if both operands are integral.
- **Subtraction:** $[a, b] - [c, d] = [a-d, b-c]$; integral if both operands are integral.
- **Multiplication:** All four quadrant cross-products $\min / \max(ac, ad, bc, bd)$; integral if both operands are integral.
- **Division:** Divisors containing zero (or unbounded divisors) trigger `div_zero=True` and yield `UNKNOWN`. Valid non-zero divisor ranges compute four quotient extremes. Division is conservatively non-integral.
- **Unary Negation:** $-[a, b] = [-b, -a]$.
- **Relational Comparisons:** Produces `[0, 1]` with `Type.BOOL` and `integral=True`, deciding `[1, 1]` or `[0, 0]` when operand intervals are strictly disjoint.

---

## Branch-Condition Refinement

The compiler implements path-sensitive branch refinement:
- Evaluates conditions ending basic blocks with `CondJump`.
- **True branch edge:** Enforces $left \text{ op } right$.
- **False branch edge:** Enforces the negated condition $\neg(left \text{ op } right)$.
- **Integer Constraints:** Applies discrete boundary adjustments for strict inequalities:
  - $x < c \implies x \le c - 1$
  - $x \le c \implies x \le c$
  - $x > c \implies x \ge c + 1$
  - $x \ge c \implies x \ge c$
- **Continuous Float Constraints:** Uses exact continuous bounds without $\pm 1$ shifts.
- **Variable-to-Variable Refinement:** Intersects bounds across pairs of variables when compared.
- **Empty Interval Detection:** When a branch condition contradicts known bounds, interval intersection (`meet`) produces an unreachable bottom state, identifying impossible paths.

---

## Loop Widening and Narrowing

To guarantee termination over cyclic control flow while retaining precision:
- **Kleene Iteration:** Sweeps through the CFG in reverse postorder.
- **Widening Threshold (`--widen-after`):** Ordinary iteration proceeds for $N$ sweeps (default: 3). If a loop header phi node is still moving after $N$ sweeps, widening extrapolates the moving bounds to prevent infinite loops.
- **Sound Narrowing (`--narrow`):** Applies the loop condition constraint to the loop body and back-edge, recovering tight bounds for bounded loop counters, decreasing counters, and loops traversing negative numbers.
- **Unconstrained Loops:** Accumulator loops or loops lacking bounding exit conditions (e.g., `sum = sum + x`) remain conservatively `UNKNOWN` and are never quantized.

---

## INT8 Safety Eligibility Rules

A value is rewritten to `INT8` **if and only if all** of the following conditions hold:

1. **Exact Boundary Range:** The statically inferred interval must satisfy:
   $$\text{inferred range} \subseteq [-128, 127]$$
   - $-128$ and $127$ are safe when integral.
   - Values $\le -129$ or $\ge 128$ are rejected for potential overflow.
2. **Guaranteed Integrality:** The value must be proven integral on all execution paths. Float variables and division results are rejected with `non-integral`.
3. **No Division-by-Zero Risk:** Values with `div_zero=True` are rejected.
4. **Intermediate Dependency Tracking:** An expression within $[-128, 127]$ is **blocked** from quantization if any of its input operands or upstream intermediate calculations were not INT8-safe.
5. **Phi Node Safety:** A phi node is eligible only if every reachable incoming alternative satisfies safety constraints.
6. **Supported Operations:** Copies, phi nodes, addition, subtraction, multiplication, and unary negation are supported for INT8 retyping. Division (never integral) and relational comparisons (Boolean-valued) are preserved in their original representation.

---

## Software Simulator Backend

The compiler includes a software simulator that interprets SSA programs before and after quantization:
- Implements two's-complement signed 8-bit arithmetic semantics for `INT8` instructions within $[-128, 127]$.
- Executes original (FP32/INT) and quantized IR side by side.
- Verifies numerical equivalence between original and quantized outputs.

---

## Command-Line Interface (CLI)

```bash
python -m src.main <path_to_file.qc> [OPTIONS]
```

### Arguments and Flags
| Flag | Description |
|---|---|
| `--emit <stages>` | Stages to inspect: `tokens`, `ast`, `tac`, `cfg`, `ssa`, `ranges`, `quantized`, `diagnostics`, `summary`, `simulate`, or `all`. (Default: `diagnostics summary`) |
| `--widen-after N` | Ordinary iterations before widening at loop phis (Default: `3`). |
| `--narrow` | Enable sound narrowing iterations after widening to tighten loop bounds. |
| `--prune-unreachable` | Prune proven impossible control-flow paths during analysis. |
| `--inputs <v1> <v2>...` | Input values for simulation of programs with uninitialized declarations. |

### Example Invocations

```bash
# Safe arithmetic diagnostics and summary
python -m src.main examples/safe_arithmetic.qc --emit diagnostics summary

# Simulate unquantized vs INT8 execution
python -m src.main examples/safe_arithmetic.qc --emit simulate

# Full pipeline inspection
python -m src.main examples/safe_arithmetic.qc --emit all

# Loop analysis with widening inspection
python -m src.main examples/while_loop.qc --emit ssa ranges quantized diagnostics --widen-after 3

# Bounded loop with narrowing enabled
python -m src.main examples/bounded_loop.qc --emit ranges quantized simulate --narrow
```

---

## RANGE//LAB — Interactive INT8 Quantization Workbench

**RANGE//LAB** is an interactive, developer-grade compiler laboratory designed for visual exploration of range analysis, control-flow graphs, SSA φ-nodes, and INT8 quantization safety.

### Architecture
- **Compiler Core & API:** Python in-process pipeline exposed via FastAPI (`src/api/server.py`) with structured JSON serialization (`src/api/serializer.py`).
- **Web Frontend:** React 19, TypeScript, and Vite application (`web/`) with Monaco Editor, React Flow interactive CFG visualization, and custom dark technical styling.

```text
┌────────────────────────────────────────────────────────┐
│             RANGE//LAB Web Workbench (React)          │
│   Monaco Editor │ Stage Navigator │ Interactive CFG    │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│           FastAPI Backend Server (src/api/)            │
│       compile_source() in-process execution driver     │
└───────────────────────────┬────────────────────────────┘
                            │ Direct Python Object Calls
                            ▼
┌────────────────────────────────────────────────────────┐
│        Existing Python Compiler & Simulator Engine     │
│  Lexer → Parser → TAC → CFG → SSA → Range → INT8 → Sim │
└────────────────────────────────────────────────────────┘
```

### Quickstart & Launch Commands

#### Prerequisites
- Python 3.10+ (with `fastapi`, `uvicorn`, `pydantic`)
- Node.js 18+ and npm

#### 1. Launch Backend & Built Frontend (Single Command)
Build the frontend and run the unified server:
```bash
# Build frontend static bundle
cd web
npm install
npm run build
cd ..

# Start unified FastAPI server on port 8000
python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

#### 2. Local Development Mode (Frontend Hot-Reloading)
Run backend and frontend independently during development:
```bash
# Terminal 1: Backend API Server
python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Vite Frontend Dev Server
cd web
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser (API calls are automatically proxied to port 8000).

### Workbench Interactive Views
- **Source Editor:** Monaco code editor with custom `.qc` language syntax highlighting, line numbers, and <kbd>Ctrl+Enter</kbd> compilation trigger.
- **Header Controls:** Built-in selector with 12 benchmark examples, `--widen-after` threshold stepper, `--narrow` toggle, and `--prune` unreachable block toggle.
- **Navigable Pipeline Stages:**
  - **Lexer:** Searchable token stream with lexeme, kind, position, and evaluated decimal literal fractions.
  - **AST:** Interactive hierarchical tree with collapsible statement and expression nodes.
  - **TAC:** Three-address code listing with instruction offsets, def/use sets, and labels.
  - **CFG:** Interactive graph with drag, zoom, and pan. Basic blocks render with true (green), false (red), jump (cyan), and back-edge (dashed amber) markers. Click any block to open the Block Inspector drawer.
  - **SSA:** SSA-renamed IR, φ-node table mapping predecessor blocks to incoming versions, and dominator tree (immediate dominators and dominance frontiers).
  - **Range Analysis:** Multi-column table of all SSA variables with filter pills (`All`, `Safe`, `Rejected`, `Quantized`, `Unknown`, `Unreachable`) and search.
  - **INT8 Safety:** Graphical number line comparing inferred intervals to $[-128, 127]$, with color-coded bars, overflow delta badges, and safety policy criteria.
  - **Quantization:** Transformed IR viewer with side-by-side diff mode and operand dependency blocking explanations.
  - **Diagnostics:** Traceable compiler diagnostic records preserving source locations, variable names, and verdicts.
  - **Summary:** Metric cards showing safe percentages, theoretical storage-width reduction, and rejection breakdowns.
  - **Simulator:** Side-by-side execution output comparison showing original 32-bit output vs. quantized INT8 output with 100% equivalence verification.

---

## Running Tests and Reproducible Evaluation

### Unit & Regression Test Suite
Run the complete unittest test suite (137 tests including compiler and API tests):
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Reproducible Evaluation Runner
Run the 12-benchmark evaluation suite:
```bash
python -m tests.evaluation
# or
python evaluate.py
```

### Frontend Build & Type Validation
Validate frontend TypeScript types and production build:
```bash
cd web
npm run build
```

---

## Current Scope and Limitations

- **Backend:** The compiler backend is a software interpreter for education, verification, and analysis demonstration. It does not produce machine code (e.g. LLVM IR, ARM assembly).
- **Theoretical Storage Metrics:** The reported storage reduction (up to 75% for 8-bit vs 32-bit representations) is a theoretical data-width reduction. We make no claims of physical hardware latency, energy, or cache savings without hardware deployment.
- **Language Scope:** Focused on core numerical kernels, arithmetic expressions, conditionals, and loops. Arrays, pointers, and structures are outside the mini-language scope.
- **Conservative Fallback:** Unsupported operations and unprovable ranges remain in their original type.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
