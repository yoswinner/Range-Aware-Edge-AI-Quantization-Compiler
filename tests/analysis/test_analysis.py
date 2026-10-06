
import unittest
from src.analysis.abstract_value import AbsVal
from src.analysis.transfer import add, sub, mul, div
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
