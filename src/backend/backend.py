from inspect import getsourcefile
from importlib.machinery import SourceFileLoader
import os

asmn = SourceFileLoader("ASMNode", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/ASMNode.py").load_module()
ir1 = SourceFileLoader("IR_Lv1_Builder", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../optimizer/IR_Lv1_Builder.py").load_module()

def main( args, IR):
	asm = [y.asm() for x in IR.IR for y in x.treeList]
	
	if args.a1:
		for i in asm:
			print(str(i))
	pass

if __name__ == "__main__":
        main()