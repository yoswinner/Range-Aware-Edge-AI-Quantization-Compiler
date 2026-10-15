"""Comprehensive tests for INT8 safety checking and quantization transformation.

Verifies:
- Exact INT8 boundaries: [-128, 127] are SAFE; -129 and 128 are REJECTED
- Intermediate overflow: a value whose operands overflow cannot be quantized
- Non-integral rejection: float constants and computations remain unquantized
- Division and division-by-zero rejection
- Unsupported operations (relational ops, inputs)
- Retyping to INT8 in the quantized SSA program
- Preservation of original types for non-quantized values
"""

import unittest

from src.ast.types import Type
from src.pipeline import compile_source
from src.quantization.safety import INT8_MAX, INT8_MIN, RejectKind, Verdict


class TestQuantization(unittest.TestCase):
    def test_int8_safety(self):
        source = "int x = 100; int y = x + 10;"
        res = compile_source(source)
        self.assertTrue(all(d.safe for d in res.quantization.decisions.values()))
        self.assertTrue(len(res.quantization.quantized) > 0)

    def test_int8_exact_lower_boundary(self):
        # Exactly -128 is valid signed 8-bit integer
        source_safe = "int x = -128;"
        res_safe = compile_source(source_safe)
        x_dec = [d for v, d in res_safe.quantization.decisions.items() if str(v).startswith("x.")][0]
        self.assertEqual(x_dec.verdict, Verdict.SAFE)
        self.assertTrue(any(str(v).startswith("x.") for v in res_safe.quantization.quantized))

        # -129 overflows signed 8-bit range
        source_overflow = "int x = -129;"
        res_overflow = compile_source(source_overflow)
        x_dec_ov = [d for v, d in res_overflow.quantization.decisions.items() if str(v).startswith("x.")][0]
        self.assertEqual(x_dec_ov.verdict, Verdict.REJECT)
        self.assertIn(RejectKind.OVERFLOW, x_dec_ov.kinds)
        self.assertFalse(any(str(v).startswith("x.") for v in res_overflow.quantization.quantized))

    def test_int8_exact_upper_boundary(self):
        # Exactly 127 is valid signed 8-bit integer
        source_safe = "int x = 127;"
        res_safe = compile_source(source_safe)
        x_dec = [d for v, d in res_safe.quantization.decisions.items() if str(v).startswith("x.")][0]
        self.assertEqual(x_dec.verdict, Verdict.SAFE)
        self.assertTrue(any(str(v).startswith("x.") for v in res_safe.quantization.quantized))

        # 128 overflows signed 8-bit range
        source_overflow = "int x = 128;"
        res_overflow = compile_source(source_overflow)
        x_dec_ov = [d for v, d in res_overflow.quantization.decisions.items() if str(v).startswith("x.")][0]
        self.assertEqual(x_dec_ov.verdict, Verdict.REJECT)
        self.assertIn(RejectKind.OVERFLOW, x_dec_ov.kinds)
        self.assertFalse(any(str(v).startswith("x.") for v in res_overflow.quantization.quantized))

    def test_intermediate_overflow_blocks_quantization(self):
        # c = 100 + 50 = 150 (overflows INT8)
        # d = c - 50 = 100 (range fits in INT8, but operand c is not quantized)
        source = """
        int a = 100;
        int b = 50;
        int c = a + b;
        int d = c - 50;
        print d;
        """
        res = compile_source(source)
        q = res.quantization

        # Find SSA names for c and d
        c_var = [v for v in q.decisions if str(v).startswith("c.")][0]
        d_var = [v for v in q.decisions if str(v).startswith("d.")][0]

        # c must be REJECTED due to OVERFLOW
        self.assertFalse(q.decisions[c_var].safe)
        self.assertIn(RejectKind.OVERFLOW, q.decisions[c_var].kinds)
        self.assertFalse(q.is_quantized(c_var))

        # d may be within bounds, but it must be BLOCKED from quantization because c is not INT8
        self.assertFalse(q.is_quantized(d_var))
        self.assertIn(d_var, q.blocked)
        self.assertIn("not INT8-safe", q.blocked[d_var])

    def test_non_integral_float_rejected(self):
        source = """
        float x = 3.5;
        float y = x + 1.0;
        print y;
        """
        res = compile_source(source)
        q = res.quantization
        # All float variables must be rejected with NON_INTEGRAL
        for v, d in q.decisions.items():
            if str(v).startswith(("x.", "y.")):
                self.assertEqual(d.verdict, Verdict.REJECT)
                self.assertIn(RejectKind.NON_INTEGRAL, d.kinds)
        self.assertEqual(len(q.quantized), 0)

    def test_division_result_rejected_as_non_integral(self):
        source = """
        float x = 20.0;
        float y = 4.0;
        float z = x / y;
        print z;
        """
        res = compile_source(source)
        q = res.quantization
        z_var = [v for v in q.decisions if str(v).startswith("z.")][0]
        self.assertEqual(q.decisions[z_var].verdict, Verdict.REJECT)
        self.assertIn(RejectKind.NON_INTEGRAL, q.decisions[z_var].kinds)
        self.assertFalse(q.is_quantized(z_var))

    def test_division_by_zero_rejected(self):
        source = """
        float x = 10.0;
        float y = 0.0;
        float z = x / y;
        print z;
        """
        res = compile_source(source)
        q = res.quantization
        z_var = [v for v in q.decisions if str(v).startswith("z.")][0]
        self.assertEqual(q.decisions[z_var].verdict, Verdict.REJECT)
        self.assertIn(RejectKind.DIV_BY_ZERO, q.decisions[z_var].kinds)
        self.assertFalse(q.is_quantized(z_var))

    def test_uninitialized_input_rejected_unknown_range(self):
        source = """
        int x;
        int y = x + 5;
        print y;
        """
        res = compile_source(source)
        q = res.quantization
        x_var = [v for v in q.decisions if str(v).startswith("x.")][0]
        self.assertEqual(q.decisions[x_var].verdict, Verdict.REJECT)
        self.assertIn(RejectKind.UNKNOWN_RANGE, q.decisions[x_var].kinds)
        self.assertFalse(q.is_quantized(x_var))

    def test_retyped_instructions_in_quantized_program(self):
        source = """
        int a = 10;
        int b = 20;
        int c = a + b;
        print c;
        """
        res = compile_source(source)
        quant_prog = res.quantization.program
        # In quantized program, c's instruction must have dest_type == INT8
        c_var = [v for v in res.quantization.quantized if str(v).startswith("c.")][0]
        _, instr = quant_prog.defs[c_var]
        self.assertEqual(instr.dest_type, Type.INT8)

    def test_unquantized_variables_preserve_original_type(self):
        source = """
        int a = 200;
        int b = 50;
        int c = a + b;
        print c;
        """
        res = compile_source(source)
        quant_prog = res.quantization.program
        c_var = [v for v in res.quantization.decisions if str(v).startswith("c.")][0]
        _, instr = quant_prog.defs[c_var]
        self.assertEqual(instr.dest_type, Type.INT)


if __name__ == "__main__":
    unittest.main()
