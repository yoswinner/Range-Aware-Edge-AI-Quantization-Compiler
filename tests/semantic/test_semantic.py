
import unittest
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.semantic.analyzer import check
from src.diagnostics.errors import SemanticError

class TestSemanticAnalysis(unittest.TestCase):
    def test_valid_semantic(self):
        source = "int x = 10; int y = x + 5;"
        ast = Parser(tokenize(source)).parse_program()
        res = check(ast)
        names = [s.name for s in res.symbols]
        self.assertIn("x", names)
        self.assertIn("y", names)
        
    def test_undeclared_variable(self):
        source = "x = 10;"
        ast = Parser(tokenize(source)).parse_program()
        with self.assertRaises(SemanticError):
            check(ast)
