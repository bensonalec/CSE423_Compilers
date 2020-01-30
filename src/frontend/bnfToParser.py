import re

	
funcTemp = 	"""
		@self.pg.production('BNFSPOT')
		def FUNCNAMESPOT(p):
			newNode = AbstractSyntaxTree("NAMESPOT",p)
			self.Head = newNode
			return newNode
"""
headTemp = 	"""
		@self.pg.production('BNFSPOT')
		def program(p):
			newNode = AbstractSyntaxTree("NAMESPOT",p)
			self.Head = newNode
			return newNode
"""

initTemp = """
	def __init__(self):
		self.pg = ParserGenerator(
			TOKENSPOT
		)
		#initialzie head and current node
		self.Head = None
"""

fi = open("BNF_definition","r")
cont = fi.read()
fi.close()
reg = r'([A-Z][A-Z|_]*[A-Z])'
reg = re.compile(reg)

tokens = []
for group in reg.findall(cont):
	tokens.append("'" + group + "'")
tokens = list(dict.fromkeys(tokens))
tokenList = "["
jon = ","
join = jon.join(tokens)
tokenList += join + "]"

initFunc = initTemp.replace("TOKENSPOT",tokenList)

fi = open("BNF_definition","r")
cont = fi.readlines()
fi.close()
functionList = ""

for line in cont:
	if(line != "\n"):
		
		spl = line.split("#")
		bnf = spl[0]
		funcname = bnf.replace(" ","_")
		funcname = funcname.replace(":","_")
		
		name = spl[1].strip()
		if(name == "program"):
			newFunc = headTemp
		else:
			newFunc = funcTemp
		newFunc = newFunc.replace("BNFSPOT",bnf)
		newFunc = newFunc.replace("FUNCNAMESPOT",funcname)
		newFunc = newFunc.replace("NAMESPOT",name)
		
		functionList += newFunc

totalOutput = """
from rply import ParserGenerator
from rply.errors import ParserGeneratorWarning
from ast import *
from warnings import simplefilter
from rply.token import Token

#we get werid 'non-descriptive' warnings from ParserGenerator, this ignores those
simplefilter('ignore', ParserGeneratorWarning)


#setup parser class
class Parser():

	INITSPOT

	def parse(self):

		FUNCLISTSPOT
	
		@self.pg.error
		def error_handle(token):
			return ValueError(token)

	#boilerplate function
	def get_parser(self):
		return self.pg.build()

	#retrieve the trees head
	def getTree(self):
		return self.Head

	def print_error(self):
		\"\"\"
		Prints parser error message. This function ultimately iterates through the AST that was 
		returned after the parser found an error. AST's consist of tokens as well as other AST's so 
		we need to iterate to find the first token and then print its source position.
		\"\"\"
		# TODO: add some more in-depth error processing to print
		# out a more detailed description of what went wrong, and possibly some suggestions 
		# at to why there was a parse/syntax error. (i.e. suggest a missing semicolon)

		head = self.getTree()
		token = 0 # token hasn't been found yet, so we set value to 0

		while True:
			# Iterate through list of elements
			for i in head.content:

				# Could be a Token
				if(type(i) == type(Token("sample", "sample"))):

					# Found a Token
					token = i
					break

			# Check again (to break out of while loop and not iterate again)		
			if (type(token) == type(Token("sample", "sample"))):
				break
			else:
				# Set head to last element.
				# If this code executes then I can assume that the 
				# last element is an AST.
				head = head.content[len(head.content)-1]

		print(f"ParsingError: Last token  \\\'{token.value}\\\' parsed successfully at, {token.source_pos}\\n")



"""

totalOutput = totalOutput.replace("INITSPOT",initFunc)
totalOutput = totalOutput.replace("FUNCLISTSPOT",functionList)
print(totalOutput)