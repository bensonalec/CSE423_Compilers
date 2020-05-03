from inspect import getsourcefile
from importlib.machinery import SourceFileLoader
import os

asmn = SourceFileLoader("ASMNode", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/ASMNode.py").load_module()
ir1 = SourceFileLoader("IR_Lv1_Builder", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../optimizer/IR_Lv1_Builder.py").load_module()
alloc = SourceFileLoader("allocator", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../backend/allocator.py").load_module()


def main(args, IR):
    """
    The main backend function, does register allocation and converts a given IR to assembly

    Args:
        args: The command line arguments of the operation (print asm, etc.)
        IR: The intermediary representation in a list of IRNode objects that is being converted to assembly
    """
    # List of assembly instructions before given allocated registers
    asm = [z for x in IR.IR for y in x.treeList for z in y.asm()]

    if args.a1:
        for i in asm:
            print(str(i)) 

    print("")
    print("")
          
    # Allocate registers for assembly instructions
    allocator = alloc.Allocator
    asm = allocator.allocateRegisters(asm)

    if args.a1:
        for i in asm:
            print(str(i)) 

if __name__ =="__main__":
    main()