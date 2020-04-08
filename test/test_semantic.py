import sys
import os
sys.path.insert(0,'../src/frontend')

import unittest
from lexer import Lexer, tokensToString
from parser import Parser
from frontend import *
from preprocessor import run
from AST_builder import buildAST, ASTNode
from symbol_table import symbol_table
from semantics import semantic

path_to_C_files = "./programs/"
path_to_output_files = "./expected_output/semantic/"

class SemanticAnalysisTest(unittest.TestCase):

    # Add program into list if for some reason, we shouldn't test it.
    skip_programs = ["Initialization_Strings.c","Functions_Strings.c"]

    maxDiff = None

    def test_semantic(self):
        print()

        for c_filename in sorted(os.listdir(path_to_C_files)):

            if c_filename.endswith('.c') and c_filename not in self.skip_programs:
                fi = open(path_to_C_files + c_filename)
                text_input = fi.read()
                fi.close()

                # Naming scheme for expected output is same as C-file, but no extension
                expected_filename = os.path.splitext(c_filename)[0]
                fi = open(path_to_output_files + expected_filename)
                expected = fi.read()
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

                sym = symbol_table(astree)

                sym.analyze()
                semAnal = semantic(astree,sym.symbols)
                semAnal.semanticAnalysis()

                with self.subTest():
                    self.assertEqual(semAnal.lineSemanticErrors(), expected)
                    status = "ok"

                print(f"{'Semantic Analysis for '+c_filename:65}", end="")
                if status == "ok":
                    print(Colors.green, f"{status}", Colors.reset)
                else:
                    print(Colors.red, f"{status}", Colors.reset)

            elif c_filename.endswith('.c'):
                print(f"{'Semantic Analysis for '+c_filename:65}", end="")
                print(Colors.blue, "skipped", Colors.reset)

class Colors:
        red='\033[31m'
        green='\033[32m'
        blue='\033[34m'
        reset='\033[00m'

if __name__ == '__main__':
    unittest.main()

