import sys
import os
sys.path.insert(0, '../src/frontend')

import unittest
from unittest.mock import patch
from io import StringIO
from lexer import Lexer, tokensToString
from parser import Parser
from frontend import *
from preprocessor import run
from AST_builder import buildAST, ASTNode


path_to_C_files = "./programs/"
path_to_output_files = "./expected_output/ast/"

class AbstractSyntaxTreeTests(unittest.TestCase):

    # Add program into list if for some reason, we shouldn't test it.
    skip_programs = []

    maxDiff = None

    def test_ast(self):
        print(' ')

        for c_filename in sorted(os.listdir(path_to_C_files)):

            if c_filename.endswith('.c') and c_filename not in self.skip_programs:

                status = "FAIL" #Will change if test passes

                fi = open(path_to_C_files + c_filename)
                text_input = fi.read()
                fi.close()

                text_input = run(text_input, path_to_C_files + c_filename)

                lexer = Lexer().get_lexer()
                tokens = lexer.lex(text_input)

                pg = Parser()
                pg.parse()
                parse = pg.get_parser()
                parse.parse(tokens)
                head = pg.getTree()

                astree = buildAST(head)

                # Naming scheme for expected output is same as C-file, but no extension
                expected_filename = os.path.splitext(c_filename)[0]
                fi = open(path_to_output_files + expected_filename)
                expected = fi.read()
                fi.close()

                with self.subTest():
                    self.assertEqual(str(astree), expected)
                    status = "ok"

                # with self.subTest():
                #     # Redirect std-out to test that AST print output is correct
                #     with patch('sys.stdout', new = StringIO()) as fake_stdout:
                #         astree.print_AST()
                #         self.assertEqual(fake_stdout.getvalue(), expected)

                #     status = "ok"

                print(f"{'AST test for '+c_filename:65}", end="")
                if status == "ok":
                    print(Colors.green, f"{status}", Colors.reset)
                else:
                    print(Colors.red, f"{status}", Colors.reset)

            elif c_filename.endswith('.c'):
                print(f"{'AST test for '+c_filename:65}", end="")
                print(Colors.blue, "skipped", Colors.reset)

class Colors:
        red='\033[31m'
        green='\033[32m'
        blue='\033[34m'
        reset='\033[00m'

if __name__ == '__main__':
	unittest.main()

