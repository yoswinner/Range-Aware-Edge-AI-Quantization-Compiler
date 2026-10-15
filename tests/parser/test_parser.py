"""Tests for syntax analysis (parsing) and AST construction."""

import unittest

from src.ast.nodes import (
    BinaryExpr,
    Declaration,
    Identifier,
    IfStmt,
    IntLiteral,
    Program,
    UnaryExpr,
    WhileStmt,
)
from src.diagnostics.errors import ParseError
from src.lexer.lexer import tokenize
from src.parser.parser import Parser


class TestParser(unittest.TestCase):
    def test_variable_declaration(self):
        source = "int x = 10;"
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, Declaration)
        self.assertEqual(stmt.name, "x")
        self.assertEqual(stmt.var_type.name, "INT")
        
    def test_binary_op(self):
        source = "int x = 1 + 2 * 3;"
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        expr = program.statements[0].init
        self.assertIsInstance(expr, BinaryExpr)
        self.assertEqual(expr.op, "+")
        self.assertIsInstance(expr.right, BinaryExpr)
        self.assertEqual(expr.right.op, "*")

    def test_parentheses_precedence(self):
        source = "int x = (1 + 2) * 3;"
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        expr = program.statements[0].init
        self.assertIsInstance(expr, BinaryExpr)
        self.assertEqual(expr.op, "*")
        self.assertIsInstance(expr.left, BinaryExpr)
        self.assertEqual(expr.left.op, "+")

    def test_if_else_parsing(self):
        source = "if (x > 0) { y = 1; } else { y = 2; }"
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        self.assertEqual(len(program.statements), 1)
        self.assertIsInstance(program.statements[0], IfStmt)

    def test_while_loop_parsing(self):
        source = "while (i < 10) { i = i + 1; }"
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        self.assertEqual(len(program.statements), 1)
        self.assertIsInstance(program.statements[0], WhileStmt)

    def test_unary_parsing(self):
        source = "int x = -5;"
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        expr = program.statements[0].init
        self.assertIsInstance(expr, UnaryExpr)
        self.assertEqual(expr.op, "-")

    def test_error(self):
        source = "int x = ;"
        tokens = tokenize(source)
        with self.assertRaises(ParseError):
            Parser(tokens).parse_program()


if __name__ == '__main__':
    unittest.main()
