"""
This module serves as the main interface to the optimization process in order to streamline the compiler.
"""

import os
import argparse
from importlib.machinery import SourceFileLoader

ir1 = SourceFileLoader("IR_Lv1_Builder", f"{os.path.dirname(__file__)}/IR_Lv1_Builder.py").load_module()
import_ir = SourceFileLoader("import_ir", f"{os.path.dirname(__file__)}/import_ir.py").load_module()

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
    if args.input:

        inp = import_ir.import_ir(args.input)
        l1ir = inp.verify()

    else:
        ir = ir1.LevelOneIR(astHead,symbolTable)
        l1ir = ir.construct()
        ir.optimize()

    if args.IR1 or args.all:
        for x in l1ir: print (x)
    pass


if __name__ == "__main__":
    cmd_options = argparse.ArgumentParser(description='Optimizer of the compiler. Can take in an AST and Symbol Table or a File with an IR')

    cmd_options.add_argument('--all',help='Prints out all intermediate representations as they are encountered in the compilation process', action="store_true")
    cmd_options.add_argument('-O', '--opt', type=int, choices=range(3), default=0, help='Determines the optimization level')
    cmd_options.add_argument('-i', action='store', dest="input", type=str, help="Used to input IR from file")
    args = cmd_options.parse_args()

    print(args.input)

    mainAST(args,astHead,symbolTable)