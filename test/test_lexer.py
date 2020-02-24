import sys
import os
sys.path.insert(0, '../src/frontend')

import unittest
from lexer import Lexer, tokensToString

path_to_C_files = "./programs/"
path_to_output_files = "./expected_output/lexer/"

class LexerTests(unittest.TestCase):

    # Add program into list if for some reason, we shouldn't test it.
    skip_programs = []

    maxDiff = None

    def test_lexer(self):
        print()

        for c_filename in os.listdir(path_to_C_files):
            
            if c_filename.endswith('.c') and c_filename not in self.skip_programs:

                print (f"Testing: {c_filename}")

                fi = open(path_to_C_files + c_filename)
                text_input = fi.read()
                fi.close()

                lexer = Lexer().get_lexer()
                tokens = lexer.lex(text_input)

                # Naming scheme for expected output is same as C-file, but no extension
                expected_filename = os.path.splitext(c_filename)[0]
                fi = open(path_to_output_files + expected_filename)
                expected = fi.read()
                fi.close()

                self.assertEqual(tokensToString(tokens), expected)
                print(f"Lexer test passed with: {c_filename}")

 
if __name__ == '__main__':
	unittest.main()
