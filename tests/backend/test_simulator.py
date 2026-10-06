
import unittest
from src.pipeline import compile_source
from src.backend.simulator import execute_ssa

class TestSimulator(unittest.TestCase):
    def test_simulator_execution(self):
        source = "int x = 10; print x;"
        res = compile_source(source)
        out = execute_ssa(res.ssa, [])
        self.assertEqual(out, [10])
