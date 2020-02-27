"""
This module serves as the main interface to the optimization process in order to streamline the compiler.
"""

import argparse
import importlib

ir1 = importlib.import_module("IR_Lv1_Builder", __name__)

def mainIR(args, fi):
    """
    .. todo::
    This is the function that when given a specific IR will produce linear intermediate representations for teh inputted program.
    """
    pass

def mainAST(args,astHead,symbolTable):
    """
    This is the function that when given an AST and a symbol table will produce linear intermediate representations for teh inputted program.

    Args:
        args: The commandline arguments that belong to the optimizer.
        astHead: The root node of the AST.
        symbolTable: The list of valid entries throughout the program.

    Returns:
        The lowest level of IR produced.
    """
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