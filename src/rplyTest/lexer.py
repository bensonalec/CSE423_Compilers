from rply import LexerGenerator

class Lexer():
	def __init__(self):
		self.lexer = LexerGenerator()

	def _add_tokens(self):
		self.lexer.add("COMMENT",r"(\/\/.*|\/\*.*\*\/|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)")
		self.lexer.add("STRING",r"(\"[\w+\;\\ \%\"\']*\")")
		self.lexer.add("PREPROCESSOR",r"(#include|#define|#undef|#if|#ifdef|#ifndef|#error|__FILE__|__LINE__|__DATE__|__TIME__|__TIMESTRAMP|pragma|# macro operator|## macro operator)")
		self.lexer.add("KEYWORDS",r"(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)")
		self.lexer.add("BINARY_OPS", r"(\&|\||\^|\~|\<\<|\>\>)")
		self.lexer.add("ADVANCED_ARITHMETIC",r"(\+\+|\-\-|\-\=|\+\=|\*\=|\/\=)")
		self.lexer.add("BOOLEAN",r"(true|false)")
		self.lexer.add("FLOATORDOUBLE",r"(\d+\.\d+)")
		self.lexer.add("CHARACTER", r"('[\w]')")
		self.lexer.add("FUNCTION",r"([a-zA-Z_]\w+\(|[a-zA-Z_]\()")
		self.lexer.add("ARITHMETIC_OPERATOR", r"(\+|\-|\/|\*|\%)")
		self.lexer.add("INTEGER",r"(\d+)")
		self.lexer.add("COMPARISON_OPERATOR",r"(==|<=|>=|<|>)")
		self.lexer.add("LOGIC_OPERATOR",r"(&&|\|\|)")
		self.lexer.add("VARIABLE", r"([a-zA-Z_]\w+|[a-zA-Z_])")
		self.lexer.add("ASSIGNMENT", r"(=)")
		self.lexer.add("OPENPAREN",r'\(')
		self.lexer.add("CLOSEPAREN",r'\)')
		self.lexer.add("LEFT_BRACKET", r"(\{)")
		self.lexer.add("RIGHT_BRACKET",r"(\})")
		self.lexer.add("SEMICOLON",r";")
		
		self.lexer.ignore(r'\s+')
		self.lexer.ignore(r'\n')
		self.lexer.ignore(r'\t')

	def get_lexer(self):
		self._add_tokens()
		return self.lexer.build()