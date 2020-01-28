import argparse
from lexer import *
from parser import Parser
from ast import AbstractSyntaxTree
from rply.errors import LexingError
from pptree import *

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

def prettyPrint(head,level,parentNode):
	if(level == 0):
		headNode = Node(head.token)
		parentNode = headNode
	
	token = head.token
	content = head.content
	for ne in content:
		if(type(ne) == type(AbstractSyntaxTree("sample","sample"))):
			nodeName = Node(ne.token,parentNode)
		else:
			
			nodeName = Node(ne,parentNode)
		if(type(ne) == type(AbstractSyntaxTree("sample","sample"))):
			prettyPrint(ne,level+1,nodeName)
	if(level == 0):
		print_tree(headNode)
	

#main function to control the frontend with different command line options.
def main(args):
	#args contain the output from cmd_options.parse_args() and hold the command line options.

	#open file for testing and make sure file is of the correct type
	if args.input_file and args.input_file.endswith(".c"):
		fi = open(args.input_file, "r")
	else:
		if not args.input_file.endswith(".c"):
			print("Error file must end with .c")
		cmd_options.print_help()
		exit()

	#Read in file
	text_input = fi.read()
	fi.close()

	#setup lexer, produce tokens
	lexer = Lexer().get_lexer()
	tokens = lexer.lex(text_input)

	#check for invalid tokens
	try:
		validateTokens(tokens)
	except LexingError as err:
		print("Received error(s) from token validation, exiting...")
		exit()		
	
	#if -l or --lex is true print the tokens from the lexer 
	if args.lex or args.all:
		temp_print = lexer.lex(text_input) #need to run lexer so that tokens are deleted for parser
		for i in temp_print:
			print(i)
		#print(tokensToString(tokens))

	#set up parser, pares the given tokens and retrieve the head of the ast
	pg = Parser()
	pg.parse()
	parser = pg.get_parser()
	try:
		parser.parse(tokens)
	except AssertionError:
		pass
	
	head = pg.getTree()

	if(args.tree):
		print(getTree(head,0))
	#print the tree starting at the head
	else:
		if(args.pretty):
			prettyPrint(head,0,None)
		else:
			printTree(head,0)

if __name__ == "__main__":
	#command line arguements

	#decription of the comiler
	cmd_options = argparse.ArgumentParser(description='Frontend of the compiler. Can produce tokens and syntax tree')
	
	#input file option
	cmd_options.add_argument('input_file', metavar='<filename.c>', type=str, help='Input c file.')
	
	#Arguement to print tokens from lexer
	cmd_options.add_argument('-l','--lex', help='Prints out tokens from lexer', action='store_true')
	
	#Print all output from lexer, parser, etc....
	cmd_options.add_argument('-a','--all', help='Prints out all intermediate ouputs.', action="store_true")

	#Prints string representation of parse tree....
	cmd_options.add_argument('-t','--tree', help='Prints string representation of parse tree.', action="store_true")

	cmd_options.add_argument('-p','--pretty',help='Prints a pretty verision of the tree, and does not print the tokens', action="store_true")

	#generate arguements
	args = cmd_options.parse_args()

	main(args)

