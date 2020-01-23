import sys
sys.path.append('../src/frontend')

import unittest
from lexer import *

path_to_C_files = "./C_testing_code/regex/"
path_to_output_files = "./expected_output/regex/"

class SimpleTokenizerTests(unittest.TestCase):

    maxDiff = None

    def test_Comments(self):
        fi = open(path_to_C_files + "comments.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "comments")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_PreProcessor(self):
        fi = open(path_to_C_files + "preProcessor.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "preProcessor")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_ImportingLibraries(self):
        fi = open(path_to_C_files + "importingLibraries.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "importingLibraries")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_Type_Assignment_Hex_Oct_Int(self):
        fi = open(path_to_C_files + "typeAssignHexOctInt.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "typeAssignHexOctInt")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_Strings(self):
        fi = open(path_to_C_files + "strings.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "strings")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_Keywords(self):
        fi = open(path_to_C_files + "keywords.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "keywords")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Bin(self):
        fi = open(path_to_C_files + "bin.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "bin")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Precision(self):
        fi = open(path_to_C_files + "precision.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "precision")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Comparison(self):
        fi = open(path_to_C_files + "comparison.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "comparison")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)
    
    def test_Arithmetic(self):
        fi = open(path_to_C_files + "arithmetic.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "arithmetic")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

if __name__ == '__main__':
	unittest.main()
