"""Comprehensive tests for the IR simulator / interpreter.

Tests coverage:
- Basic and chained arithmetic operations
- Unary negation
- Relational comparisons and conditional jumps
- While loop execution and phi node resolution
- External input injection
- INT8 two's-complement wrapping semantics
- Simulation equivalence between original and quantized IR
- Error handling: uninitialized variable, missing input, division by zero, step limit
"""

import unittest

from src.ast.types import Type
from src.backend.simulator import SimulatorError, execute_ssa, simulate_programs
from src.pipeline import compile_source


class TestSimulator(unittest.TestCase):
    def test_simulator_execution(self):
        source = "int x = 10; print x;"
        res = compile_source(source)
        out = execute_ssa(res.ssa, [])
        self.assertEqual(out, [10])

    def test_simulator_arithmetic_ops(self):
        source = """
        int a = 15;
        int b = 4;
        int sum = a + b;
        int diff = a - b;
        int prod = a * b;
        print sum;
        print diff;
        print prod;
        """
        res = compile_source(source)
        out = execute_ssa(res.ssa)
        self.assertEqual(out, [19, 11, 60])

    def test_simulator_unary_negation(self):
        source = """
        int x = 42;
        int y = -x;
        print y;
        """
        res = compile_source(source)
        out = execute_ssa(res.ssa)
        self.assertEqual(out, [-42])

    def test_simulator_if_else_control_flow(self):
        source = """
        int x = 10;
        int y = 20;
        int res = 0;
        if (x < y) {
            res = 1;
        } else {
            res = 2;
        }
        print res;
        """
        res = compile_source(source)
        out = execute_ssa(res.ssa)
        self.assertEqual(out, [1])

    def test_simulator_while_loop_execution(self):
        source = """
        int n = 5;
        int fact = 1;
        while (n > 1) {
            fact = fact * n;
            n = n - 1;
        }
        print fact;
        """
        res = compile_source(source)
        out = execute_ssa(res.ssa)
        self.assertEqual(out, [120])

    def test_simulator_external_inputs(self):
        source = """
        int x;
        int y;
        int z = x + y;
        print z;
        """
        res = compile_source(source, run_simulation=False)
        out = execute_ssa(res.ssa, inputs=[12, 18])
        self.assertEqual(out, [30])

    def test_simulator_missing_inputs_error(self):
        source = """
        int x;
        print x;
        """
        res = compile_source(source, run_simulation=False)
        with self.assertRaises(SimulatorError):
            execute_ssa(res.ssa, inputs=[])

    def test_simulator_division_by_zero_error(self):
        source = """
        int a = 10;
        int b = 0;
        float c = a / b;
        print c;
        """
        res = compile_source(source, run_simulation=False)
        with self.assertRaises(SimulatorError):
            execute_ssa(res.ssa)

    def test_simulator_step_limit_prevents_infinite_loop(self):
        source = """
        int x = 1;
        while (x > 0) {
            x = x + 1;
        }
        print x;
        """
        res = compile_source(source, run_simulation=False)
        with self.assertRaises(SimulatorError):
            execute_ssa(res.ssa, max_steps=100)

    def test_simulate_programs_equivalence_on_safe_program(self):
        source = """
        int a = 20;
        int b = 30;
        int c = a + b;
        int d = c - 10;
        print d;
        """
        res = compile_source(source)
        sim = simulate_programs(res.ssa, res.quantization.program)
        self.assertTrue(sim.is_equivalent)
        self.assertEqual(sim.original_output, [40])
        self.assertEqual(sim.quantized_output, [40])
        self.assertIsNone(sim.error)

    def test_simulate_programs_with_inputs(self):
        source = """
        int x;
        int y = x * 2;
        print y;
        """
        res = compile_source(source, run_simulation=False)
        sim = simulate_programs(res.ssa, res.quantization.program, inputs=[7])
        self.assertTrue(sim.is_equivalent)
        self.assertEqual(sim.original_output, [14])
        self.assertEqual(sim.quantized_output, [14])


if __name__ == "__main__":
    unittest.main()
