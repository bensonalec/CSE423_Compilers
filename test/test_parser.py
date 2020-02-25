import sys
import os
sys.path.insert(0, '../src/frontend')

import unittest
from lexer import Lexer, tokensToString
from parser import Parser, ParseTree
from preprocessor import run
import frontend

path_to_C_files = "./programs/"
path_to_output_files = "./expected_output/parser/"

class ParserTests(unittest.TestCase):

    # Add program into list if for some reason, we shouldn't test it.
    skip_programs = []

    maxDiff = None

    def test_parser(self):
        print(' ')

        for c_filename in os.listdir(path_to_C_files):
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

                # Naming scheme for expected output is same as C-file, but no extension
                expected_filename = os.path.splitext(c_filename)[0]
                fi = open(path_to_output_files + expected_filename)
                expected = fi.read()
                fi.close()

                with self.subTest():
                    self.assertEqual(head.getListView(0), expected)
                    status = "ok"
                
                print(f"{'Parser test for '+c_filename:65} {status}")

            elif c_filename.endswith('.c'):
                print(f"{'Parser test for '+c_filename:65} skipped")


if __name__ == '__main__':
    unittest.main()
