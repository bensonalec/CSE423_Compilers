"""
This module handle ir input from a file
"""
from rply import LexerGenerator
from rply.errors import LexingError
import copy
import re



class import_ir():

        

        
        def __init__(self, filename):
        fd = open(filename):

        self.data = fd.read()


        def tokenize():
            pass


        def parse():
            pass

class IR_Lexer():
    """
    The lexer class definition
    """
    def __init__(self):
        """
        Constructs the Lexer object.
        """
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        """
        Adds tokens to the rply lexer object
        """
		self.lexer.add("INT",r"([1-9]\d*|\d)")
		self.lexer.add("FLOAT",r"(\d|[1-9]\d+)\.\d*")
		self.lexer.add("CHAR",r"\'\\?[\w\;\\ \%\"\']\'")
		self.lexer.add("STRING",r"(\"[^\n]*?(?<!\\)\")|(\'[^\n]*?(?<!\\)\')")
		self.lexer.add("PLUS",r"\+")
		self.lexer.add("MINUS",r"-")
		self.lexer.add("DIVIDE",r"/")
		self.lexer.add("TIMES",r"\*")
		self.lexer.add("MODULUS",r"%")
		self.lexer.add("LEFT_SHIFT",r"<<")
		self.lexer.add("RIGHT_SHIFT",r">>")
		self.lexer.add("NOT",r"!")
		self.lexer.add("XOR",r"\^")
		self.lexer.add("NEGATE",r"~")
		self.lexer.add("SEMICOLON",r";")
		self.lexer.add("RETURN",r"\breturn\b")
		self.lexer.add("GOTO",r"\goto\b")
		self.lexer.add("IF",r"\bif\b")
		self.lexer.add("ELSE",r"\belse\b")
		self.lexer.add("GEQ",r">=")
		self.lexer.add("LEQ",r"<=")
		self.lexer.add("GREATER_THAN",r">")
		self.lexer.add("LESS_THAN",r"<")
		self.lexer.add("NOT_EQUAL_TO",r"!=")
		self.lexer.add("EQUAL_TO",r"={2}")
		self.lexer.add("EQUALS",r"=")
		self.lexer.add("NULL",r"\bNULL\b")
		self.lexer.add("KEYWORD","\b(const|signed|static|unsigned|extern)\b")
		self.lexer.add("COMMA",r",")
		self.lexer.add("COLON",r":")
		self.lexer.add("AND",r"&{2}")
		self.lexer.add("OR",r"\|{2}")
		self.lexer.add("BW_AND",r"&")
		self.lexer.add("BW_OR",r"\|")
        self.lexer.add("PERIOD",r"\.")
		self.lexer.add("VAR_NAME",r"[a-zA-Z_]\w*")
		self.lexer.add("TYPE",r"\b(auto|long double|double|float|long long( int)?|long|int|short|char|void)\b")
		self.lexer.add("OPEN_PAREN",r"\(")
		self.lexer.add("CLOSE_PAREN",r"\)")
		self.lexer.add("OPEN_BRACK",r"\{")
		self.lexer.add("CLOSE_BRACK",r"\}")
		

    def get_lexer(self):
        """
        Retrieves the lexer, with the tokens added to the inner lexer object.

        Returns:
            The lexer, now built with the tokens added
        """
        self._add_tokens()
        return self.lexer.build()

def print_error(token):
    """
    Prints lexer error message. Currently we only experience invalid token
    errors. The input `token` is a `Token` object, imported from `rply`.

    Args:
        token: The token object that is returned from the lexer.
    """
    print(f"LexingError: Invalid Token \'{token.value}\' at, {token.source_pos}\n")

