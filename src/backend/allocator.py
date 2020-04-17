from copy import copy
import importlib
import os
from inspect import getsourcefile
from importlib.machinery import SourceFileLoader

asmn = SourceFileLoader("ASMNode", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/ASMNode.py").load_module()
stk = SourceFileLoader("stack", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/stack.py").load_module()



class Allocator():

    def allocateRegisters(asm_list):

        # Set up directory of registers
        # We give it assembly list because we may need it to "look ahead" to get next-available-register
        stack = stk.Stack()
        regDir = RegisterDirectory(asm_list, stack)
        # regDir = RegisterDirectory(asm_list)

        

        for idx, instr in enumerate(asm_list):
            copy_list = copy(asm_list[idx])
            case = 0

            # Case 0: Just the operation. (ie. labels, returns, etc..)
            if asm_list[idx].noParams:
                case = 0
                pass

            # Case 4: Find last 2 used registers, free left side, update right side.

            # left    ->  %REG
            # right   ->  %REG
            #
            elif asm_list[idx].leftNeedsReg and asm_list[idx].rightNeedsReg:

                leftReg = regDir.var_in_reg(asm_list[idx].left)
                if leftReg == None:
                    leftReg = regDir.var_in_stack(asm_list[idx].left)
                    if leftReg == None:
                        leftReg = regDir.get_free(var=asm_list[idx].left)

                asm_list[idx].left = leftReg.name

                rightReg = regDir.var_in_reg(asm_list[idx].right)
                if rightReg == None:
                    rightReg = regDir.var_in_stack(asm_list[idx].right)
                    if rightReg == None:
                        rightReg = regDir.get_free(var=asm_list[idx].right)

                asm_list[idx].right = rightReg.name

                regDir.update_reg(rightReg.name, var="")
                case = 4
                pass

            # Case 1: Moving a literal to a new register
            #
            # left    ->  $1
            # right   ->  %REG
            #
            elif asm_list[idx].leftLiteral and asm_list[idx].rightNeedsReg:

                newReg = regDir.var_in_reg(asm_list[idx].left)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].left)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].left)

                asm_list[idx].right = newReg.name

                regDir.update_reg(newReg.name, asm_list[idx].left)
                case = 1
                pass

            # Case 5: After an operation like add/sub this case is for moving the answer to a tmp variable
            #
            # left    ->  %REG
            # right   ->  _1
            #
            elif asm_list[idx].leftNeedsReg and asm_list[idx].rightHasVar:

                # last used register becomes our source register
                newReg = regDir.last_used[-1]
                asm_list[idx].left = newReg.name

                # Search for destination register, allocate one if necessary
                newReg = regDir.var_in_reg(asm_list[idx].right)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].right)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].right)

                asm_list[idx].right = newReg.name

                case = 5
                pass

            # Case 2: Moving a literal to variable.
            #         Need to find register corresponding to that variable and update it.
            #         If no register exists, allocate one.
            #
            # left    ->  $1
            # right   ->  _1
            #
            elif asm_list[idx].leftLiteral and asm_list[idx].rightHasVar:

                newReg = regDir.var_in_reg(asm_list[idx].right)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].right)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].right)

                regDir.update_reg(newReg.name, var=asm_list[idx].right)
                asm_list[idx].right = newReg.name

                case = 2
                pass

            # Case 3: Performing operation on variable. Need to find register corresponding to
            #          that variable. NOTE: I check if right side is a literal because that means
            #          right side is a register with a literal value already set.
            #          For this case, I assume last used register is the correct one.
            #          Should I be searching instead?
            #
            # left    ->  _1
            # right   ->  %REG
            #
            elif asm_list[idx].leftHasVar and asm_list[idx].rightNeedsReg:

                # Search for source register, allocate one if necessary
                newReg = regDir.var_in_reg(asm_list[idx].left)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].left)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].left)

                asm_list[idx].left = newReg.name

                # Search for destination register, allocate one if necessary
                newReg = regDir.var_in_reg(asm_list[idx].right)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].right)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].right)

                asm_list[idx].right = newReg.name


                case = 3
                pass

            

            

            # Case 6: NOTE: Not too sure when this case occurs. Currently we are not catching it.

            # left    ->  %REG
            # right   ->  None
            #
            # elif asm_list[idx].leftNeedsReg and asm_list[idx].rightNone:
            #     case = 6
            #     pass

            # Case 7: Moving values from variable to variable.
            #
            # left    ->  _1
            # right   ->  a
            #
            elif asm_list[idx].leftHasVar and asm_list[idx].rightHasVar:

                # search for source register, allocate if necessary
                newReg = regDir.var_in_reg(asm_list[idx].left)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].left)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].left)

                asm_list[idx].left = newReg.name   
                
                # search for destination register, allocate if necessary
                newReg = regDir.var_in_reg(asm_list[idx].right)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].right)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].right)

                asm_list[idx].right = newReg.name
                
                case = 7
                pass

            # Case 8: left side needs variable. This is for arithmetic operations that
            #         only have one operand and store the result in another register by default.
            #         Example:
            #         idiv rsi    --- Will store result in %rax and not use %rsi again, so we free it.
            #
            elif asm_list[idx].rightNone:

                if asm_list[idx].left != "rbp":

                    # search for source register, allocate if necessary
                    newReg = regDir.var_in_reg(asm_list[idx].left)
                    if newReg == None:
                        newReg = regDir.var_in_stack(asm_list[idx].left)
                        if newReg == None:
                            newReg = regDir.get_free(var=asm_list[idx].left)

                    asm_list[idx].left = newReg.name

                case = 8



            # Case 9: left side needs register but right side is hard-coded
            #       (ie. %rax or something like that)
            #
            elif asm_list[idx].leftHasVar:

                # search for source register, allocate if necessary
                newReg = regDir.var_in_reg(asm_list[idx].left)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].left)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].left)

                asm_list[idx].left = newReg.name

                # regDir.free_reg(asm_list[idx].left)
                case = 9
                pass

            # Case 10: rigt side needs register but left side is hard coded

            elif asm_list[idx].rightHasVar:

                # search for destination register, allocate if necessary
                newReg = regDir.var_in_reg(asm_list[idx].right)
                if newReg == None:
                    newReg = regDir.var_in_stack(asm_list[idx].right)
                    if newReg == None:
                        newReg = regDir.get_free(var=asm_list[idx].right)

                asm_list[idx].right = newReg.name

                case = 10

            else:

                # should be caught by Case 9...
                if asm_list[idx].right == "rax":
                    # search for source register, allocate if necessary
                    newReg = regDir.var_in_reg(asm_list[idx].left)
                    if newReg == None:
                        newReg = regDir.var_in_stack(asm_list[idx].left)
                        if newReg == None:
                            newReg = regDir.get_free(var=asm_list[idx].left)

                    asm_list[idx].left = newReg.name

                case = "E"
                pass

            # We need to update the assembly list in the register directory.
            # The directory used the assembly list to "look-ahead" in some cases,
            # and to be aware of which index is currently being looked at.
            regDir.asm.pop(0)

            print(f"{str(asm_list[idx]):20}", f"case = {case}\t", f"{str(copy_list)}")


        return asm_list





class RegisterDirectory():

    used_regs = ["rcx","rbx","rsi","r8","r9","r10","r11","r12","r13","r14","r15"] #these are the total registers used.

    class registerData():

        def __init__(self, register_name):

            self.name = register_name
            self.isOpen = True
            self.var_value = None
            # self.literal_value = None

        def update(self, var):
            self.var_value = var
            # self.literal_value = lit
            self.isOpen = False

        def free(self):
            self.isOpen = True
            self.var_value = None
            # self.literal_value = None

    def __init__(self, asm, stack):
        self.real_asm = asm
        self.asm = copy(asm)
        self.stack = stack
        self.regs = []
        self.last_used = []

        for reg in self.used_regs:
            self.regs.append(self.registerData(reg))

    def var_in_reg(self, var):
        """
        Find register containing passed in variable name.

        Returns either the node or None
        """
        for reg in self.regs:
            if var == reg.var_value:
                return reg
        return None

    def var_in_stack(self, var):
        """
        Find/Create registerData that contains stack pointer 
        with offset corresponding to the passed in variable name.
        """
        offset = self.stack.find_offset(var)
        if offset == None:
            return None
        
        regData = self.registerData(f"{offset}(rsp)")
        regData.update(var)

        return regData


    def get_free(self, var):
        """
        Finds lastest register that isnt being used else performs register eviction,
        updates and returns that register.
        """

        #Search for free register.
        for ind,reg in enumerate(self.regs):
            if self.regs[ind].isOpen == True:

                self.regs[ind].update(var)
                self.regs[ind].isOpen = False
                self.last_used.append(self.regs[ind])

                return self.regs[ind]

        # No free registers, evict register and return it
        tmpReg = self.evict_register(var)
        self.last_used.append(tmpReg)
        return tmpReg



    def update_reg(self, name, var):
        """
        Updates the given register using the name, isopen, var_value_value.
        """
        for reg in self.regs:
            if reg.name == name:
                reg.update(var)
                self.last_used.remove(reg)
                self.last_used.append(reg)


    def free_reg(self, name):
        print("This shit is not supposed to be called")
        """
        Frees the given register searching by the given register name
        """
        for reg in self.regs:
            if reg.name == name:
                self.last_used.remove(reg)
                reg.free()


    def evict_register(self, var):
        """
        Evicts register that is the last used in the code ahead.
        """

        order_used = []
        for line in self.asm:
            if line.leftHasVar:

                left = self.var_in_reg(line.left)
                if left:
                    order_used.append(left)

            if line.rightHasVar:

                right = self.var_in_reg(line.right)
                if right:
                    order_used.append(right)

            if [x for x in order_used if x not in self.regs] == [] and order_used != []:
                break

        #gets the registers not used.
        # left_over = self.regs - order_used
        left_over = [x for x in order_used if x not in self.regs]
        # This means no available register
        # if left_over == []:


        # if order_used != []:
        #     result = order_used.pop()

        #     stack_offset = self.stack.find_offset(result.var_value)
        #     if stack_offset == None:
        #         # need to insert into stack and get offset?
        #         stack_offset = self.stack.insert(result.var_value)
        #         pass

        #     # Instruction to move this register's value onto stack
        #     node = asmn.ASMNode("mov", result.name, f"{stack_offset}(rsp)")

        #     # Insert instruction into the modified ASM list at adjusted index
        #     self.real_asm.insert(len(self.real_asm) - len(self.asm), node)
        #     self.asm.insert(0, node)

        #     self.update_reg(result.name, var)

        # else:
        stack_offset = self.stack.insert(var)
        result = self.registerData(f"{stack_offset}(rsp)")
        result.update(var)

        return result







        # # We have some registers that will not be used again.
        # else:

        #     # NOTE: May need to free leftover regs not sure yet.
        #     result = left_over.pop()
        #     self.update_reg(result.name, var)
        #     return result




