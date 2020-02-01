"""
This module contains the Lexer class and it's token name and regexes, as well as some error checking for tokens
"""
from rply import LexerGenerator
from rply.errors import LexingError
import copy

class Lexer():
	"""
	Lexer is the object that contains all of the token name, regexes,and functionality of the Lexer
	"""
	def __init__(self):
		"""
		Creates a new Lexer object and creates an attribute of the class called Lexer from rply
		:return: Does not return anything
		"""
		self.lexer = LexerGenerator()
	
	def _add_tokens(self):
		"""
		Adds all of the necessary token names and regexes to the lexer attribute, as well as telling the lexer 
		what to ignore
		:return: Does not return anything
		"""
		self.lexer.add("COMMENT",      r"(\/\/.*|\/\*.*\*\/|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)") # Catches both multi-line and single line comments
		self.lexer.add("PREPROCESSOR", r"#\s*(warning|else|endif|include|undef|ifdef|ifndef|if|elif|pragma|define|if|elif|error|pragma|line)([\t\f ]+[^\s]+)*")
		self.lexer.add("CHAR",          r"\'[\w\;\\ \%\"\']\'")
		self.lexer.add("STRING",       r"(\"[\w+\;\\ \%\"\']*\")") # Classifies single characters and multiple characters as a string
		self.lexer.add("HEX",          r"0x[\dA-Fa-f]+")
		self.lexer.add("OCT",          r"0[0-7]{1,3}")
		self.lexer.add("BIN",          r"0b[01]+")
		self.lexer.add("PRECISION",    r"\-?(\d\.\d+|[1-9]\d*\.\d+)")
		self.lexer.add("INTEGER",      r"\-?([1-9]\d*|\d)")
		self.lexer.add("COMPARISON",   r"[=<>!]=|[<>]")
		self.lexer.add("ASSIGNMENT",   r"([+*/-]|<{2}|>{2}|[|&^~])?=|\+{2}|\-{2}")
		self.lexer.add("LOGICAL",      r"&{2}|\|{2}")
		self.lexer.add("ACCESS",       r"->|\.|\[|\]")
		self.lexer.add("ARITHMETIC",   r"[%*/+-]|<{2}|>{2}|[|&^~]")
		self.lexer.add("MODIFIER",     r"\b(const|register|signed|static|unsigned|volatile|typedef|extern|sizeof|inline)\b")
		self.lexer.add("BEHAVIOR",     r"\b(break|continue|goto|return)\b")
		self.lexer.add("LOOPING",      r"\b(do|for|while)\b")
		self.lexer.add("BRANCHING",    r"\b(if|else|switch|case|default)\b")
		self.lexer.add("TYPE",         r"\b(NULL|void|char|short|int|long|float|double|struct|union|enum|auto)\b")
		self.lexer.add("SELF_DEFINED", r"[a-zA-Z_]\w*")
		self.lexer.add("OPEN_PAREN",   r"\(")
		self.lexer.add("CLOSE_PAREN",  r"\)")
		self.lexer.add("OPEN_BRACE",   r"\{")
		self.lexer.add("CLOSE_BRACE",  r"\}")
		self.lexer.add("SEMICOLON",    r";")
		self.lexer.add("COLON",        r":")
		self.lexer.add("COMMA",        r",")
		self.lexer.add("INVALID",       r".+?") # Just to catch stuff we havent thought about yet		
		self.lexer.ignore(r'\s+')
		self.lexer.ignore(r'\n')
		self.lexer.ignore(r'\t')
	def get_lexer(self):
		"""
		Calls _add_tokens to the initial lexer attribute, and then returns a built version of that lexer attribute
		:return: The built lexer
		"""
		self._add_tokens()
		return self.lexer.build()
	
def tokensToString(tokens):
	"""
	Returns a string version of all of the tokens. Used for output and error checking
	:param tokens: The lsit of tokens to be printed
	:return: the string representation of the tokens
	"""
	out = ""
	for tok in tokens:
		out+= str(tok) + "\n"
	return out

def validateTokens(tokens):
	"""
	Validates the given token list. If an invalid token to found, 
	then a LexingError exception is raised. Otherwise, returns normally.
	:param tokens: the list of tokens to be validated
	:return: This does not return anything
	"""
	cpy = copy.deepcopy(tokens)
	status = "PASS"

	# Goes through copy list and looks for any "invalid tokens".
	# The lexer will mark any unknown tokens with the name, "INVALID".
	for i in cpy:
		if (i.name == "INVALID"):
			print_error(i)
			status = "FAIL" # status is changed

	if (status == "FAIL"):
		raise LexingError("invalid token", i.source_pos)

def print_error(token):
	"""
	Prints lexer error message. Currently we only experience invalid token
	errors. The input token is a Token object, imported from rply.
	:param token: The token to be printed
	:return: This does not return anything
	"""
	print(f"LexingError: Invalid Token \'{token.value}\' at, {token.source_pos}\n")
	
		