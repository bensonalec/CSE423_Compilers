import argparse
import importlib

frontend = importlib.import_module("frontend.frontend", package="frontend")
#optimization = importlib.import_module("optimization.optimization", package="optimization)
#backend = importlib.import_module("backend.backend", package="backend")

def main(args, fi):

    # Execution of the Frontend. 
    # This returns the first intermediate representation of the inputed C file, an Abstract Syntax Tree.
    ast = frontend.main(args, fi)



    # Execution of Optimization


    # Execution of Backend





if __name__ == "__main__":
    #command line arguements

    #decription of the compiler
    cmd_options = argparse.ArgumentParser(description='Main execution of C compiler. Can produce different representations of inputed C code. (i.e. tokens, parse tree, abstract syntax tree, etc.)')
    
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