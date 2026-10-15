"""Comprehensive tests for abstract range analysis, interval transfer functions,
integrality tracking, join operations, and fixed-point iteration with loop widening.
"""

from fractions import Fraction
import unittest

from src.analysis.abstract_value import AbsVal
from src.analysis.range_analysis import DEFAULT_WIDEN_AFTER, analyze_ranges
from src.analysis.transfer import add, compare, div, mul, neg, sub
from src.ast.types import Type
from src.pipeline import compile_source


class TestAbstractValueAndTransfer(unittest.TestCase):
    """Unit tests for interval arithmetic and abstract value transfer functions."""

    def test_interval_addition_positive(self):
        a = AbsVal.interval(10, 20, True)
        b = AbsVal.interval(5, 15, True)
        c = add(a, b)
        self.assertEqual(c.lo, Fraction(15))
        self.assertEqual(c.hi, Fraction(35))
        self.assertTrue(c.integral)
        self.assertFalse(c.is_unknown)

    def test_interval_addition_mixed_signs(self):
        a = AbsVal.interval(-20, 10, True)
        b = AbsVal.interval(-5, 15, True)
        c = add(a, b)
        self.assertEqual(c.lo, Fraction(-25))
        self.assertEqual(c.hi, Fraction(25))
        self.assertTrue(c.integral)

    def test_interval_subtraction(self):
        a = AbsVal.interval(10, 20, True)
        b = AbsVal.interval(5, 10, True)
        c = sub(a, b)
        self.assertEqual(c.lo, Fraction(0))
        self.assertEqual(c.hi, Fraction(15))
        self.assertTrue(c.integral)

    def test_interval_subtraction_negative(self):
        a = AbsVal.interval(0, 10, True)
        b = AbsVal.interval(-10, -5, True)
        c = sub(a, b)
        self.assertEqual(c.lo, Fraction(5))
        self.assertEqual(c.hi, Fraction(20))
        self.assertTrue(c.integral)

    def test_interval_multiplication_positive(self):
        a = AbsVal.interval(2, 5, True)
        b = AbsVal.interval(3, 4, True)
        c = mul(a, b)
        self.assertEqual(c.lo, Fraction(6))
        self.assertEqual(c.hi, Fraction(20))
        self.assertTrue(c.integral)

    def test_interval_multiplication_mixed_cross_product(self):
        a = AbsVal.interval(-3, 4, True)
        b = AbsVal.interval(-2, 5, True)
        c = mul(a, b)
        # Products: (-3)*(-2)=6, (-3)*5=-15, 4*(-2)=-8, 4*5=20
        self.assertEqual(c.lo, Fraction(-15))
        self.assertEqual(c.hi, Fraction(20))
        self.assertTrue(c.integral)

    def test_interval_multiplication_both_negative(self):
        a = AbsVal.interval(-5, -2, True)
        b = AbsVal.interval(-4, -3, True)
        c = mul(a, b)
        self.assertEqual(c.lo, Fraction(6))
        self.assertEqual(c.hi, Fraction(20))
        self.assertTrue(c.integral)

    def test_interval_multiplication_zero_crossing(self):
        a = AbsVal.interval(-10, 10, True)
        b = AbsVal.interval(0, 5, True)
        c = mul(a, b)
        self.assertEqual(c.lo, Fraction(-50))
        self.assertEqual(c.hi, Fraction(50))
        self.assertTrue(c.integral)

    def test_interval_negation(self):
        a = AbsVal.interval(5, 10, True)
        c = neg(a)
        self.assertEqual(c.lo, Fraction(-10))
        self.assertEqual(c.hi, Fraction(-5))
        self.assertTrue(c.integral)

    def test_interval_negation_crossing_zero(self):
        a = AbsVal.interval(-3, 8, True)
        c = neg(a)
        self.assertEqual(c.lo, Fraction(-8))
        self.assertEqual(c.hi, Fraction(3))
        self.assertTrue(c.integral)

    def test_division_strictly_positive(self):
        a = AbsVal.interval(20, 40, True)
        b = AbsVal.interval(2, 4, True)
        c = div(a, b)
        self.assertEqual(c.lo, Fraction(5))
        self.assertEqual(c.hi, Fraction(20))
        self.assertFalse(c.integral, "Division is never guaranteed integral")
        self.assertFalse(c.div_zero)
        self.assertFalse(c.is_unknown)

    def test_division_strictly_negative_divisor(self):
        a = AbsVal.interval(20, 40, True)
        b = AbsVal.interval(-4, -2, True)
        c = div(a, b)
        self.assertEqual(c.lo, Fraction(-20))
        self.assertEqual(c.hi, Fraction(-5))
        self.assertFalse(c.integral)
        self.assertFalse(c.div_zero)

    def test_division_by_zero_divisor_contains_zero(self):
        a = AbsVal.interval(10, 20, True)
        b = AbsVal.interval(0, 5, True)
        c = div(a, b)
        self.assertTrue(c.is_unknown)
        self.assertTrue(c.div_zero)
        self.assertIn("contains 0", c.reason)

    def test_division_by_zero_divisor_straddles_zero(self):
        a = AbsVal.interval(10, 20, True)
        b = AbsVal.interval(-2, 3, True)
        c = div(a, b)
        self.assertTrue(c.is_unknown)
        self.assertTrue(c.div_zero)

    def test_division_by_unknown_divisor(self):
        a = AbsVal.interval(10, 20, True)
        b = AbsVal.unknown(True, "unknown divisor")
        c = div(a, b)
        self.assertTrue(c.is_unknown)
        self.assertTrue(c.div_zero)

    def test_division_unknown_dividend_known_safe_divisor(self):
        a = AbsVal.unknown(True, "unknown dividend")
        b = AbsVal.interval(2, 4, True)
        c = div(a, b)
        self.assertTrue(c.is_unknown)
        self.assertFalse(c.div_zero)

    def test_relational_comparisons(self):
        a = AbsVal.interval(1, 3, True)
        b = AbsVal.interval(5, 8, True)
        # Definitely true: a < b
        c_lt = compare("<", a, b)
        self.assertEqual(c_lt.lo, Fraction(1))
        self.assertEqual(c_lt.hi, Fraction(1))
        self.assertTrue(c_lt.integral)

        # Definitely false: a > b
        c_gt = compare(">", a, b)
        self.assertEqual(c_gt.lo, Fraction(0))
        self.assertEqual(c_gt.hi, Fraction(0))
        self.assertTrue(c_gt.integral)

        # Overlapping: uncertain
        overlap = AbsVal.interval(2, 6, True)
        c_overlap = compare("<", a, overlap)
        self.assertEqual(c_overlap.lo, Fraction(0))
        self.assertEqual(c_overlap.hi, Fraction(1))
        self.assertTrue(c_overlap.integral)

    def test_join_intervals(self):
        a = AbsVal.interval(1, 5, True)
        b = AbsVal.interval(3, 10, True)
        j = a.join(b)
        self.assertEqual(j.lo, Fraction(1))
        self.assertEqual(j.hi, Fraction(10))
        self.assertTrue(j.integral)

    def test_join_integrality_conservative(self):
        a = AbsVal.interval(1, 5, True)
        b = AbsVal.interval(2, 8, False)
        j = a.join(b)
        self.assertFalse(j.integral, "Join with non-integral must be non-integral")

    def test_join_with_unknown(self):
        a = AbsVal.interval(1, 5, True)
        b = AbsVal.unknown(True, "reason b")
        j = a.join(b)
        self.assertTrue(j.is_unknown)

    def test_join_preserves_div_zero_flag(self):
        a = AbsVal.unknown(False, "div by zero", div_zero=True)
        b = AbsVal.interval(1, 5, True)
        j = a.join(b)
        self.assertTrue(j.div_zero)


class TestProgramRangeAnalysis(unittest.TestCase):
    """Integration tests for range analysis on SSA programs."""

    def test_arithmetic_constant_propagation_ranges(self):
        source = """
        int a = 10;
        int b = 25;
        int c = a + b;
        int d = c * 2;
        print d;
        """
        res = compile_source(source)
        # Find c and d definitions in SSA
        values = res.ranges.values
        names = {str(k): v for k, v in values.items()}
        # Verify c is [35, 35] and d is [70, 70]
        c_facts = [fact for name, fact in names.items() if name.startswith("c.")]
        d_facts = [fact for name, fact in names.items() if name.startswith("d.")]
        self.assertTrue(len(c_facts) > 0)
        self.assertTrue(len(d_facts) > 0)
        self.assertEqual(c_facts[0].lo, 35)
        self.assertEqual(c_facts[0].hi, 35)
        self.assertEqual(d_facts[0].lo, 70)
        self.assertEqual(d_facts[0].hi, 70)

    def test_conditional_branch_phi_join_range(self):
        source = """
        int x = 10;
        int y = 0;
        if (x > 5) {
            y = 20;
        } else {
            y = 50;
        }
        print y;
        """
        res = compile_source(source)
        # y should join 20 and 50 to [20, 50]
        y_facts = [fact for name, fact in res.ranges.values.items() if str(name).startswith("y.")]
        self.assertTrue(any(f.lo <= 20 and f.hi >= 50 and f.integral for f in y_facts))

    def test_loop_widening_terminates_and_widens(self):
        source = """
        int i = 0;
        int sum = 0;
        while (i < 100) {
            sum = sum + i;
            i = i + 1;
        }
        print sum;
        """
        res = compile_source(source, widen_after=3)
        self.assertTrue(res.ranges.converged)
        self.assertTrue(len(res.ranges.widened) > 0)
        # Sum and i should be widened to UNKNOWN
        has_widened_unknown = any(f.is_unknown for f in res.ranges.values.values())
        self.assertTrue(has_widened_unknown)

    def test_loop_widening_custom_widen_after(self):
        source = """
        int i = 0;
        while (i < 50) {
            i = i + 2;
        }
        """
        res1 = compile_source(source, widen_after=1)
        res5 = compile_source(source, widen_after=5)
        self.assertTrue(res1.ranges.converged)
        self.assertTrue(res5.ranges.converged)
        self.assertLess(res1.ranges.sweeps, res5.ranges.sweeps)

    def test_uninitialized_input_is_unknown(self):
        source = """
        int x;
        int y = x + 10;
        print y;
        """
        res = compile_source(source)
        # x is an input with unknown range
        x_facts = [f for name, f in res.ranges.values.items() if str(name).startswith("x.")]
        self.assertTrue(all(f.is_unknown for f in x_facts))
        # y = x + 10 must also be unknown
        y_facts = [f for name, f in res.ranges.values.items() if str(name).startswith("y.")]
        self.assertTrue(all(f.is_unknown for f in y_facts))

    def test_division_by_zero_flagged_in_pipeline(self):
        source = """
        int a = 10;
        int b = 0;
        float c = a / b;
        """
        res = compile_source(source)
        c_facts = [f for name, f in res.ranges.values.items() if str(name).startswith("c.")]
        self.assertTrue(len(c_facts) > 0)
        self.assertTrue(c_facts[0].div_zero)


if __name__ == "__main__":
    unittest.main()
