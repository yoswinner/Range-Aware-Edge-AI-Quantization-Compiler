"""Unit and regression tests for loop analysis, widening, and narrowing (Phase D)."""

import unittest

from src.pipeline import compile_source


class TestLoopNarrowing(unittest.TestCase):
    def test_increasing_counter_bounded_with_narrowing(self):
        source = """
        int i = 0;
        while (i < 10) {
            i = i + 1;
        }
        print i;
        """
        # With narrow=True, i should narrow to [0, 10]
        res = compile_source(source, widen_after=3, narrow=True)
        self.assertTrue(res.ranges.converged)
        i_header = [f for name, f in res.ranges.values.items() if str(name).startswith("i.2")]
        self.assertTrue(len(i_header) > 0)
        fact = i_header[0]
        self.assertFalse(fact.is_unknown)
        self.assertEqual(fact.lo, 0)
        self.assertEqual(fact.hi, 10)
        self.assertTrue(fact.integral)
        self.assertTrue(res.simulation.is_equivalent)
        self.assertEqual(res.simulation.original_output, [10])

    def test_decreasing_counter_bounded_with_narrowing(self):
        source = """
        int i = 10;
        while (i > 0) {
            i = i - 1;
        }
        print i;
        """
        res = compile_source(source, widen_after=3, narrow=True)
        self.assertTrue(res.ranges.converged)
        i_header = [f for name, f in res.ranges.values.items() if str(name).startswith("i.2")]
        self.assertTrue(len(i_header) > 0)
        fact = i_header[0]
        self.assertFalse(fact.is_unknown)
        self.assertEqual(fact.lo, 0)
        self.assertEqual(fact.hi, 10)
        self.assertTrue(res.simulation.is_equivalent)
        self.assertEqual(res.simulation.original_output, [0])

    def test_loop_traversing_negative_values(self):
        source = """
        int i = -10;
        while (i < 0) {
            i = i + 1;
        }
        print i;
        """
        res = compile_source(source, widen_after=3, narrow=True)
        self.assertTrue(res.ranges.converged)
        i_header = [f for name, f in res.ranges.values.items() if str(name).startswith("i.2")]
        self.assertTrue(len(i_header) > 0)
        fact = i_header[0]
        self.assertFalse(fact.is_unknown)
        self.assertEqual(fact.lo, -10)
        self.assertEqual(fact.hi, 0)
        self.assertTrue(res.simulation.is_equivalent)
        self.assertEqual(res.simulation.original_output, [0])

    def test_oscillating_loop_converges_without_widening(self):
        source = """
        int x = 0;
        int n = 6;
        while (n > 0) {
            x = 1 - x;
            n = n - 1;
        }
        print x;
        """
        res = compile_source(source, widen_after=5, narrow=False)
        self.assertTrue(res.ranges.converged)
        x_facts = [f for name, f in res.ranges.values.items() if str(name).startswith("x.")]
        # Oscillating value stays within [0, 1]
        self.assertTrue(any(f.lo == 0 and f.hi == 1 for f in x_facts))
        self.assertTrue(res.simulation.is_equivalent)

    def test_unconstrained_expanding_loop_remains_unknown(self):
        source = """
        int i = 0;
        int sum = 0;
        while (i < 50) {
            sum = sum + i;
            i = i + 1;
        }
        print sum;
        """
        # sum has no guard constraining its bound; must remain UNKNOWN
        res = compile_source(source, widen_after=3, narrow=True)
        self.assertTrue(res.ranges.converged)
        sum_facts = [f for name, f in res.ranges.values.items() if str(name).startswith("sum.")]
        # sum.2 and sum.3 must be unknown/unbounded
        has_unknown_sum = any(f.is_unknown for f in sum_facts)
        self.assertTrue(has_unknown_sum)
        # Loop variables sum.2 and sum.3 must NOT be quantized
        sum_loop_quantized = any(str(v) in ("sum.2", "sum.3") for v in res.quantization.quantized)
        self.assertFalse(sum_loop_quantized)
        self.assertTrue(res.simulation.is_equivalent)

    def test_widen_after_variation(self):
        source = """
        int i = 0;
        while (i < 20) {
            i = i + 1;
        }
        print i;
        """
        # widen_after 1 terminates in fewer sweeps than widen_after 5
        res1 = compile_source(source, widen_after=1, narrow=False)
        res5 = compile_source(source, widen_after=5, narrow=False)
        self.assertTrue(res1.ranges.converged)
        self.assertTrue(res5.ranges.converged)
        self.assertLess(res1.ranges.sweeps, res5.ranges.sweeps)


if __name__ == "__main__":
    unittest.main()
