
import unittest
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.semantic.analyzer import check
from src.ir.lowering import generate_tac

class TestTAC(unittest.TestCase):
    def test_tac_generation(self):
        source = "int x = 10; int y = x + 5;"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        self.assertTrue(len(tac.instrs) > 0)
        self.assertIn("x", tac.symbols)
