"""Unit and integration regression tests for branch-condition refinement (Phase C)."""

from fractions import Fraction
import unittest

from src.analysis.abstract_value import AbsVal
from src.analysis.refinement import refine_condition
from src.ast.types import Type
from src.ir.values import Const, Temp, Var
from src.pipeline import compile_source


class TestBranchRefinement(unittest.TestCase):
    def setUp(self):
        self.x = Var("x.1")
        self.y = Var("y.1")

    def test_refine_less_than_integer_true_edge(self):
        # x < 10 on true edge -> x <= 9
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, "<", self.x, Const(10, Type.INT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, 0)
        self.assertEqual(val.hi, 9)
        self.assertTrue(val.integral)

    def test_refine_less_than_integer_false_edge(self):
        # x < 10 on false edge -> x >= 10
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, "<", self.x, Const(10, Type.INT), is_true_edge=False)
        val = refined[self.x]
        self.assertEqual(val.lo, 10)
        self.assertEqual(val.hi, 20)
        self.assertTrue(val.integral)

    def test_refine_less_equal_integer_true_edge(self):
        # x <= 10 on true edge -> x <= 10
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, "<=", self.x, Const(10, Type.INT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, 0)
        self.assertEqual(val.hi, 10)

    def test_refine_less_equal_integer_false_edge(self):
        # x <= 10 on false edge -> x >= 11
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, "<=", self.x, Const(10, Type.INT), is_true_edge=False)
        val = refined[self.x]
        self.assertEqual(val.lo, 11)
        self.assertEqual(val.hi, 20)

    def test_refine_greater_than_integer_true_edge(self):
        # x > 5 on true edge -> x >= 6
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, ">", self.x, Const(5, Type.INT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, 6)
        self.assertEqual(val.hi, 20)

    def test_refine_greater_than_integer_false_edge(self):
        # x > 5 on false edge -> x <= 5
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, ">", self.x, Const(5, Type.INT), is_true_edge=False)
        val = refined[self.x]
        self.assertEqual(val.lo, 0)
        self.assertEqual(val.hi, 5)

    def test_refine_greater_equal_integer_true_edge(self):
        # x >= 5 on true edge -> x >= 5
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, ">=", self.x, Const(5, Type.INT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, 5)
        self.assertEqual(val.hi, 20)

    def test_refine_greater_equal_integer_false_edge(self):
        # x >= 5 on false edge -> x <= 4
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, ">=", self.x, Const(5, Type.INT), is_true_edge=False)
        val = refined[self.x]
        self.assertEqual(val.lo, 0)
        self.assertEqual(val.hi, 4)

    def test_refine_equality(self):
        # x == 7 on true edge -> x in [7, 7]
        env = {self.x: AbsVal(Fraction(0), Fraction(20), True)}
        refined = refine_condition(env, "==", self.x, Const(7, Type.INT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, 7)
        self.assertEqual(val.hi, 7)

    def test_refine_inequality_at_boundary(self):
        # x in [5, 10], x != 5 -> x in [6, 10]
        env = {self.x: AbsVal(Fraction(5), Fraction(10), True)}
        refined = refine_condition(env, "!=", self.x, Const(5, Type.INT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, 6)
        self.assertEqual(val.hi, 10)

        # x in [5, 10], x != 10 -> x in [5, 9]
        refined_hi = refine_condition(env, "!=", self.x, Const(10, Type.INT), is_true_edge=True)
        val_hi = refined_hi[self.x]
        self.assertEqual(val_hi.lo, 5)
        self.assertEqual(val_hi.hi, 9)

    def test_refine_negative_bounds(self):
        # x in [-20, 10], x > -5 -> x in [-4, 10]
        env = {self.x: AbsVal(Fraction(-20), Fraction(10), True)}
        refined = refine_condition(env, ">", self.x, Const(-5, Type.INT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, -4)
        self.assertEqual(val.hi, 10)

        # x in [-20, 10], x < -5 -> x in [-20, -6]
        refined_neg = refine_condition(env, "<", self.x, Const(-5, Type.INT), is_true_edge=True)
        val_neg = refined_neg[self.x]
        self.assertEqual(val_neg.lo, -20)
        self.assertEqual(val_neg.hi, -6)

    def test_refine_float_continuous_bounds(self):
        # Float condition x < 10.0 does NOT shift by 1
        env = {self.x: AbsVal(Fraction(0), Fraction(20), False)}
        refined = refine_condition(env, "<", self.x, Const(10.0, Type.FLOAT), is_true_edge=True)
        val = refined[self.x]
        self.assertEqual(val.lo, 0)
        self.assertEqual(val.hi, 10)
        self.assertFalse(val.integral)

    def test_refine_variable_to_variable(self):
        # x in [0, 50], y in [10, 20], condition x < y
        env = {
            self.x: AbsVal(Fraction(0), Fraction(50), True),
            self.y: AbsVal(Fraction(10), Fraction(20), True),
        }
        refined = refine_condition(env, "<", self.x, self.y, is_true_edge=True)
        # x <= 20 - 1 = 19
        self.assertEqual(refined[self.x].hi, 19)
        # y >= 0 + 1 = 1 (already >= 10, so kept 10)
        self.assertEqual(refined[self.y].lo, 10)

    def test_impossible_branch_returns_unreachable(self):
        # x in [10, 20], condition x < 5 is impossible
        env = {self.x: AbsVal(Fraction(10), Fraction(20), True)}
        refined = refine_condition(env, "<", self.x, Const(5, Type.INT), is_true_edge=True)
        self.assertTrue(refined[self.x].unreachable)

    def test_pipeline_branch_refinement_in_blocks(self):
        source = """
        int x;
        int y = 0;
        if (x < 10) {
            y = 1;
        } else {
            y = 2;
        }
        print y;
        """
        res = compile_source(source)
        self.assertTrue(res.ranges.converged)
        # block_in for then block has x <= 9
        # block_in for else block has x >= 10
        blocks = res.ssa.cfg.blocks
        cond_block = None
        for bid, blk in blocks.items():
            if any(ins.defs() and str(ins.dest).startswith("y.") for ins in blk.instrs):
                cond_block = bid
                break
        self.assertIsNotNone(cond_block)


if __name__ == "__main__":
    unittest.main()
