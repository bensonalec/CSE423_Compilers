import sys
sys.path.append('../src/frontend')

import unittest
from lexer import *


class SimpleTokenizerTests(unittest.TestCase):

    maxDiff = None

    def test_Comments(self):
        fi = open("./C_testing_code/regex/comments.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/comments")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_PreProcessor(self):
        fi = open("./C_testing_code/regex/preProcessor.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/preProcessor")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_ImportingLibraries(self):
        fi = open("./C_testing_code/regex/importingLibraries.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/importingLibraries")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_Type_Assignment_Hex_Oct_Int(self):
        fi = open("./C_testing_code/regex/typeAssignHexOctInt.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/typeAssignHexOctInt")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_Strings(self):
        fi = open("./C_testing_code/regex/strings.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/strings")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_Keywords(self):
        fi = open("./C_testing_code/regex/keywords.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/keywords")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Bin(self):
        fi = open("./C_testing_code/regex/bin.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/bin")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Precision(self):
        fi = open("./C_testing_code/regex/precision.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/precision")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Comparison(self):
        fi = open("./C_testing_code/regex/comparison.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/comparison")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Arithmetic(self):
        fi = open("./C_testing_code/regex/arithmetic.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output/regex/arithmetic")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

if __name__ == '__main__':
	unittest.main()
