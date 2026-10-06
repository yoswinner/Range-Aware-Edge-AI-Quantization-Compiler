# Range-Aware Edge AI Quantization Compiler

**SSA-based static analysis compiler for safety-aware INT8 quantization.**

---

## Overview

This is a compiler pipeline that uses **SSA-based static analysis**, **range analysis**, and **integrality analysis** to determine whether numerical computations can safely be represented using INT8 based on the currently implemented analysis and supported operations.

The compiler takes a small numerical C-like language as input, builds an intermediate representation in Static Single Assignment (SSA) form, performs conservative static analysis on value ranges and integrality, and selectively transforms only those computations for which INT8 safety can be statically proven. Values whose safety cannot be proven remain unquantized (e.g. in FP32).

## Motivation

Edge AI deployments can benefit from reduced-precision arithmetic such as INT8 because narrower representations can reduce storage and memory bandwidth requirements. However, aggressive quantization can introduce issues if bounds are exceeded. This project implements a compiler-driven approach: rather than relying on runtime profiling or dynamic heuristics, the compiler performs conservative static analysis to identify provably safe quantization opportunities under its strictly defined constraints.

## Compiler Pipeline and Components

The compiler is structured as a complete end-to-end pipeline:

1. **Lexer & Parser:** Reads the source program and constructs an Abstract Syntax Tree (AST).
2. **Semantic Analysis:** Performs type checking and semantic validation.
3. **IR Generation (TAC):** Lowers the AST into Three Address Code (TAC).
4. **CFG Construction:** Groups TAC into basic blocks and builds a Control Flow Graph (CFG).
5. **SSA Construction:** Converts the CFG into Static Single Assignment (SSA) form, inserting **phi nodes** to track values across control-flow branches. This enables precise, path-sensitive data-flow analysis.
6. **Range & Integrality Analysis:** Propagates known minimum and maximum bounds for variables, along with integrality properties (whether a value has a fractional part).
7. **Loop Widening:** To handle loops without analyzing infinitely, the compiler simulates loop iterations statically up to a limit. If the analysis does not stabilize within the configured widening threshold, the compiler conservatively widens the affected range to `UNKNOWN`, ensuring that loop analysis terminates.
8. **INT8 Safety Check:** Determines whether each computation satisfies the strict INT8 constraints.
9. **Selective Quantization:** Replaces operations with INT8 equivalents in the SSA IR where proven safe.
10. **Simulator Backend:** A lightweight, teaching-scale execution mechanism that interprets the quantized IR. *(Note: This is an educational simulator, not an LLVM backend or production hardware backend.)*

## Core Safety Rule

The decision to quantize a value is governed by a strict, conservative safety check. A value should only be lowered to INT8 when the compiler can establish that it is integral and its possible range stays within [-128, 127].

Specifically, a value is considered safe for INT8 quantization **only if all** of the following hold:
1. The value is **proven to be integral** (no fractional component) on all paths.
2. The value's **range is statically known** through analysis.
3. The statically known range **fits entirely within** `[-128, 127]`.
4. Safety is established **conservatively** — if any condition cannot be proven (e.g., an input is bounded by `UNKNOWN`), the value is **not** quantized.

Unsafe, insufficiently proven, non-integral, or UNKNOWN values remain unquantized, preserving the compiler's conservative safety policy within the supported analysis.

## Project Structure

```text
Range-Aware-Edge-AI-Quantization-Compiler/
├── src/                        # Source code for all compiler stages
│   ├── lexer/                  
│   ├── parser/                 
│   ├── ast/                    
│   ├── semantic/               
│   ├── ir/                     
│   ├── cfg/                    
│   ├── ssa/                    
│   ├── analysis/               
│   ├── quantization/           
│   ├── backend/                # Lightweight simulator 
│   ├── diagnostics/            
│   └── main.py                 # CLI Entry point
├── tests/                      # Unittest suites for all stages
├── examples/                   # Sample .qc programs demonstrating features
├── docs/                       # Additional documentation
└── README.md                   # This file
```

## Setup and Requirements

- Python 3.10+

Clone the repository:

```bash
git clone <repository_url>
cd Range-Aware-Edge-AI-Quantization-Compiler
```

## Running the Compiler

The compiler is invoked through its CLI interface. You can compile and analyze any `.qc` source file.

```bash
python -m src.main <path_to_file.qc>
```

You can view the output of specific compiler stages using the `--emit` flag. Available stages are: `tokens`, `ast`, `tac`, `cfg`, `ssa`, `ranges`, `quantized`, `diagnostics`, `summary`, or `all`.

**Example:**
```bash
python -m src.main examples/safe_arithmetic.qc --emit summary diagnostics
```

**Output Snippet:**
```text
===== summary =====
SSA values analysed: 3
  labelled SAFE:      3
  rewritten to int8:  3
  labelled REJECT:    0

===== diagnostics =====
Line 1, Column 5
Variable: x.1
Type: int
Inferred range: [10, 10]
Integral: YES
INT8 Safety: SAFE
Reason: within INT8 bounds and integral on all paths
Transformation: int -> int8
...
```

To control loop widening (how many ordinary iterations to simulate before assuming `UNKNOWN`), use `--widen-after`:
```bash
python -m src.main examples/while_loop.qc --widen-after 5
```

## Examples

The `examples/` directory contains sample programs that demonstrate the compiler's analysis capabilities:

- `safe_arithmetic.qc`: Basic arithmetic where all values statically fall within `[-128, 127]`. All operations are quantized.
- `if_else_phi.qc`: Demonstrates SSA phi-node resolution across branches. If both branches produce safe values, the phi-node is quantized.
- `while_loop.qc`: Demonstrates range expansion in loops and loop widening. Loop iterators that might exceed INT8 bounds are safely rejected.
- `overflow_rejection.qc`: An arithmetic sequence that clearly exceeds 127. The compiler rejects quantization for the overflowing variables.
- `non_integral_rejection.qc`: Demonstrates the integrality analysis rejecting variables that contain fractional parts.

## Running the Test Suite

The compiler includes a comprehensive test suite covering the lexer, parser, AST, semantic analysis, IR generation, CFG, SSA, range analysis, quantization logic, and a full integration pipeline.

Run the tests using Python's built-in `unittest` framework:

```bash
python -m unittest discover -s tests -v
```



## Current Limitations and Future Work

- **Backend:** The current backend is a lightweight software simulator intended for teaching and validation. It does not output machine code (e.g., x86, ARM, or LLVM IR) and is not intended to run on physical hardware.
- **Measured Performance:** Because this project uses a teaching-scale simulator, we do not claim experimentally measured runtime speedups, latency reductions, or energy savings. The INT8 quantization provides *theoretical* storage-width benefits.
- **Language Features:** The input language currently supports numerical operations and basic control flow. Complex data structures like arrays and structs are not currently supported.
- **Unsupported Operations:** Any unsupported or unanalyzable operations remain conservatively unquantized.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
