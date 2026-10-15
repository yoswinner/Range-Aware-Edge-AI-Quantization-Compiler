"""Regression tests for exact INT8 boundaries, intermediate overflow, integrality, and retyping (Phase F)."""

from fractions import Fraction
import unittest

from src.analysis.abstract_value import AbsVal
from src.ast.types import Type
from src.pipeline import compile_source
from src.quantization.safety import RejectKind, check_int8_safety


class TestSafetyEdgeCases(unittest.TestCase):
    def test_exact_signed_int8_lower_boundary_minus_128(self):
        val = AbsVal(Fraction(-128), Fraction(0), True)
        decision = check_int8_safety(val, True, "copy")
        self.assertTrue(decision.safe)

    def test_exact_signed_int8_upper_boundary_127(self):
        val = AbsVal(Fraction(0), Fraction(127), True)
        decision = check_int8_safety(val, True, "copy")
        self.assertTrue(decision.safe)

    def test_boundary_overflow_minus_129(self):
        val = AbsVal(Fraction(-129), Fraction(0), True)
        decision = check_int8_safety(val, True, "copy")
        self.assertFalse(decision.safe)
        self.assertIn(RejectKind.OVERFLOW, decision.kinds)

    def test_boundary_overflow_128(self):
        val = AbsVal(Fraction(0), Fraction(128), True)
        decision = check_int8_safety(val, True, "copy")
        self.assertFalse(decision.safe)
        self.assertIn(RejectKind.OVERFLOW, decision.kinds)

    def test_fractional_value_rejected_even_if_in_bounds(self):
        # Range [10, 20] but non-integral
        val = AbsVal(Fraction(10), Fraction(20), False)
        decision = check_int8_safety(val, True, "copy")
        self.assertFalse(decision.safe)
        self.assertIn(RejectKind.NON_INTEGRAL, decision.kinds)

    def test_division_by_zero_propagated_to_reject(self):
        val = AbsVal(Fraction(5), Fraction(10), True, div_zero=True)
        decision = check_int8_safety(val, True, "copy")
        self.assertFalse(decision.safe)
        self.assertIn(RejectKind.DIV_BY_ZERO, decision.kinds)

    def test_unreachable_value_rejected(self):
        val = AbsVal.bot()
        decision = check_int8_safety(val, True, "copy")
        self.assertFalse(decision.safe)

    def test_intermediate_overflow_blocks_downstream_quantization(self):
        source = """
        int a = 100;
        int b = 50;
        int c = a + b;
        int d = c - 50;
        print d;
        """
        res = compile_source(source)
        # a and b fit INT8
        # c overflows INT8 (150 > 127)
        # d mathematically equals 100, but depends on c which was not quantized!
        # d must be blocked!
        c_name = [v for v in res.quantization.decisions if str(v).startswith("c.")][0]
        d_name = [v for v in res.quantization.decisions if str(v).startswith("d.")][0]

        self.assertFalse(res.quantization.decisions[c_name].safe)
        self.assertNotIn(c_name, res.quantization.quantized)

        self.assertTrue(res.quantization.decisions[d_name].safe)
        self.assertNotIn(d_name, res.quantization.quantized)
        self.assertIn(d_name, res.quantization.blocked)

    def test_unquantized_variables_preserve_original_type(self):
        source = """
        float x = 10.0;
        float y = 5.0;
        float z = x + y;
        print z;
        """
        res = compile_source(source)
        quant_prog = res.quantization.program
        for _, instr in quant_prog.instructions():
            if hasattr(instr, "dest_type"):
                self.assertEqual(instr.dest_type, Type.FLOAT)


if __name__ == "__main__":
    unittest.main()
