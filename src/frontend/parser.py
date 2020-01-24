from rply import ParserGenerator
from ast import *

#setup parser class
class Parser():
	def __init__(self):
		#tell the parser what tokens to expect
		self.pg = ParserGenerator(
			['INTEGER','SELF_DEFINED','OPENPAREN','CLOSEPAREN','SEMICOLON','ARITHMETIC','LEFT_BRACE','RIGHT_BRACE','TYPE','BEHAVIOR','ASSIGNMENT']
		)
		#initialzie head and current node
		self.Head = None
		self.CurrentNode = None

	def parse(self):
		#parse for the print statement, this will be our trees head since it's our top level
		@self.pg.production('program : function_definition')
		def program(p):
			
			newNode = AbstractSyntaxTree("program",p)
			self.Head = newNode
			return newNode
		
		@self.pg.production('function_definition : function_definition function_definition')
		def function_def_list(p):
			newNode = AbstractSyntaxTree("function_def_list",p)
			return newNode

		@self.pg.production('function_definition : TYPE SELF_DEFINED OPENPAREN CLOSEPAREN LEFT_BRACE content RIGHT_BRACE')
		def function_definition(p):
			newNode = AbstractSyntaxTree("function_definition",p)
			return newNode

		@self.pg.production('content : content content')
		def contentExpand(p):
			newNode = AbstractSyntaxTree("content",p)
			return newNode
		
		@self.pg.production('content : arithmeticExpression ARITHMETIC arithmeticExpression SEMICOLON')
		@self.pg.production('arithmeticExpression : arithmeticExpression ARITHMETIC arithmeticExpression')
		def mathExpression(p):
			newNode = AbstractSyntaxTree("arithmetic_expression",p)
			return newNode

		@self.pg.production('arithmeticExpression : INTEGER')
		def integerAsExpression(p):
			newNode = AbstractSyntaxTree("integer",p)
			return newNode

		@self.pg.production('content : BEHAVIOR INTEGER SEMICOLON')
		def return_statement(p):
			newNode = AbstractSyntaxTree("return",p)
			return newNode

		@self.pg.production('content : TYPE SELF_DEFINED ASSIGNMENT arithmeticExpression SEMICOLON')
		@self.pg.production('content : SELF_DEFINED ASSIGNMENT arithmeticExpression SEMICOLON')
		def integerAssignment(p):
			newNode = AbstractSyntaxTree("integer_assignment",p)
			return newNode

		@self.pg.production('content : SELF_DEFINED OPENPAREN arithmeticExpression CLOSEPAREN SEMICOLON')
		def function(p):
			newNode = AbstractSyntaxTree("function",p)
			return newNode
	
		#setup the function for variables inside of function calls
		@self.pg.production('expression : SELF_DEFINED')
		def variable(p):
			newNode = AbstractSyntaxTree("variable",p)
			return newNode

		#build BNF for expressions, since each side is an expression it can either take in another equation or a number
		@self.pg.production('expression : arithmeticExpression ARITHMETIC arithmeticExpression')
		def expression(p):
			#print(p[0])
			left = p[0]
			right = p[2]
			operator = p[1]

			newNode = AbstractSyntaxTree("EXPRESSION",p)
			return newNode

		#default error handling function
		@self.pg.error
		def error_handle(token):
			return ValueError(token)
	
	#boilerplate function
	def get_parser(self):
		return self.pg.build()

	#retrieve the trees head
	def getTree(self):
		return self.Head