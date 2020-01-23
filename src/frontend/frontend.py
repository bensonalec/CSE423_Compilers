from lexer import *
from parser import Parser
from ast import AbstractSyntaxTree

import sys
#function to print the tree


def printTree(head,level):
	level += 1
	token = head.token
	content = head.content
	print("Level: ",level,"Node: ",content, "Type: ",token)
	#iterate through the components of the BNF
	for node in content:
		if(type(node) == type(AbstractSyntaxTree("sample","sample"))):
			printTree(node,level)

#main function to control the frontend with different command line options.
def main():
	#open file for testing
	#fi = open("./test_files/parsertest.c","r")
	fi = open(sys.argv[1], "r")
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
	printTree(head,0)


if __name__ == "__main__":
	main()

