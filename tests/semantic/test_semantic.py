"""Tests for semantic analysis, symbol table management, and type checking."""

import unittest

from src.diagnostics.errors import SemanticError
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.semantic.analyzer import check


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

    def test_duplicate_declaration_error(self):
        source = "int x = 10; int x = 20;"
        ast = Parser(tokenize(source)).parse_program()
        with self.assertRaises(SemanticError):
            check(ast)

    def test_type_mismatch_float_to_int_narrowing(self):
        source = "int x = 3.5;"
        ast = Parser(tokenize(source)).parse_program()
        with self.assertRaises(SemanticError):
            check(ast)


if __name__ == "__main__":
    unittest.main()
