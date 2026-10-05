# Range-Aware Edge AI Quantization Compiler

**SSA-based static analysis compiler for safe FP32-to-INT8 quantization.**

---

## Overview

This is a Compiler Design course project implementing a small compiler pipeline that uses **SSA-based static analysis**, **range analysis**, and **integrality analysis** to determine whether numerical computations can safely be represented using INT8.

The compiler takes a small numerical C-like language as input, builds an intermediate representation in Static Single Assignment (SSA) form, performs conservative static analysis on value ranges and integrality, and selectively transforms only those computations for which INT8 safety can be statically proven. Values whose safety cannot be proven remain in FP32.

## Problem Statement

> Can a compiler statically determine which numerical computations can be safely represented using INT8 and transform only those computations for which safety can be proven?

Edge AI deployments often benefit from reduced-precision arithmetic (e.g., INT8) for lower memory usage and faster execution. However, aggressive quantization can introduce overflow, underflow, or precision loss. This project explores a compiler-driven approach: rather than relying on runtime profiling or heuristics, the compiler itself performs conservative static analysis to identify provably safe quantization opportunities.

## Objectives

1. **Build a small numerical C-like compiler front end** — lexer, parser, AST construction, and semantic analysis for a simplified input language supporting numerical computations.
2. **Generate Three Address Code (TAC) and Control Flow Graph (CFG)** — lower the AST into a standard intermediate representation organized into basic blocks.
3. **Convert the IR into Static Single Assignment (SSA) form** — apply SSA construction to enable precise data-flow analysis.
4. **Perform static range and integrality analysis** — propagate value ranges and integrality properties through the SSA IR using conservative abstract interpretation.
5. **Develop conservative INT8 safety checks** — determine whether each computation's range fits within INT8 bounds and its result is provably integral.
6. **Transform proven-safe computations to INT8** — selectively quantize only those operations for which safety has been statically established.
7. **Preserve source-level traceability** — maintain mappings from IR operations back to source locations for diagnostics and evaluation.

## Compiler Pipeline

```
Source Program
     ↓
   Lexer
     ↓
   Parser
     ↓
    AST
     ↓
Semantic Analysis
     ↓
Three Address Code (TAC)
     ↓
Basic Blocks / CFG
     ↓
    SSA
     ↓
Range + Integrality Analysis
     ↓
INT8 Safety Check
     ↓
Quantization Transformation
     ↓
Quantized SSA IR
     ↓
Simulator / Backend
     ↓
Diagnostics + Evaluation
```

## Core Safety Principle

The quantization decision for each value is governed by a conservative safety check:

- **INT8 representable range:** [-128, 127]
- A value is considered safe for INT8 quantization **only if all** of the following hold:
  1. The value is **proven to be integral** (no fractional component).
  2. The value's **range is statically known** through analysis.
  3. The known range **fits entirely within** [-128, 127].
  4. Safety is established **conservatively** — if any of the above cannot be proven, the value is **not** quantized.
- **If safety cannot be proven, the value remains in FP32.** This ensures correctness is never sacrificed for optimization.

## Project Structure

```
Range-Aware-Edge-AI-Quantization-Compiler/
│
├── src/                        # Source code for all compiler stages
│   ├── lexer/                  # Lexical analysis (tokenization)
│   ├── parser/                 # Syntax analysis (parsing)
│   ├── ast/                    # Abstract Syntax Tree representation
│   ├── semantic/               # Semantic analysis (type checking, validation)
│   ├── ir/                     # Three Address Code (TAC) generation
│   ├── cfg/                    # Basic blocks and Control Flow Graph construction
│   ├── ssa/                    # SSA form construction and utilities
│   ├── analysis/               # Range analysis and integrality analysis
│   ├── quantization/           # INT8 safety checking and quantization transformation
│   ├── backend/                # Lightweight simulator / backend
│   └── diagnostics/            # Source-level diagnostics and evaluation reporting
│
├── tests/                      # Test suites for each compiler stage
│   ├── lexer/                  # Lexer tests
│   ├── parser/                 # Parser tests
│   ├── ssa/                    # SSA construction tests
│   ├── range_analysis/         # Range and integrality analysis tests
│   ├── quantization/           # Quantization decision and transformation tests
│   └── integration/            # End-to-end integration tests
│
├── examples/                   # Example input programs for the compiler
│
├── docs/                       # Documentation
│   └── review/                 # Project review presentation and review documents
│
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
└── LICENSE                     # MIT License
```

## Current Status

> **This repository currently contains the project structure and documentation only.**
> Implementation of the compiler stages will be developed incrementally.

No compiler stages (lexer, parser, SSA, range analysis, quantization, etc.) have been implemented yet. The repository is set up and ready for development to begin.

## Academic Context

| | |
|---|---|
| **Course** | BCSE307L — Compiler Design |
| **Institution** | Vellore Institute of Technology, Vellore |
| **Faculty Guide** | Prof. Kanagaraj R |

### Team

| Name | Registration Number |
|---|---|
| Yash Pradhan | 24BCE0702 |
| Anjini Pandey | 24BCE0714 |
| Ishita Srivastava | 24BDS0234 |

## Review Materials

The final project review presentation and review document are stored in [`docs/review/`](docs/review/).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
