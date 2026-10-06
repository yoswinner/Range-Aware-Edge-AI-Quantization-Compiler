
import unittest
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.semantic.analyzer import check
from src.ir.lowering import generate_tac
from src.cfg.cfg import build_cfg
from src.ssa.construction import build_ssa
from src.ir.tac import Phi

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
