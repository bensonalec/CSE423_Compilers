"""
This module acts as the interface for running all the seperate portions of the front end. It allows
for command line arguments that can be used to determine which portion is run.
"""
import argparse
from lexer import *
from rply.errors import LexingError
from pptree import *
from parser import AbstractSyntaxTree

import bnfToParser

def getTree(head,level):
    """
    Outputs a string version of the Abstract Syntax Tree that can be used in unit testing. Calls itself recursively
    param: head: the head node of the tree
    param: level: the current level of the tree
    :return: A string of the nodes in the tree
    """
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
    """
    Prints a simple version of the tree for output. Calls itself recursively
    param: head: the head node of the tree
    param: level: the current level of the tree
    :return: Does not return anything
    """
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
    """
    Prints the Abstract Syntax Tree using a tree library (pptree)
    param: head: The head node of the tree
    param: level: the level the tree is on
    param: parentNode: the parent node of the tree
    :return: There is no return 
    """
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
        #this is a function from the pptree
        print_tree(headNode)
    

#main function to control the frontend with different command line options.
def main(args, fi):
    """
    The main function of this, takes in command line input via an object from argparse, and the name of the file.
    param: args: the object that contains the command line arguements
    param: fi: the file object that is open
    """

    if args.bnf:
        bnfToParser.main(args.bnf)
    from parser import Parser
    

    try:

        #Read in file
        text_input = fi.read()
        fi.close()

        #setup lexer, produce tokens, check for invalid tokens
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        validateTokens(tokens)
        
        #set up parser and parse the given tokens
        pg = Parser()
        pg.parse()
        parser = pg.get_parser()
        parser.parse(tokens)

    except LexingError as err:
        print("Received error(s) from token validation. Exiting...")
        exit()

    except AssertionError as err:
        # parser has it's own detailed error printing
        pg.print_error()
        print("Received AssertionError(s) from parser, continuing with what was parsed...\n")

    except BaseException as err:
        print(f"BaseException: {err}. Exiting...")
        exit()
    
    # Retrieve the head of the AST
    head = pg.getTree()


    #if -l or --lex is true print the tokens from the lexer 
    if args.lex or args.all:
        temp_print = lexer.lex(text_input) #need to run lexer so that tokens are deleted for parser
        for i in temp_print:
            print(i)
        #print(tokensToString(tokens))

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

    cmd_options.add_argument('-b', '--bnf', nargs='?', const='./BNF_definition', type=str, help='Rebuilds the parser using the current BNF grammar')

    #generate arguements
    args = cmd_options.parse_args()


    #open file and pass into main.
    if args.input_file and args.input_file.endswith(".c"):
        fi = open(args.input_file, "r")
    else:
        #if not c file.
        if not args.input_file.endswith(".c"):
            print("Error file must end with .c")
        cmd_options.print_help()
        exit()
    main(args, fi)

