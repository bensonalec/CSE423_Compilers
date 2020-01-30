import sys
sys.path.insert(0, '../src/frontend')

import unittest
from lexer import *
from rply.errors import LexingError
from parser import Parser 


path_to_C_files = "./C_testing_code/regex/"
path_to_output_files = "./expected_output/regex/"

class ErrorHandlingTests(unittest.TestCase):

    maxDiff = None

    def test_lexer_fail(self):

        # Invalid tokens '@' and '#'
        text_input = """
        int main() {
            @
            return 1;
            #
        }
        """

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)

        with self.assertRaises(LexingError): validateTokens(tokens)

    def test_parser_fail(self):

        # Missing semi-colon
        text_input = """
        int main() {
            return 1
        }
        """

        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        validateTokens(tokens)
        
        pg = Parser()
        pg.parse()
        parser = pg.get_parser()

        with self.assertRaises(AssertionError): parser.parse(tokens)

if __name__ == '__main__':
	unittest.main()
