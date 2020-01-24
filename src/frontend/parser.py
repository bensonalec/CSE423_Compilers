
from rply import ParserGenerator
from ast import *

#setup parser class
class Parser():

	
	def __init__(self):
		self.pg = ParserGenerator(
			['TYPE','SELF_DEFINED','OPENPAREN','CLOSEPAREN','LEFT_BRACE','RIGHT_BRACE','ARITHMETIC','SEMICOLON','INTEGER','BEHAVIOR','ASSIGNMENT']
		)
		#initialzie head and current node
		self.Head = None


	def parse(self):

		
		@self.pg.production('program : function_definition')
		def program(p):
			newNode = AbstractSyntaxTree("program",p)
			self.Head = newNode
			return newNode

		@self.pg.production('function_definition : function_definition function_definition')
		def function_definition___function_definition_function_definition(p):
			newNode = AbstractSyntaxTree("function definition",p)
			return newNode

		@self.pg.production('function_definition : TYPE SELF_DEFINED OPENPAREN CLOSEPAREN LEFT_BRACE content RIGHT_BRACE')
		def function_definition___TYPE_SELF_DEFINED_OPENPAREN_CLOSEPAREN_LEFT_BRACE_content_RIGHT_BRACE(p):
			newNode = AbstractSyntaxTree("function definition",p)
			return newNode

		@self.pg.production('content : content content')
		def content___content_content(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('content : arithmeticExpression ARITHMETIC arithmeticExpression SEMICOLON')
		def content___arithmeticExpression_ARITHMETIC_arithmeticExpression_SEMICOLON(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('arithmeticExpression : arithmeticExpression ARITHMETIC arithmeticExpression')
		def arithmeticExpression___arithmeticExpression_ARITHMETIC_arithmeticExpression(p):
			newNode = AbstractSyntaxTree("arithmeticExpression",p)
			return newNode

		@self.pg.production('arithmeticExpression : INTEGER')
		def arithmeticExpression___INTEGER(p):
			newNode = AbstractSyntaxTree("arithmeticExpression",p)
			return newNode

		@self.pg.production('content : BEHAVIOR INTEGER SEMICOLON')
		def content___BEHAVIOR_INTEGER_SEMICOLON(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('content : TYPE SELF_DEFINED ASSIGNMENT arithmeticExpression SEMICOLON')
		def content___TYPE_SELF_DEFINED_ASSIGNMENT_arithmeticExpression_SEMICOLON(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('content : SELF_DEFINED ASSIGNMENT arithmeticExpression SEMICOLON')
		def content___SELF_DEFINED_ASSIGNMENT_arithmeticExpression_SEMICOLON(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('content : SELF_DEFINED OPENPAREN arithmeticExpression CLOSEPAREN SEMICOLON')
		def content___SELF_DEFINED_OPENPAREN_arithmeticExpression_CLOSEPAREN_SEMICOLON(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode

		@self.pg.production('expression : SELF_DEFINED')
		def expression___SELF_DEFINED(p):
			newNode = AbstractSyntaxTree("expression",p)
			return newNode

		@self.pg.production('expression : arithmeticExpression ARITHMETIC arithmeticExpression')
		def expression___arithmeticExpression_ARITHMETIC_arithmeticExpression(p):
			newNode = AbstractSyntaxTree("expression",p)
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


