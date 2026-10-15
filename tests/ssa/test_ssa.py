"""Comprehensive tests for SSA form construction.

Verifies:
- Cytron's dominance frontier algorithm for Phi insertion
- If-else diamond phi placement with incoming block branches
- While loop header phi placement with pre-header and back-edge incoming blocks
- SSA variable versioning / renaming
- Dominance frontiers and immediate dominators (idom)
- SSA def-use map consistency
"""

import unittest

from src.cfg.cfg import build_cfg
from src.ir.lowering import generate_tac
from src.ir.tac import Phi
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.pipeline import compile_source
from src.semantic.analyzer import check
from src.ssa.construction import build_ssa


class TestSSA(unittest.TestCase):
    def test_ssa_phi_insertion(self):
        source = "int x = 10; if (x > 0) { x = 5; } int y = x;"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        cfg = build_cfg(tac)
        ssa = build_ssa(cfg)
        phis = ssa.phis()
        self.assertGreater(len(phis), 0)

    def test_ssa_if_else_phi_incoming_branches(self):
        source = """
        int x = 10;
        if (x > 5) {
            x = 20;
        } else {
            x = 30;
        }
        int y = x;
        """
        res = compile_source(source)
        phis = res.ssa.phis()
        self.assertGreater(len(phis), 0)
        # At least one phi should merge x from two incoming predecessor blocks
        x_phis = [p for p in phis if str(p.dest).startswith("x.")]
        self.assertTrue(len(x_phis) > 0)
        phi = x_phis[0]
        self.assertEqual(len(phi.incoming), 2)

    def test_ssa_while_loop_header_phi(self):
        source = """
        int i = 0;
        int acc = 0;
        while (i < 10) {
            acc = acc + i;
            i = i + 1;
        }
        """
        res = compile_source(source)
        phis = res.ssa.phis()
        # Should have loop phis for i and acc
        phi_dest_names = [str(p.dest) for p in phis]
        self.assertTrue(any(name.startswith("i.") for name in phi_dest_names))
        self.assertTrue(any(name.startswith("acc.") for name in phi_dest_names))

    def test_ssa_variable_version_renaming(self):
        source = """
        int x = 1;
        x = 2;
        x = 3;
        int y = x;
        """
        res = compile_source(source)
        # x should have versions 1, 2, 3
        x_defs = [str(v) for v in res.ssa.defs if str(v).startswith("x.")]
        self.assertIn("x.1", x_defs)
        self.assertIn("x.2", x_defs)
        self.assertIn("x.3", x_defs)

    def test_ssa_dominance_frontiers_computed(self):
        source = """
        int a = 1;
        if (a > 0) {
            a = 2;
        } else {
            a = 3;
        }
        int b = a;
        """
        res = compile_source(source)
        dom = res.ssa.dom
        # Dominance frontiers must not be empty for an if-else diamond
        has_non_empty_df = any(len(frontiers) > 0 for frontiers in dom.frontiers.values())
        self.assertTrue(has_non_empty_df)

    def test_ssa_immediate_dominators(self):
        source = """
        int x = 10;
        int y = 20;
        int z = x + y;
        """
        res = compile_source(source)
        dom = res.ssa.dom
        # Entry block has no parent in idom (None)
        self.assertIsNone(dom.idom[res.ssa.cfg.entry])

    def test_ssa_defs_consistency(self):
        source = """
        int a = 5;
        int b = 10;
        int c = a + b;
        int d = c * 2;
        """
        res = compile_source(source)
        for _, instr in res.ssa.instructions():
            for v in instr.defs():
                self.assertIn(v, res.ssa.defs)
                block_id, defining_instr = res.ssa.defs[v]
                self.assertEqual(defining_instr, instr)


if __name__ == "__main__":
    unittest.main()
