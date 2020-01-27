
from rply import ParserGenerator
from ast import *

#setup parser class
class Parser():

	
	def __init__(self):
		self.pg = ParserGenerator(
			['TYPE','SELF_DEFINED','OPEN_PAREN','CLOSE_PAREN','OPEN_BRACE','CLOSE_BRACE','ASSIGNMENT','SEMICOLON','LOOPING','BRANCHING','BEHAVIOR','COMMA','INTEGER','STRING','PRECISION','COMPARISON','LOGICAL','ARITHMETIC']
		)
		#initialzie head and current node
		self.Head = None


	def parse(self):

		
		@self.pg.production('program : definitionList ')
		def program(p):
			newNode = AbstractSyntaxTree("program",p)
			self.Head = newNode
			return newNode

		@self.pg.production('definitionList : definitionList functionDefinition ')
		def definitionList___definitionList_functionDefinition_(p):
			newNode = AbstractSyntaxTree("definitionList",p)
			return newNode

		@self.pg.production('definitionList : functionDefinition ')
		def definitionList___functionDefinition_(p):
			newNode = AbstractSyntaxTree("definitionList",p)
			return newNode

		@self.pg.production('functionDefinition : TYPE SELF_DEFINED OPEN_PAREN args CLOSE_PAREN block ')
		def functionDefinition___TYPE_SELF_DEFINED_OPEN_PAREN_args_CLOSE_PAREN_block_(p):
			newNode = AbstractSyntaxTree("function definition",p)
			return newNode

		@self.pg.production('block : OPEN_BRACE block content CLOSE_BRACE ')
		def block___OPEN_BRACE_block_content_CLOSE_BRACE_(p):
			newNode = AbstractSyntaxTree("block",p)
			return newNode

		@self.pg.production('block : OPEN_BRACE content CLOSE_BRACE ')
		def block___OPEN_BRACE_content_CLOSE_BRACE_(p):
			newNode = AbstractSyntaxTree("block",p)
			return newNode

		@self.pg.production('content : content single_line ')
		def content___content_single_line_(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('content : ')
		def content___(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('single_line : TYPE SELF_DEFINED ASSIGNMENT literal SEMICOLON ')
		def single_line___TYPE_SELF_DEFINED_ASSIGNMENT_literal_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("variable assignment",p)
			return newNode

		@self.pg.production('single_line : function_call SEMICOLON ')
		def single_line___function_call_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("function call",p)
			return newNode

		@self.pg.production('single_line : LOOPING OPEN_PAREN boolean CLOSE_PAREN block ')
		def single_line___LOOPING_OPEN_PAREN_boolean_CLOSE_PAREN_block_(p):
			newNode = AbstractSyntaxTree("loop",p)
			return newNode

		@self.pg.production('single_line : LOOPING block LOOPING OPEN_PAREN boolean CLOSE_PAREN SEMICOLON ')
		def single_line___LOOPING_block_LOOPING_OPEN_PAREN_boolean_CLOSE_PAREN_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("do while",p)
			return newNode

		@self.pg.production('single_line : BRANCHING OPEN_PAREN boolean CLOSE_PAREN block ')
		def single_line___BRANCHING_OPEN_PAREN_boolean_CLOSE_PAREN_block_(p):
			newNode = AbstractSyntaxTree("if and else",p)
			return newNode

		@self.pg.production('single_line : BRANCHING OPEN_PAREN non_contiguous CLOSE_PAREN block ')
		def single_line___BRANCHING_OPEN_PAREN_non_contiguous_CLOSE_PAREN_block_(p):
			newNode = AbstractSyntaxTree("switch",p)
			return newNode

		@self.pg.production('single_line : arithmetic SEMICOLON ')
		def single_line___arithmetic_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("arithmetic",p)
			return newNode

		@self.pg.production('single_line : BEHAVIOR literal SEMICOLON ')
		def single_line___BEHAVIOR_literal_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("return statement",p)
			return newNode

		@self.pg.production('single_line : BEHAVIOR non_contiguous SEMICOLON ')
		def single_line___BEHAVIOR_non_contiguous_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("statement",p)
			return newNode

		@self.pg.production('single_line : BEHAVIOR SEMICOLON ')
		def single_line___BEHAVIOR_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("return statement",p)
			return newNode

		@self.pg.production('single_line : SELF_DEFINED ASSIGNMENT literal SEMICOLON ')
		def single_line___SELF_DEFINED_ASSIGNMENT_literal_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("assignment",p)
			return newNode

		@self.pg.production('single_line : SELF_DEFINED ASSIGNMENT boolean SEMICOLON ')
		def single_line___SELF_DEFINED_ASSIGNMENT_boolean_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("assignment",p)
			return newNode

		@self.pg.production('single_line : SELF_DEFINED ASSIGNMENT arithmetic SEMICOLON ')
		def single_line___SELF_DEFINED_ASSIGNMENT_arithmetic_SEMICOLON_(p):
			newNode = AbstractSyntaxTree("assignment",p)
			return newNode

		@self.pg.production('function_call : SELF_DEFINED OPEN_PAREN param CLOSE_PAREN ')
		def function_call___SELF_DEFINED_OPEN_PAREN_param_CLOSE_PAREN_(p):
			newNode = AbstractSyntaxTree("function call",p)
			return newNode

		@self.pg.production('param : literal ')
		def param___literal_(p):
			newNode = AbstractSyntaxTree("parameter",p)
			return newNode

		@self.pg.production('param : SELF_DEFINED ')
		def param___SELF_DEFINED_(p):
			newNode = AbstractSyntaxTree("paramater",p)
			return newNode

		@self.pg.production('param : param COMMA literal ')
		def param___param_COMMA_literal_(p):
			newNode = AbstractSyntaxTree("parameter",p)
			return newNode

		@self.pg.production('param : param COMMA SELF_DEFINED ')
		def param___param_COMMA_SELF_DEFINED_(p):
			newNode = AbstractSyntaxTree("parameter",p)
			return newNode

		@self.pg.production('param : ')
		def param___(p):
			newNode = AbstractSyntaxTree("parameter",p)
			return newNode

		@self.pg.production('literal : INTEGER ')
		def literal___INTEGER_(p):
			newNode = AbstractSyntaxTree("literal",p)
			return newNode

		@self.pg.production('literal : STRING ')
		def literal___STRING_(p):
			newNode = AbstractSyntaxTree("literal",p)
			return newNode

		@self.pg.production('literal : PRECISION ')
		def literal___PRECISION_(p):
			newNode = AbstractSyntaxTree("literal",p)
			return newNode

		@self.pg.production('args : ')
		def args___(p):
			newNode = AbstractSyntaxTree("argument",p)
			return newNode

		@self.pg.production('args : TYPE SELF_DEFINED ')
		def args___TYPE_SELF_DEFINED_(p):
			newNode = AbstractSyntaxTree("argument",p)
			return newNode

		@self.pg.production('args : args COMMA TYPE SELF_DEFINED ')
		def args___args_COMMA_TYPE_SELF_DEFINED_(p):
			newNode = AbstractSyntaxTree("argument",p)
			return newNode

		@self.pg.production('boolean : boolean COMPARISON boolean ')
		def boolean___boolean_COMPARISON_boolean_(p):
			newNode = AbstractSyntaxTree("boolean",p)
			return newNode

		@self.pg.production('boolean : boolean LOGICAL boolean ')
		def boolean___boolean_LOGICAL_boolean_(p):
			newNode = AbstractSyntaxTree("boolean",p)
			return newNode

		@self.pg.production('boolean : arithmetic ')
		def boolean___arithmetic_(p):
			newNode = AbstractSyntaxTree("boolean",p)
			return newNode

		@self.pg.production('boolean : function_call ')
		def boolean___function_call_(p):
			newNode = AbstractSyntaxTree("boolean",p)
			return newNode

		@self.pg.production('boolean : SELF_DEFINED ')
		def boolean___SELF_DEFINED_(p):
			newNode = AbstractSyntaxTree("boolean",p)
			return newNode

		@self.pg.production('boolean : boolean ')
		def boolean___boolean_(p):
			newNode = AbstractSyntaxTree("boolean",p)
			return newNode

		@self.pg.production('boolean : numeral ')
		def boolean___numeral_(p):
			newNode = AbstractSyntaxTree("boolean",p)
			return newNode

		@self.pg.production('arithmetic : arithmetic ARITHMETIC arithmetic ')
		def arithmetic___arithmetic_ARITHMETIC_arithmetic_(p):
			newNode = AbstractSyntaxTree("arithmetic",p)
			return newNode

		@self.pg.production('arithmetic : numeral ')
		def arithmetic___numeral_(p):
			newNode = AbstractSyntaxTree("arithmetic",p)
			return newNode

		@self.pg.production('arithmetic : arithmetic ')
		def arithmetic___arithmetic_(p):
			newNode = AbstractSyntaxTree("arithmetic",p)
			return newNode

		@self.pg.production('numeral : INTEGER ')
		def numeral___INTEGER_(p):
			newNode = AbstractSyntaxTree("numeral",p)
			return newNode

		@self.pg.production('numeral : PRECISION ')
		def numeral___PRECISION_(p):
			newNode = AbstractSyntaxTree("numeral",p)
			return newNode

		@self.pg.production('non_contiguous : PRECISION ')
		def non_contiguous___PRECISION_(p):
			newNode = AbstractSyntaxTree("non contiguous",p)
			return newNode

		@self.pg.production('non_contiguous : INTEGER ')
		def non_contiguous___INTEGER_(p):
			newNode = AbstractSyntaxTree("non contiguous",p)
			return newNode

		@self.pg.production('non_contiguous : STRING ')
		def non_contiguous___STRING_(p):
			newNode = AbstractSyntaxTree("non contiguous",p)
			return newNode

		@self.pg.production('non_contiguous : SELF_DEFINED ')
		def non_contiguous___SELF_DEFINED_(p):
			newNode = AbstractSyntaxTree("non contiguous",p)
			return newNode

	
		@self.pg.error
		def error_handle(token):
			return ValueError(token)

	#boilerplate function
	def get_parser(self):
		return self.pg.build()

	#retrieve the trees head
	def getTree(self):
		return self.Head


