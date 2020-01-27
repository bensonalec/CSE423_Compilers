import sys

sys.path.insert(0,"../src/frontend")

import unittest
from lexer import Lexer
from parser import Parser
import frontend
path_to_C_files = "./C_testing_code/programs/"
path_to_output_files = "./expected_output/parsing/"

class SimpleParserTests(unittest.TestCase):

    maxDiff = None

    def test_Minimum(self):
        fi = open(path_to_C_files + "return_one.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "bare_minimum_expected")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_WhileLoop(self):
        fi = open(path_to_C_files + "while_loop.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "while_loop")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)


if __name__ == '__main__':
	unittest.main()
