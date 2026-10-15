"""Tests for Three-Address Code (TAC) intermediate representation generation."""

import unittest

from src.ir.lowering import generate_tac
from src.ir.tac import BinOp, CondJump, Jump, Label, Print, UnOp
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.semantic.analyzer import check


class TestTAC(unittest.TestCase):
    def test_tac_generation(self):
        source = "int x = 10; int y = x + 5;"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        self.assertTrue(len(tac.instrs) > 0)
        self.assertIn("x", tac.symbols)

    def test_tac_if_else_control_flow(self):
        source = "int a = 1; if (a > 0) { a = 2; } else { a = 3; }"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        has_cond_jump = any(isinstance(i, CondJump) for i in tac.instrs)
        has_jump = any(isinstance(i, Jump) for i in tac.instrs)
        has_label = any(isinstance(i, Label) for i in tac.instrs)
        self.assertTrue(has_cond_jump)
        self.assertTrue(has_jump)
        self.assertTrue(has_label)

    def test_tac_while_loop(self):
        source = "int i = 0; while (i < 10) { i = i + 1; }"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        labels = [i for i in tac.instrs if isinstance(i, Label)]
        self.assertGreaterEqual(len(labels), 2)

    def test_tac_unary_and_print(self):
        source = "int x = 5; int y = -x; print y;"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        has_unop = any(isinstance(i, UnOp) and i.op == "neg" for i in tac.instrs)
        has_print = any(isinstance(i, Print) for i in tac.instrs)
        self.assertTrue(has_unop)
        self.assertTrue(has_print)


if __name__ == "__main__":
    unittest.main()
