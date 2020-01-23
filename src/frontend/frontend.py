from lexer import *
from parser import Parser
from ast import AbstractSyntaxTree

#function to print the tree


def getTree(head,level):
	level += 1
	token = head.token
	content = head.content
	li = []
	out = ""
	for node in content:
		if(type(node) != type(AbstractSyntaxTree("sample","sample"))):
			li.append(node)
		else:
			li.append(node.token)
	
	out = (level,li)


	#iterate through the components of the BNF
	for node in content:
		if(type(node) == type(AbstractSyntaxTree("sample","sample"))):
			out += getTree(node,level)
	return out

def printTree(head,level):
	level += 1
	token = head.token
	content = head.content
	li = []
	out = ""
	for node in content:
		if(type(node) != type(AbstractSyntaxTree("sample","sample"))):
			li.append(node)
		else:
			li.append(node.token)
	
	print(level,":",li)


	#iterate through the components of the BNF
	for node in content:
		if(type(node) == type(AbstractSyntaxTree("sample","sample"))):
			printTree(node,level)


#open file for testing
fi = open("./test_files/parsertest.c","r")
text_input = fi.read()
fi.close()

#setup lexer, produce tokens
lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)
#print(tokensToString(tokens))
#set up parser, pares the given tokens and retrieve the head of the ast
pg = Parser()
pg.parse()
parser = pg.get_parser()
parser.parse(tokens)
head = pg.getTree()
#print the tree starting at the head
(printTree(head,0))

