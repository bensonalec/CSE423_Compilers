# For verbose output use the following command:
# python -m unittest -v master_test.py

from rply import LexerGenerator

class Lexer():
	def __init__(self):
		self.lexer = LexerGenerator()

	def _add_tokens(self):
		self.lexer.add("COMMENT",      r"(\/\/.*|\/\*.*\*\/|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)") # Catches both multi-line and single line comments
		self.lexer.add("LIBRARY",      r"<\w+\.h>|\"\w+\.h\"")
		self.lexer.add("STRING",       r"(([\"\'])[\w+\;\\ \%\"\']*\2)") # Classifies single characters and multiple characters as a string
		self.lexer.add("HEX",          r"0x[\dA-Fa-f]+")
		self.lexer.add("OCT",          r"0[0-7]{1,3}")
		self.lexer.add("BIN",          r"0b[01]+")
		self.lexer.add("PRECISION",    r"\-{0,1}(\d\.\d+|[1-9]\d*\.\d+)")
		self.lexer.add("INTEGER",      r"\-{0,1}([1-9]\d*|\d)")
		self.lexer.add("COMPARISON",   r"[=<>!]=|[<>]")
		self.lexer.add("ASSIGNMENT",   r"[+*/-]{0,1}=")
		self.lexer.add("LOGICAL",      r"&{2}|\|{2}")
		self.lexer.add("ACCESS",       r"->|\.|\[|\]")
		self.lexer.add("BITWISE",      r"<{2}|>{2}|[|&^~]")
		self.lexer.add("ARITHMETIC",   r"\+{2}|\-{2}|[%*/+-]")
		self.lexer.add("MODIFIER",     r"\b(const|register|signed|static|unsigned|volatile|typedef|extern|sizeof)\b")
		self.lexer.add("BEHAVIOR",     r"\b(break|continue|goto|return)\b")
		self.lexer.add("LOOPING",      r"\b(do|for|while)\b")
		self.lexer.add("BRANCHING",    r"\b(if|else|switch|case|default)\b")
		self.lexer.add("TYPE",         r"\b(NULL|void|char|short|int|long|float|double|struct|union|enum|auto)\b")
#TODO: Lexer doesnt pick up #error macro correctly, fix regex for this token
#		self.lexer.add("MACRO",		   r"\#\s*error \w+$")
		self.lexer.add("PREPROCESSOR", r"\#\s*(include|pragma|define|error|warning|undef|ifdef|ifndef|if|else|elif|endif|line)")
		self.lexer.add("SELF_DEFINED", r"[a-zA-Z_]\w*")
		self.lexer.add("OPENPAREN",    r"\(")
		self.lexer.add("CLOSEPAREN",   r"\)")
		self.lexer.add("LEFT_BRACE",   r"\{")
		self.lexer.add("RIGHT_BRACE",  r"\}")
		self.lexer.add("SEMICOLON",    r";")
		self.lexer.add("COLON",        r":")
		self.lexer.add("COMMA",        r",")
		self.lexer.add("OTHERS",       r".+?") # Just to catch stuff we havent thought about yet
		
		self.lexer.ignore(r'\s+')

	def get_lexer(self):
		self._add_tokens()
		return self.lexer.build()

def tokensToString(tokens):
	out = ""
	for tok in tokens:
		out+= str(tok) + "\n"
	return out