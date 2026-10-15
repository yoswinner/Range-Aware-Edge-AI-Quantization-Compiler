"""Tests for Control Flow Graph (CFG) and Basic Block construction."""

import unittest

from src.cfg.cfg import build_cfg
from src.ir.lowering import generate_tac
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.semantic.analyzer import check


class TestCFG(unittest.TestCase):
    def test_cfg_building(self):
        source = "int x = 10; if (x > 0) { x = 5; } else { x = 0; }"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        cfg = build_cfg(tac)
        self.assertGreater(len(cfg.blocks), 2)

    def test_cfg_straight_line_code(self):
        source = "int x = 1; int y = 2; int z = x + y;"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        cfg = build_cfg(tac)
        # Entry synthetic block B0 + real block B1
        self.assertEqual(len(cfg.blocks), 2)
        self.assertIn(cfg.entry, cfg.blocks)

    def test_cfg_while_loop_back_edge(self):
        source = "int i = 0; while (i < 5) { i = i + 1; }"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        cfg = build_cfg(tac)
        # Verify back_edges() method returns at least one back edge (loop)
        self.assertTrue(len(cfg.back_edges()) > 0)

    def test_cfg_reverse_postorder(self):
        source = "int x = 10; if (x > 5) { x = 20; } else { x = 30; } int y = x;"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        cfg = build_cfg(tac)
        rpo = cfg.reverse_postorder()
        self.assertEqual(rpo[0], cfg.entry)
        self.assertEqual(len(rpo), len(cfg.blocks))


if __name__ == "__main__":
    unittest.main()
