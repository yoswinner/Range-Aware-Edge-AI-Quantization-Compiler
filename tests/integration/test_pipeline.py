"""Integration tests for the end-to-end compiler pipeline and IR simulator.

Verifies:
- Complete pipeline execution: Source -> Lex -> Parse -> TAC -> CFG -> SSA -> Range Analysis -> Quantization -> Simulation
- Equivalence between unquantized and INT8-quantized execution
- Conservative fallback on overflow, non-integral values, and loops
- Traceability of diagnostics and safety decisions
"""

import unittest
from fractions import Fraction

from src.backend.simulator import execute_ssa
from src.pipeline import compile_source
from src.quantization.safety import RejectKind


class TestPipelineAndSimulator(unittest.TestCase):
    def test_end_to_end_execution(self):
        source = """
        int x = 10;
        int y = 5;
        int z = x + y;
        print z;
        """
        result = compile_source(source)
        outputs = execute_ssa(result.ssa, [])
        self.assertEqual(outputs, [15])

    def test_quantized_execution(self):
        source = """
        int x = 100;
        int y = 20;
        int z = x + y;
        print z;
        """
        result = compile_source(source)
        quantized_prog = result.quantization.program
        outputs = execute_ssa(quantized_prog, [])
        self.assertEqual(outputs, [120])

    def test_quantized_execution_with_control_flow(self):
        source = """
        int x = 10;
        int sum = 0;
        while (x > 0) {
            sum = sum + x;
            x = x - 1;
        }
        print sum;
        """
        result = compile_source(source)
        outputs = execute_ssa(result.quantization.program, [])
        self.assertEqual(outputs, [55])

    def test_pipeline_simulation_integration(self):
        source = """
        int a = 12;
        int b = 34;
        int c = a + b;
        print c;
        """
        result = compile_source(source)
        self.assertIsNotNone(result.simulation)
        self.assertTrue(result.simulation.is_equivalent)
        self.assertEqual(result.simulation.original_output, [46])
        self.assertEqual(result.simulation.quantized_output, [46])
        self.assertIsNone(result.simulation.error)

    def test_pipeline_conservative_on_overflow(self):
        source = """
        int x = 100;
        int y = 50;
        int z = x + y;
        print z;
        """
        result = compile_source(source)
        # z is 150 > 127, must NOT be quantized
        z_var = [v for v in result.quantization.decisions if str(v).startswith("z.")][0]
        self.assertFalse(result.quantization.is_quantized(z_var))
        self.assertIn(RejectKind.OVERFLOW, result.quantization.decisions[z_var].kinds)
        # Semantics are still accurately preserved
        self.assertTrue(result.simulation.is_equivalent)
        self.assertEqual(result.simulation.original_output, [150])
        self.assertEqual(result.simulation.quantized_output, [150])

    def test_pipeline_conservative_on_non_integral(self):
        source = """
        float x = 10.0;
        float y = 3.5;
        float z = x + y;
        print z;
        """
        result = compile_source(source)
        # y (3.5) and z (13.5) have fractional parts and must NOT be quantized to INT8
        y_var = [v for v in result.quantization.decisions if str(v).startswith("y.")][0]
        z_var = [v for v in result.quantization.decisions if str(v).startswith("z.")][0]
        self.assertFalse(result.quantization.is_quantized(y_var))
        self.assertFalse(result.quantization.is_quantized(z_var))
        self.assertIn(RejectKind.NON_INTEGRAL, result.quantization.decisions[y_var].kinds)
        self.assertIn(RejectKind.NON_INTEGRAL, result.quantization.decisions[z_var].kinds)
        self.assertTrue(result.simulation.is_equivalent)
        self.assertEqual(result.simulation.original_output, [13.5])
        self.assertEqual(result.simulation.quantized_output, [13.5])

    def test_pipeline_if_else_phi_equivalence(self):
        source = """
        int x = 10;
        int y = 20;
        int max = 0;
        if (x > y) {
            max = x;
        } else {
            max = y;
        }
        print max;
        """
        result = compile_source(source)
        self.assertTrue(result.simulation.is_equivalent)
        self.assertEqual(result.simulation.original_output, [20])
        self.assertEqual(result.simulation.quantized_output, [20])

    def test_pipeline_while_loop_widening_equivalence(self):
        source = """
        int x = 5;
        int sum = 0;
        while (x > 0) {
            sum = sum + x;
            x = x - 1;
        }
        print sum;
        """
        result = compile_source(source)
        self.assertTrue(result.ranges.converged)
        self.assertTrue(result.simulation.is_equivalent)
        self.assertEqual(result.simulation.original_output, [15])
        self.assertEqual(result.simulation.quantized_output, [15])

    def test_pipeline_intermediate_overflow_blocks_downstream(self):
        source = """
        int a = 80;
        int b = 60;
        int c = a + b;
        int d = c - 100;
        print d;
        """
        result = compile_source(source)
        c_var = [v for v in result.quantization.decisions if str(v).startswith("c.")][0]
        d_var = [v for v in result.quantization.decisions if str(v).startswith("d.")][0]
        self.assertFalse(result.quantization.is_quantized(c_var))
        self.assertFalse(result.quantization.is_quantized(d_var))
        self.assertTrue(result.simulation.is_equivalent)
        self.assertEqual(result.simulation.original_output, [40])

    def test_pipeline_diagnostics_records(self):
        source = """
        int x = 10;
        int y = 20;
        int z = x + y;
        """
        result = compile_source(source)
        self.assertTrue(len(result.diagnostics) >= 3)
        names = [d.name for d in result.diagnostics]
        self.assertTrue(any("x." in n for n in names))
        self.assertTrue(any("y." in n for n in names))
        self.assertTrue(any("z." in n for n in names))


if __name__ == '__main__':
    unittest.main()
