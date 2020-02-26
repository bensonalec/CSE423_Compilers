import argparse
import importlib

ir1 = importlib.import_module("IR_Lv1_Builder", __name__)

def mainIR(args, fi):
    pass

def mainAST(args,astHead,symbolTable):
    ir = ir1.LevelOneIR(astHead,symbolTable)
    ir.construct()
    pass

if __name__ == "__main__":
    cmd_options = argparse.ArgumentParser(description='Optimizer of the compiler. Can take in an AST and Symbol Table or a File with an IR')

    cmd_options.add_argument('--all',help='Prints out all intermediate representations as they are encountered in the compilation process', action="store_true")
    cmd_options.add_argument('-O0',help='Does no optimization')
    cmd_options.add_argument('-O1',help='Optimize the symbol table and AST')
    args = cmd_options.parse_args()

    mainAST(args,astHead,symbolTable)