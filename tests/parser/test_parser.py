import unittest
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.ast.nodes import Program, Declaration, BinaryExpr, Identifier, IntLiteral
from src.diagnostics.errors import ParseError

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

    def test_error(self):
        source = "int x = ;"
        tokens = tokenize(source)
        with self.assertRaises(ParseError):
            Parser(tokens).parse_program()

if __name__ == '__main__':
    unittest.main()
