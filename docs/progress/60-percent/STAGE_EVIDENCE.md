# Stage Evidence

| Stage | Status | Source Files | Tests | Actual Evidence | Limitations |
|------|--------|--------------|-------|------------------|-------------|
| Lexer | IMPLEMENTED | `src/lexer/lexer.py`, `src/lexer/tokens.py` | `tests/lexer/test_lexer.py` | Tokenizes integer/float literals, keywords, identifiers. Line/col attached. | Only basic ASCII characters supported. |
| Parser | IMPLEMENTED | `src/parser/parser.py` | `tests/parser/test_parser.py` | Parses while, if/else, declarations, assignments, binary ops. | Does not support unary operations aside from simple negation. |
| AST | IMPLEMENTED | `src/ast/nodes.py`, `src/ast/printer.py`, `src/ast/types.py` | `tests/ast/test_ast.py` | Strongly typed nodes storing source locations. | No support for arrays or structs. |
| Semantic Analysis | IMPLEMENTED | `src/semantic/analyzer.py`, `src/semantic/symbols.py` | `tests/semantic/test_semantic.py` | Resolves names to symbols, enforces types (int vs float). | Strict scope rules, does not permit shadowing. |
| TAC | IMPLEMENTED | `src/ir/lowering.py`, `src/ir/tac.py`, `src/ir/values.py` | `tests/ir/test_tac.py` | Flattens expressions to 3-address format using temporaries. | Does not attempt expression re-association. |
| CFG | IMPLEMENTED | `src/cfg/cfg.py`, `src/cfg/dominators.py` | `tests/cfg/test_cfg.py` | Computes basic blocks, back-edges, post-order traversals. |  |
| SSA | IMPLEMENTED | `src/ssa/construction.py`, `src/ssa/verify.py` | `tests/ssa/test_ssa.py` | Inserts `Phi` nodes using iterated dominance frontiers, renames versions. |  |
| Range Analysis | IMPLEMENTED | `src/analysis/range_analysis.py`, `src/analysis/transfer.py` | `tests/analysis/test_analysis.py` | Implements interval rules over `+`, `-`, `*`, `/`. | Relies on integer-specific truncation for limits. |
| Integrality Analysis | IMPLEMENTED | `src/analysis/transfer.py`, `src/analysis/abstract_value.py` | `tests/analysis/test_analysis.py` | Boolean flag AND tracking. Safely invalidates on division. |  |
| Loop/Widening | IMPLEMENTED | `src/analysis/range_analysis.py` | `tests/analysis/test_analysis.py` | Widen to UNKNOWN if range does not stabilize within 3 sweeps. | If a loop reaches UNKNOWN due to widening, this causes a conservative rejection consistent with the safety-first design. |
| INT8 Safety | IMPLEMENTED | `src/quantization/safety.py` | `tests/quantization/test_quantization.py` | Rejects bounds `< -128` or `> 127`, zero divisions, UNKNOWNs. | Unsupported quantization operations such as relational comparisons are strictly rejected as a current scope/implementation limitation. |
| Quantization | IMPLEMENTED | `src/quantization/quantizer.py` | `tests/quantization/test_quantization.py` | Performs `INT8` type conversion recursively on operations proven SAFE. | Only applies to proven basic arithmetic, avoiding control flow headers. |
| Simulator | IMPLEMENTED | `src/backend/simulator.py` | `tests/backend/test_simulator.py` | Executes TAC instruction set, accurately wrapping constraints. | No memory simulation; strictly register/stack evaluation for demonstration. |

This milestone represents a coherent compiler core implementation designed to prove static INT8 safety.


## Current Limitations
- **Loop Widening**: Loop widening may conservatively produce UNKNOWN if the range does not stabilize, leading to safe rejection.
- **Unsupported Operations**: Unsupported operations (such as relational comparisons) are safely rejected by the quantization pass.
- **Backend Simulator**: The backend is an IR-walking simulator, not hardware code generation.
- **Performance Evaluation**: Runtime and energy improvements have not been measured.
