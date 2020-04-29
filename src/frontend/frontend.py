"""
This module acts as the interface for running all the seperate portions of the front end. It allows
for command line arguments that can be used to determine which portion is run.
"""
import os
import argparse
from importlib.machinery import SourceFileLoader
from inspect import getsourcefile
import traceback
import sys

from rply.errors import LexingError
from copy import deepcopy

lex = SourceFileLoader("lexer", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/lexer.py").load_module()
par = SourceFileLoader("parser", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/parser.py").load_module()
btp = SourceFileLoader("bnfToParser", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/bnfToParser.py").load_module()
ast = SourceFileLoader("AST_builder", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/AST_builder.py").load_module()
sym = SourceFileLoader("symbol_table", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/symbol_table.py").load_module()
pre = SourceFileLoader("preprocessor", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/preprocessor.py").load_module()
semantic = SourceFileLoader("semantics", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/semantics.py").load_module()

def getTree(head,level):
    """
    Outputs a string version of the ParseTree that can be used in unit testing. Calls itself recursively

    Args:
        head: The head node of the tree.
        level: The current level of the tree.

    Returns:
        A string of the nodes in the tree.
    """
    level += 1
    token = head.token
    content = head.content
    li = []
    out = ""
    for node in content:
        if(type(node) != type(par.ParseTree("sample","sample"))):
            li.append(node)
        else:
            li.append(node.token)

    out = (level,li)


    #iterate through the components of the BNF
    for node in content:
        if(type(node) == type(par.ParseTree("sample","sample"))):
            out += getTree(node,level)
    return out


def print_tokens(tokens):
    """
    Prints tokens returned from Lexer

    Args:
        tokens: Tokens generated from the Lexer
    """
    print(lex.tokensToString(deepcopy(tokens)))



def main(args):
    """
    The main function of the frontend, takes in command line input via an object from argparse, and the name of the file.

    Args:
        args: The object that contains the command line arguements.
        fi: The file object that is open.
    """

    if args.bnf:
        btp.main(args.bnf)
        importlib.reload(par)
    astree = None
    symTab = None
    try:

        fi = open(args.input_file, "r")

        #Read in file
        text_input = fi.read()
        fi.close()

        #Pre-process the text
        text_input = pre.run(text_input, args.input_file)

        #setup lexer, produce tokens, check for invalid tokens
        lexer = lex.Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        lex.validateTokens(tokens)

        if args.lex or args.all:
            # Print the tokens from the lexer
            print_tokens(tokens)

        #set up parser and parse the given tokens
        pg = par.Parser()
        pg.parse()
        parser = pg.get_parser()
        parser.parse(tokens)

        # Retrieve the head of the parse tree
        head = pg.getTree()

        if args.tree or args.all:
            # Represent parse tree as a list with levels
            # print(head.getListView(0))
            print(head.__repr__)
            # print(str(head) == head.getListView(0))

        if args.pretty or args.all:
            # Pretty print parse tree
            # pprint_tree(head)
            # head.print_ParseTree()
            print(head)

        # Build Abstract Syntax Tree
        
        astree = ast.buildAST(head)
        # if(astree != None):
        if args.ast or args.all:
            # Pretty print AST
            # astree.print_AST()
            print(astree)

        # Initialize symbol table and begin semantic analysis
        symTab = sym.symbol_table(astree)
        symTab.analyze()

        if args.symbol_table or args.all:
            print (symTab)

        semAnal = semantic.semantic(astree,symTab.symbols)
        semAnal.semanticAnalysis()
        if args.errors or args.all:
            semAnal.printSemanticErrors()
        # print(astree)
        # if(astree == None):
        #     print("Error in input to parser")
        #     sys.exit()
    except LexingError as err:
        exit()

    except AssertionError as err:
        # parser has it's own detailed error printing
        pg.print_error()
        exit()

    except BaseException as err:
        traceback.print_exc()
        print(f"Unrecoverable exception occured. Exiting...")
        exit()
    if(astree == None or symTab == None):
        print("Something unexpected happened...")
    if(semAnal.errors != []):
        semAnal.printSemanticErrors()
        exit(0)
    
    return astree, symTab

if __name__ == "__main__":
    #command line arguements

    #decription of the comiler
    cmd_options = argparse.ArgumentParser(description='Frontend of the compiler. Can produce tokens and syntax tree')

    cmd_options.add_argument('--all',help='Prints out all intermediate representations as they are encountered in the compilation process', action="store_true")

    #input file option
    cmd_options.add_argument('input_file', metavar='<filename.c>', type=str, help='Input c file.')

    #Arguement to print tokens from lexer
    cmd_options.add_argument('-l','--lex', help='Prints out tokens from lexer', action='store_true')

    #Prints string representation of parse tree....
    cmd_options.add_argument('-t','--tree', help='Prints string representation of parse tree.', action="store_true")

    cmd_options.add_argument('-p','--pretty',help='Prints a pretty verision of the tree, and does not print the tokens', action="store_true")

    #Print all output from lexer, parser, etc....
    cmd_options.add_argument('-a','--ast', help='Prints out the abstract syntax tree.', action="store_true")

    cmd_options.add_argument('-s','--symbol_table', help='Prints out the known and unknown symbols encountered during semantic analysis.', action="store_true")

    cmd_options.add_argument('-b', '--bnf', nargs='?', const=os.path.realpath("./BNF_definition"), type=str, help='Rebuilds the parser using the current BNF grammar')

    cmd_options.add_argument('-e', '--errors',help='Prints out the errors in the semantic analysis',action="store_true")

    #generate arguements
    args = cmd_options.parse_args()


    #open file and pass into main.
    if args.input_file and args.input_file.endswith(".c"):
        main(args)
    else:
        #if not c file.
        if not args.input_file.endswith(".c"):
            print("Error file must end with .c")
        cmd_options.print_help()
        exit()


