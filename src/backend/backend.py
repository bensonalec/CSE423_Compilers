import importlib

def main( args, IR):
	asm = [y.asm() for x in IR for y in x.treelist]
	
	if args.a1:
		for i in asm:
			print(str(i))
	pass

if __name__ == "__main__":
        main()