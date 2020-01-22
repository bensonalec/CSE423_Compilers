import unittest, sys, run
sys.path.append('../src')
sys.path.append('../src/rplyTest')
from lexer import *
from rply import errors


class TokenizeTests(unittest.TestCase):
    def test_SimpleReturn(self):
        text_input = "int main() { return 1; }"
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_output")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

    def test_ComplexReturn(self):
        fi = open("./complex.c")
        text_input = fi.read()
        fi.close()
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        fi = open("./expected_complex_output")
        expected = fi.read()
        fi.close()

        self.assertEqual(tokensToString(tokens), expected)

class MyFirstTests(unittest.TestCase):
  def test_hello(self):
    self.assertEqual(run.hello_world(), 'hello world')

	
if __name__ == '__main__':
	unittest.main()
