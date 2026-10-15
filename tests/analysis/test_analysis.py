"""Tests for abstract range analysis transfer functions and fixed point iteration."""

from fractions import Fraction
import unittest

from src.analysis.abstract_value import AbsVal
from src.analysis.transfer import add, div, mul, sub
from src.pipeline import compile_source


class TestAnalysis(unittest.TestCase):
    def test_integrality_and_range(self):
        a = AbsVal.const(10)
        b = AbsVal.const(20)
        res = add(a, b)
        self.assertTrue(res.integral)
        self.assertEqual(res.lo, 30)
        self.assertEqual(res.hi, 30)

    def test_loop_widening(self):
        source = "int i = 0; while (i < 10) { i = i + 1; }"
        res = compile_source(source, widen_after=3)
        # Should contain loop widening
        has_unknown = any(v.is_unknown for v in res.ranges.values.values())
        self.assertTrue(has_unknown)

    def test_integrality_loss_through_fraction(self):
        a = AbsVal.const(10)
        b = AbsVal.const(Fraction(1, 2))
        res = add(a, b)
        self.assertFalse(res.integral)
        self.assertEqual(res.lo, Fraction(21, 2))

    def test_integrality_multiplication(self):
        a = AbsVal.interval(2, 5, True)
        b = AbsVal.interval(3, 4, True)
        res_int = mul(a, b)
        self.assertTrue(res_int.integral)

        c = AbsVal.interval(2, 5, False)
        res_float = mul(a, c)
        self.assertFalse(res_float.integral)

    def test_subtraction_transfer(self):
        a = AbsVal.interval(10, 20, True)
        b = AbsVal.interval(2, 5, True)
        c = sub(a, b)
        self.assertEqual(c.lo, 5)
        self.assertEqual(c.hi, 18)
        self.assertTrue(c.integral)

    def test_multiplication_transfer_all_quadrants(self):
        a = AbsVal.interval(-4, 3, True)
        b = AbsVal.interval(-2, 5, True)
        c = mul(a, b)
        self.assertEqual(c.lo, -20)
        self.assertEqual(c.hi, 15)

    def test_division_by_zero_transfer(self):
        a = AbsVal.interval(10, 20, True)
        b = AbsVal.interval(-1, 1, True)
        c = div(a, b)
        self.assertTrue(c.is_unknown)
        self.assertTrue(c.div_zero)

    def test_converging_loop_fixed_point_without_widening(self):
        # x alternates between 0 and 1, stabilizing within sweeps
        source = """
        int x = 0;
        int n = 4;
        while (n > 0) {
            x = 1 - x;
            n = n - 1;
        }
        """
        res = compile_source(source, widen_after=5)
        self.assertTrue(res.ranges.converged)
        x_facts = [f for name, f in res.ranges.values.items() if str(name).startswith("x.")]
        # x is bounded in [0, 1]
        self.assertTrue(any(f.lo == 0 and f.hi == 1 for f in x_facts))


if __name__ == "__main__":
    unittest.main()
