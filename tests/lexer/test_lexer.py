import unittest
from fractions import Fraction
from src.lexer.tokens import TokenKind
from src.lexer.lexer import tokenize
from src.diagnostics.errors import LexError

class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        source = "int x = 10;"
        tokens = tokenize(source)
        self.assertEqual(len(tokens), 6) # 5 tokens + EOF
        self.assertEqual(tokens[0].kind, TokenKind.KW_INT)
        self.assertEqual(tokens[1].kind, TokenKind.IDENT)
        self.assertEqual(tokens[1].lexeme, "x")
        self.assertEqual(tokens[2].kind, TokenKind.ASSIGN)
        self.assertEqual(tokens[3].kind, TokenKind.INT_LIT)
        self.assertEqual(tokens[3].value, Fraction(10))
        self.assertEqual(tokens[4].kind, TokenKind.SEMI)

    def test_floats(self):
        source = "float y = 3.14;"
        tokens = tokenize(source)
        self.assertEqual(tokens[3].kind, TokenKind.FLOAT_LIT)
        self.assertEqual(tokens[3].value, Fraction("3.14"))

    def test_comments(self):
        source = "// this is a comment\nint x = 1; /* block */"
        tokens = tokenize(source)
        self.assertEqual(tokens[0].kind, TokenKind.KW_INT)
        self.assertEqual(tokens[3].kind, TokenKind.INT_LIT)

    def test_errors(self):
        with self.assertRaises(LexError):
            tokenize("int x = 1. ;")
        with self.assertRaises(LexError):
            tokenize("/* unterminated ")

if __name__ == '__main__':
    unittest.main()
