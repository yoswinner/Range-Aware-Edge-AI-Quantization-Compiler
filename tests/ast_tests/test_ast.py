
import unittest
from src.ast.nodes import IntLiteral
from src.ast.types import Type
from src.diagnostics.location import SourceLocation
from fractions import Fraction

class TestAST(unittest.TestCase):
    def test_ast_node_creation(self):
        loc = SourceLocation(1, 1)
        node = IntLiteral(loc=loc, value=Fraction(10))
        self.assertEqual(node.value, 10)
        self.assertEqual(node.loc.line, 1)
