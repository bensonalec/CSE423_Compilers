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
from AST_builder import buildAST, print_AST, ASTNode


path_to_C_files = "./programs/"
path_to_output_files = "./expected_output/ast/"

class AbstractSyntaxTreeTests(unittest.TestCase):

    # Add program into list if for some reason, we shouldn't test it.
    skip_programs = ["Arithmetic_As_Function_Input.c","If_Else.c","Identifiers_Variables_Functions.c", "Pre_Processor.c"]

    maxDiff = None

    def test_ast(self):
        print(' ')

        for c_filename in os.listdir(path_to_C_files):
            
            if c_filename.endswith('.c') and c_filename not in self.skip_programs:
                
                status = "FAIL" #Will change if test passes

                fi = open(path_to_C_files + c_filename)
                text_input = fi.read()
                fi.close()

                text_input = run(text_input)

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
                    # Redirect std-out to test that AST print output is correct
                    with patch('sys.stdout', new = StringIO()) as fake_stdout:
                        print_AST(astree)
                        self.assertEqual(fake_stdout.getvalue(), expected)
                    
                    status = "ok"
                
                print(f"{'AST test for '+c_filename:65} {status}")

if __name__ == '__main__':
	unittest.main()

