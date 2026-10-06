import unittest
from fractions import Fraction
from src.pipeline import compile_source
from src.backend.simulator import execute_ssa

class TestPipelineAndSimulator(unittest.TestCase):
    def test_end_to_end_execution(self):
        source = """
        int x = 10;
        int y = 5;
        int z = x + y;
        print z;
        """
        result = compile_source(source)
        # Execute the original unquantized IR
        outputs = execute_ssa(result.ssa, [])
        self.assertEqual(outputs, [15])

    def test_quantized_execution(self):
        source = """
        int x = 100;
        int y = 20;
        int z = x + y;
        print z;
        """
        # 100 + 20 = 120 which is within [-128, 127], so z is INT8 safe
        result = compile_source(source)
        # Verify it got quantized
        # z will be in result.quantization.quantized
        # We find the name of 'z' inside the symbols. 
        # Actually we just execute the quantized program and verify the output.
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

if __name__ == '__main__':
    unittest.main()
