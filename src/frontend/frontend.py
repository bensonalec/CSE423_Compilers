import argparse
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

	#command line arguement

	#decription of the comiler
	cmd_options = argparse.ArgumentParser(description='Frontend of the compiler. Can produce tokens and syntax tree')
	
	#input file option
	cmd_options.add_argument('input_file', metavar='<filename.c>', type=str, help='Input c file.')
	
	#Arguement to print tokens from lexer
	cmd_options.add_argument('-l','--lex', help='Prints out tokens from lexer', action='store_true')
	
	#Print all output from lexer, parser, etc....
	cmd_options.add_argument('-a','--all', help='Prints out all intermediate ouputs.', action="store_true")

	args = cmd_options.parse_args()


	#open file for testing and make sure file is of the correct type
	if args.input_file and args.input_file.endswith(".c"):
		fi = open(args.input_file, "r")
	else:
		if not args.input_file.endswith(".c"):
			print("Error file must end with .c")
		cmd_options.print_help()
		exit()

	print(args.lex)

	text_input = fi.read()
	fi.close()

	#setup lexer, produce tokens
	lexer = Lexer().get_lexer()

	tokens = lexer.lex(text_input)
	if args.lex:
		temp_print = lexer.lex(text_input)
		for i in temp_print:
			print(i)
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

