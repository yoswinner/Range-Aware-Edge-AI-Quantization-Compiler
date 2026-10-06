
import unittest
from src.pipeline import compile_source

class TestQuantization(unittest.TestCase):
    def test_int8_safety(self):
        source = "int x = 100; int y = x + 10;"
        res = compile_source(source)
        self.assertTrue(all(d.safe for d in res.quantization.decisions.values()))
        self.assertTrue(len(res.quantization.quantized) > 0)
