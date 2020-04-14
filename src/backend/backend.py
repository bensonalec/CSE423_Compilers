from inspect import getsourcefile
from importlib.machinery import SourceFileLoader
import os

asmn = SourceFileLoader("ASMNode", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/ASMNode.py").load_module()
ir1 = SourceFileLoader("IR_Lv1_Builder", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../optimizer/IR_Lv1_Builder.py").load_module()

def main( args, IR):

    asm = [z for x in IR.IR for y in x.treeList for z in y.asm()]

    if args.a1:
        for i in asm:
            print(str(i))

    reg_list = [
    ]

    reg_dir = {
        "rax" : None,
        "rcx" : None,
        "rdx" : None,
        "rbx" : None,
        "rsi" : None,
        "rdi" : None,
        "rsp" : None,
        "rbp" : None,
        "r8"  : None,
        "r9"  : None,
        "r10" : None,
        "r11" : None,
        "r12" : None,
        "r13" : None,
        "r14" : None,
        "r15" : None,
    }

    var_dir = {
    }

    for instr in asm:

        # Case 1: right side is 'tmp'
        if not instr.leftTmp and instr.rightTmp:
            if instr.left.startswith("$"):
                tmpReg = [x for x,y in reg_dir.items() if y == None][0]
                reg_dir[tmpReg] = instr.left
                instr.right = tmpReg
                # Figure out the next availabe register, ie the right hand of the instruction, and give the respective key the left hand operand which is a immediate value
                pass
            elif instr.left in reg_dir:
                instr.right = var_dir[instr.right]
                pass
            elif instr.varName in var_dir:
                print("This happened keaton!")
                tmpReg = [x for x,y in reg_dir.items() if y == None][0]
                reg_dir[tmpReg] = var_dir[instr.varName] # Should be the memory location of the variable
                var_dir[instr.varName] = tmpReg
                # Figure out the next availabe register, ie the right hand of the instruction, and give the respective key the left hand operand which is a variable or memory location
                pass
            else:
                print ("Something happened that should have been foreseen around line 62")

        # Case 2: left side is 'tmp'
        # mov $1, rax
        #when tmp is not set, it can be a given register or a constant

        elif instr.leftTmp and not instr.rightTmp:
            if instr.left == None and instr.right in reg_dir:
                # tmpValue = reg_dir[instr.varName]
                reg_dir[instr.right] = tmpValue
                # right hand side is a register which means it needs to be updated depending on the operation
                pass
            else:
                # see if the variable is in a register already. If it is, update the register else move the variable to a register and assign it?
                #check if instr.right is in a reg
                if instr.right in var_dir:
                    #update register
                    var_dir[instr.right] = ???
                    pass
                else:
                    #move the var to a register and assing it
                    tmpReg = [x for x,y in reg_dir.items() if y == None][0]
                    reg_dir[tmpReg] =
                    pass


        # Case 3: Both sides are 'tmp'
        elif instr.leftTmp and instr.rightTmp:
            # For left side:
            # We can free this register as it isnt needed any longer (for most operations?)

            # For right side:
            # Allocate next available register with the value recovered from whatever left side contains
            pass

        # Case 4: Neither are 'tmp'
        elif not instr.leftTmp and not instr.rightTmp:
            if instr.left and instr.right:
                #should not enter
                pass
            elif instr.left.startswith("$") and instr.right in reg_dir:
                #should be correct posibly free intra.right if not used anymore.
                pass

            elif instr.left in reg_dir and instr.right in reg_dir:
                #since instr.left is a reg we can see if we can free it if it is not used.
                pass

            pass

    # if args.a1:
    #     for i in asm:
    #         print(str(i))

if __name__ =="__main__":
    main()