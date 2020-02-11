import sys

sys.path.insert(0,"../src/frontend")

import unittest
from lexer import Lexer
from parser import Parser
import frontend
path_to_C_files = "./C_testing_code/programs/"
path_to_output_files = "./expected_output/parsing/"

class MinimalParserTests(unittest.TestCase):

    maxDiff = None

    def test_Identifiers_Variables_Functions(self):
        fi = open(path_to_C_files + "Identifiers_Variables_Functions.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Identifiers_Variables_Functions")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Keywords(self):
        fi = open(path_to_C_files + "Keywords.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Keywords")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Arithmetic(self):
        fi = open(path_to_C_files + "Arithmetic.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Arithmetic")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Assignment(self):
        fi = open(path_to_C_files + "Assignment.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Assignment")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Boolean(self):
        fi = open(path_to_C_files + "Boolean.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Boolean")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Goto(self):
        fi = open(path_to_C_files + "Goto.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Goto")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_If_Else(self):
        fi = open(path_to_C_files + "If_Else.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "If_Else")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Unary(self):
        fi = open(path_to_C_files + "Unary.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Unary")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Return(self):
        fi = open(path_to_C_files + "Return.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Return")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_Break(self):
        fi = open(path_to_C_files + "Break.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "Break")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)

    def test_While(self):
        fi = open(path_to_C_files + "While.c")
        text_input = fi.read()
        fi.close()

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        pg = Parser()
        pg.parse()
        parse = pg.get_parser()
        parse.parse(tokens)
        head = pg.getTree()

        fi = open(path_to_output_files + "While")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(frontend.getTree(head,0)), expected)


if __name__ == '__main__':
	unittest.main()
