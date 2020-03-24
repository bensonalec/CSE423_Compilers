import sys
import os
sys.path.insert(0,'../src/frontend')
sys.path.insert(0,'../src/optimizer')

import unittest
from lexer import Lexer, tokensToString
from parser import Parser
from frontend import *
from preprocessor import run
from AST_builder import buildAST, ASTNode
from semantics import symbol_table
import IR_Lv1_Builder as ir1


# optimizer = importlib.import_module("optimizer.optimizer", __name__)
# ir1 = importlib.import_module("IR_Lv1_Builder", __name__)

path_to_C_files = "./programs/"
path_to_output_files = "./expected_output/ir/"

class IRTest(unittest.TestCase):

    # Add program into list if for some reason, we shouldn't test it.
    skip_programs = []
    maxDiff = None

    def test_ir(self):
        print()

        for c_filename in os.listdir(path_to_C_files):
            
            if c_filename.endswith('.c') and c_filename not in self.skip_programs:

                status = "FAIL" #Will change if test passes

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
                ir = ir1.LevelOneIR(astree,sym)
                l1ir = ir.construct()
                result = ""
                for x in l1ir:
                    result += x + "\n"
                
                with self.subTest():
                    self.assertEqual(result, expected)
                    status = "ok"

                print(f"{'IR test for '+c_filename:65}", end="")
                if status == "ok":
                    print(Colors.green, f"{status}", Colors.reset)
                else:
                    print(Colors.red, f"{status}", Colors.reset)
                
            elif c_filename.endswith('.c'):
                print(f"{'IR for '+c_filename:65}", end="")
                print(Colors.blue, "skipped", Colors.reset)

class Colors: 
        red='\033[31m'
        green='\033[32m'
        blue='\033[34m'
        reset='\033[00m'

if __name__ == '__main__':
    unittest.main()

