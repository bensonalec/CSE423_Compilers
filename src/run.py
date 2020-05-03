"""
This module serves as the main interface to the compiler. It connects all the parts of the compiler in such a way that all representations are handed off to the next step.
"""

from inspect import getsourcefile
import os
import argparse
from importlib.machinery import SourceFileLoader

frontend = SourceFileLoader("frontend.frontend", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/frontend/frontend.py").load_module()
optimizer = SourceFileLoader("optimizer.optimizer", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/optimizer/optimizer.py").load_module()
backend = SourceFileLoader("backend.backend", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/backend/backend.py").load_module()
def main(args):
    """
    Main control flow for our compiler. Takes in command line arguments, and executes the frontend, optimizer, and backend in order if necessary.

    Args:
        args: The argparse object  
    """
    try:

        # Execution of the Frontend.
        # This returns the Abstract Syntax Tree and Symbol Table
        if not args.input:
            ast, sym = frontend.main(args)
        else:
            ast = None
            sym = None

        # Execution of Optimization
        ir = optimizer.main(args,ast,sym)

        # Execution of Backend
        backend.main(args, ir)

    except BaseException as err:
        print("Compilation failed: ", err)
        exit(1)




if __name__ == "__main__":
    
    #command line arguements
    cmd_options = argparse.ArgumentParser(description='Main execution of C compiler. Can produce different representations of inputed C code. (i.e. tokens, parse tree, abstract syntax tree, etc.)')
    cmd_options.add_argument('--all',help='Prints out all intermediate representations as they are encountered in the compilation process', action="store_true")
    cmd_options.add_argument('input_file', metavar='<filename.c>', type=str, help='Input c file.')
    cmd_options.add_argument('-l','--lex', help='Prints out tokens from lexer', action='store_true')
    cmd_options.add_argument('-t','--tree', help='Prints string representation of parse tree.', action="store_true")
    cmd_options.add_argument('-p','--pretty',help='Prints a pretty verision of the tree, and does not print the tokens', action="store_true")
    cmd_options.add_argument('-ast','--ast', help='Prints out the abstract syntax tree.', action="store_true")
    cmd_options.add_argument('-s','--symbol_table', help='Prints out the known and unknown symbols encountered during semantic analysis.', action="store_true")
    cmd_options.add_argument('-e', '--errors',help='Prints out the errors in the semantic analysis',action="store_true")
    cmd_options.add_argument('-b', '--bnf', nargs='?', const=os.path.abspath(os.path.dirname(__file__)) + "/frontend/BNF_definition", type=str, help='Rebuilds the parser using the current BNF grammar')
    cmd_options.add_argument('-O', '--opt', type=int, choices=range(3), default=0, help='Determines the optimization level')
    cmd_options.add_argument('-ir',help='Output the first level of IR in the optimizer phase', action="store_true")
    cmd_options.add_argument('-i', '--input', action='store_true', help="Used to input IR from file")
    cmd_options.add_argument('-asm', '--asm', help='Prints the assembly after the first pass.', action="store_true")
    cmd_options.add_argument('--IRout', metavar='<output-filename>', type=str, default=None, help="Used to output the final generated IR to a file")
    cmd_options.add_argument('--ASMout', metavar='<output-filename>', type=str, default=None, help="Used to output the generated assembly to a file")

    #generate arguements
    args = cmd_options.parse_args()

    #open file and pass into main.
    if args.input_file and args.input_file.endswith(".c"):
        main(args)
    elif args.input: #if we need to take input file in redirect input file
        args.input = args.input_file
        main(args)
    else:
        #if not c file.
        if not args.input_file.endswith(".c"):
            print("Error file must end with .c")
        cmd_options.print_help()
        exit()
