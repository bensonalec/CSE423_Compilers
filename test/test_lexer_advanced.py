import sys
sys.path.append('../src/frontend')

import unittest
from lexer import *

path_to_C_files = "./C_testing_code/programs/"
path_to_output_files = "./expected_output/programs/"

class SimpleTokenizerTests(unittest.TestCase):

    maxDiff = None

    def test_SimpleReturnOne(self):
        fi = open(path_to_C_files + "return_one.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "return_one")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_ComplexRandom(self):
        fi = open(path_to_C_files + "complex_random.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open(path_to_output_files + "complex_random")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)


if __name__ == '__main__':
	unittest.main()
