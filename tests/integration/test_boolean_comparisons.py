"""Integration tests for comparison operators and boolean semantics (Phase E)."""

import unittest

from src.ast.types import Type
from src.pipeline import compile_source


class TestBooleanComparisons(unittest.TestCase):
    def test_all_relational_operators_in_conditions(self):
        operators = ["<", "<=", ">", ">=", "==", "!="]
        for op in operators:
            source = f"""
            int a = 10;
            int b = 20;
            int r = 0;
            if (a {op} b) {{
                r = 1;
            }} else {{
                r = 2;
            }}
            print r;
            """
            res = compile_source(source)
            self.assertTrue(res.ranges.converged, f"Failed for operator {op}")
            self.assertTrue(res.simulation.is_equivalent, f"Simulation mismatch for operator {op}")

    def test_comparison_result_is_boolean_and_not_arithmetic_int8(self):
        source = """
        int a = 10;
        int b = 20;
        int r = 0;
        if (a < b) {
            r = 100;
        }
        print r;
        """
        res = compile_source(source)
        # Find temporary holding the boolean comparison
        bool_temps = [
            v for v, (_, ins) in res.ssa.defs.items()
            if hasattr(ins, "op") and ins.op == "<"
        ]
        self.assertTrue(len(bool_temps) > 0)
        t = bool_temps[0]
        # Comparison produces Type.BOOL
        self.assertEqual(res.ssa.defs[t][1].dest_type, Type.BOOL)
        # Relational comparison operation is NOT quantized to INT8 arithmetic
        self.assertNotIn(t, res.quantization.quantized)
        self.assertTrue(res.simulation.is_equivalent)
        self.assertEqual(res.simulation.quantized_output, [100])


if __name__ == "__main__":
    unittest.main()
