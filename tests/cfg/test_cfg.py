
import unittest
from src.lexer.lexer import tokenize
from src.parser.parser import Parser
from src.semantic.analyzer import check
from src.ir.lowering import generate_tac
from src.cfg.cfg import build_cfg

class TestCFG(unittest.TestCase):
    def test_cfg_building(self):
        source = "int x = 10; if (x > 0) { x = 5; } else { x = 0; }"
        ast = Parser(tokenize(source)).parse_program()
        check(ast)
        tac = generate_tac(ast)
        cfg = build_cfg(tac)
        self.assertGreater(len(cfg.blocks), 2)
