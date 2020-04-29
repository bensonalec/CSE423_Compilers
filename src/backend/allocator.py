from copy import copy
import importlib
import os
from inspect import getsourcefile
from importlib.machinery import SourceFileLoader

asmn = SourceFileLoader("ASMNode", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/ASMNode.py").load_module()
stk = SourceFileLoader("stack", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/stack.py").load_module()



class Allocator():

    def allocateRegisters(asm_list):

        newAsm_list = []

        # Set up directory of registers
        # We give it assembly list because we may need it to "look ahead" to get next-available-register
        stack = stk.Stack()
        regDir = RegisterDirectory(asm_list, newAsm_list, stack)
        # regDir = RegisterDirectory(asm_list)

        idx = -1

        for instr in asm_list:
            idx += 1
            copy_list = copy(instr) #DEBUGGING
            case = 0                #DEBUGGING

            # Case functionDecl
            if instr.functionDecl:
                # Sets up the stack with the parameters
                stack.scope_change()
                [stack.stk.append(x) for x in instr.stack]

                # Sets up the registers with the correct values
                [regDir.update_reg(x, y) for x, y in instr.regDir.items()]
                [regDir.free_reg(x) for x in ["rbx", "r12", "r13", "r14", "r15"]]
                pass


            # Case regIsParam
            elif instr.regIsParam:
                paramReg = regDir.reg_in_use(instr.right)

                # if register already in use
                if paramReg:
                    regDir.paramSwap(paramReg, instr.left)
                    pass


            # Case 0: Dont touch this instruction (labels, ret, etc..)
            elif instr.dontTouch:

                if instr.command == "pop" and instr.left == "rbp":
                    newAsm_list.append(asmn.ASMNode("add", f"${stack.dist_from_base()}", f"%rsp"))

                #NOTE cannot continue here code needed at the end of the loop.
                case = 0
                pass

            # Case 4: Operation with two registers.
            #         NOTE: Currently the value on right is being erased..should we catch the instances of "mov"?
            #               and not erase?
            # left    ->  %REG
            # right   ->  %REG
            #
            elif instr.leftNeedsReg and instr.rightNeedsReg:

                newReg = regDir.find_reg(instr.left, idx)
                instr.left = newReg.name
                instr.leftOffset = newReg.offset

                newReg = regDir.find_reg(instr.right, idx)
                instr.right = newReg.name
                instr.rightOffset = newReg.offset
                regDir.update_reg(newReg.name, var="")
                case = 4
                pass

            # Case 1: Moving a literal to a new register
            #
            # left    ->  $1
            # right   ->  %REG
            #
            elif instr.leftLiteral and instr.rightNeedsReg:
                if(instr.right):
                    newReg = regDir.find_reg(instr.right, idx)
                else:
                    newReg = regDir.find_reg(instr.left, idx)

                ogRight = instr.right
                instr.right = newReg.name
                instr.rightOffset = newReg.offset

                if ogRight == "":
                    regDir.update_reg(newReg.name, instr.left)

                case = 1
                pass

            # Case 5: After an operation like add/sub this case is for moving the answer to a tmp variable
            #
            # left    ->  %REG
            # right   ->  _1
            #
            elif instr.leftNeedsReg and instr.rightHasVar:

                # last used register becomes our source register
                newReg = regDir.last_used[-1]
                instr.left = newReg.name
                instr.leftOffset = newReg.offset

                newReg = regDir.find_reg(instr.right, idx)
                instr.right = newReg.name
                instr.rightOffset = newReg.offset
                case = 5
                pass

            # Case 2: Moving a literal to variable.
            #         Need to find register corresponding to that variable and update it.
            #         If no register exists, allocate one.
            #
            # left    ->  $1
            # right   ->  _1
            #
            elif instr.leftLiteral and instr.rightHasVar:

                newReg = regDir.find_reg(instr.right,idx)

                regDir.update_reg(newReg.name, var=instr.right)

                instr.right = newReg.name
                instr.rightOffset = newReg.offset
                case = 2
                pass

            # Case 3:
            # NOTE: Looks similiar to Case 4 and Case 5...could we merge them and add some conditionals?
            #
            # left    ->  _1
            # right   ->  %REG
            #
            elif instr.leftHasVar and instr.rightNeedsReg:

                newReg = regDir.find_reg(instr.left,idx)
                instr.left = newReg.name
                instr.leftOffset = newReg.offset

                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name
                instr.rightOffset = newReg.offset

                case = 3
                pass

            # Case 7: Moving values from variable to variable.
            #       NOTE: Looks similiar to Case 3/4/5 merge them?
            # left    ->  _1
            # right   ->  a
            #
            elif instr.leftHasVar and instr.rightHasVar:

                newReg = regDir.find_reg(instr.left,idx)
                instr.left = newReg.name
                instr.leftOffset = newReg.offset

                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name
                instr.rightOffset = newReg.offset
                case = 7
                pass

            # New case 11 for: mov $1 rax
            elif instr.right == "rax" and instr.leftLiteral:
                case = 11
                pass


            # Case 8: left side needs variable. This is for arithmetic operations that
            #         only have one operand and store the result in another register by default.
            #         Example:
            #         idiv rsi    --- Will store result in %rax and not use %rsi again, so we free it.
            #       NOTE: similiar to Case 9/10..merge?
            elif instr.right == "" or instr.right == "rax":

                if instr.left != "rbp":

                    newReg = regDir.find_reg(instr.left, idx)
                    instr.left = newReg.name
                    instr.leftOffset = newReg.offset

                case = "8-9"



            # Case 9: left side needs register but right side is hard-coded
            #       (ie. %rax or something like that)
            #   NOTE: inverse of Case 10...merge?
            # elif instr.leftHasVar:
            #     newReg = regDir.find_reg(instr.left)
            #     instr.left = newReg.name

            #     case = 9
            #     pass

            # Case 10: rigt side needs register but left side is hard coded
            #   NOTE: inverse of Case 9...merge?
            elif instr.rightHasVar:
                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name
                instr.rightOffset = newReg.offset
                case = 10
            else:
                case = "E"
                pass


            # Ensures that shifting only uses the lower byte of the appropriate register
            if instr.command in ["sal", "sar"]:
                if instr.left.endswith("x"):
                    instr.left = f"{instr.left[1]}l"
                elif instr.left.endswith("i") or instr.left.endswith("p"):
                    instr.left = f"{instr.left[1:]}l"
                elif instr.left.startswith("r"):
                    instr.left = f"{instr.left}b"

            # We need to update the assembly list in the register directory.
            # The directory used the assembly list to "look-ahead" in some cases,
            # and to be aware of which index is currently being looked at.
            #regDir.asm.pop(0)
            newAsm_list.append(instr)

            print(f"{str(instr):20}", f"case = {case}\t", f"{str(copy_list)}")
            # print(f"{str(instr):20}", f"case = {case}\t", f"{str(copy_list)}", f"index : {idx}")
        # print("")

        # newAsm_list = [x for x in newAsm_list if x.left != x.right and x.command != "mov"]

        return newAsm_list



class RegisterDirectory():

    used_regs = ["rcx","rbx","rdi","rsi","r8","r9","r10","r11","r12","r13","r14","r15"] #these are the total registers used.

    class registerData():

        def __init__(self, register_name):

            self.name = register_name
            self.isOpen = True
            self.var_value = None
            self.offset = None
            # self.literal_value = None

        def update(self, var, offset):
            self.var_value = var
            # self.literal_value = lit
            self.isOpen = False
            self.offset = offset

        def free(self):
            self.isOpen = True
            self.var_value = None
            self.offset = None
            # self.literal_value = None

        def is_tmp(self):
            if self.var_value:
                return self.var_value.startswith("tV_")

            return True

        def __str__(self):
            return f"{self.name} {self.isOpen} {self.var_value} {self.offset}"

    def __init__(self, asm, newAsm_list, stack):
        # self.real_asm = asm
        self.newAsm = newAsm_list
        self.asm = asm
        self.stack = stack
        self.regs = []
        self.last_used = []

        for reg in self.used_regs:
            self.regs.append(self.registerData(reg))

    def find_reg(self, name, idx):
        """
        Finds register containing the passed in variable name.

        First, searches local registers.
        Second, searches on stack.
        Else, allocates new register

        Returns:
            new RegisterData object or None
        """
        newReg = self.var_in_reg(name)
        if newReg == None:
            newReg = self.get_free(name, idx)
            if newReg == None:
                # print("HERERE")
                return self.evict_register(name, idx)
            return self.var_in_stack(name, newReg)

        return newReg

    def var_in_reg(self, var):
        """
        Find register containing passed in variable name.

        Returns either the node or None
        """
        for reg in self.regs:
            if var == reg.var_value:
                return reg
        return None

    def var_in_stack(self, var, reg):
        """
        Find/Create registerData that contains stack pointer
        with offset corresponding to the passed in variable name.
        """
        # print("HERER", var, reg.name)
        offset = self.stack.find_offset(var)
        if offset == None:
            # print("offset not found")
            reg.update(var, None)
            return reg

        print ("stack")

        return self.swap(reg, var)

        # regData = self.registerData(f"{offset}(rbp)")
        # regData = self.registerData("rbp")
        # regData.update(var, offset)

        # return regData


    def get_free(self, var, idx):
        """
        Finds lastest register that isnt being used else performs register eviction,
        updates and returns that register.
        """

        #Search for free register.
        for ind,reg in enumerate(self.regs):
            # print (self.regs[ind].name, [x.name for x in self.last_used[-2:]])
            if self.regs[ind].isOpen == True:

                self.regs[ind].update(var, None)
                self.regs[ind].isOpen = False
                self.last_used.append(self.regs[ind])

                return self.regs[ind]

        for ind,reg in enumerate(self.regs):
            if (
                self.regs[ind].is_tmp()
                    and
                self.var_in_reg(self.asm[idx].left) != self.regs[ind]
                    and
                # self.var_in_reg(self.asm[idx].right) == self.regs[ind]
                    # and
                self.regs[ind] not in self.last_used[-2:]
                ):
                # print("here")
                print([x.name for x in self.last_used[-3:]])
                self.regs[ind].update(var, None)
                self.regs[ind].isOpen = False
                self.last_used.append(self.regs[ind])

                return self.regs[ind]

        return None



    def update_reg(self, name, var):
        """
        Updates the given register using the name, isopen, var_value_value.
        """
        for reg in self.regs:
            if reg.name == name:
                reg.update(var, None)
                if reg in self.last_used:
                    self.last_used.remove(reg)
                self.last_used.append(reg)


    def free_reg(self, name):
        """
        Frees the given register searching by the given register name
        """
        for reg in self.regs:
            if reg.name == name:
                # self.last_used.remove(reg)
                reg.free()

    def evict_register(self, var, index):
        """
        Evicts register that is the last used in the code ahead.
        """
        order_used = []
        for line in self.asm[index:]:
            if line.leftHasVar:

                left = self.var_in_reg(line.left)
                if left:
                    order_used.append(left)

            if line.rightHasVar:

                right = self.var_in_reg(line.right)
                if right:
                    order_used.append(right)

            if [x for x in self.regs if x not in order_used] == [] and order_used != []:
                break

        #gets the registers not used.
        left_over = [x for x in self.regs if x not in order_used]

        result = left_over.pop() if left_over else self.regs[0]

        if result.is_tmp() and (var.startswith("$") or var.startswith("tV_")):
            result.update(var, None)
            return result

        print (result.is_tmp(), var.startswith("tV_"))
        print (result.name, var)

        return self.swap(result, var)

    def swap(self, reg, var):

        print (reg, var)

        if reg.is_tmp() or reg.isOpen:
            pass
        else:
            rO = self.stack.find_offset(reg.var_value)
            if not rO:
                rO = self.stack.insert(reg.var_value)
                # print(var)
                self.newAsm.append(asmn.ASMNode("sub", "$4", "rsp"))
            self.newAsm.append(asmn.ASMNode("mov", reg.name, "rbp", rightOffset=rO))

        offset = self.stack.find_offset(var)
        self.newAsm.append(asmn.ASMNode("mov", "rbp", reg.name, leftOffset=offset))

        reg.update(var, None)

        return reg

    def paramSwap(self, paramReg, var):
        if not paramReg.is_tmp():
            rO = self.stack.find_offset(paramReg.var_value)
            if not rO:
                rO = self.stack.insert(paramReg.var_value)
                # print(var)
                self.newAsm.append(asmn.ASMNode("sub", "$4", "rsp"))
            self.newAsm.append(asmn.ASMNode("mov", paramReg.name, "rbp", rightOffset=rO))

        paramReg.update(var, None)

        return paramReg

    def reg_in_use(self, reg_name):
        """
        Determines if register is in use.
        """
        for reg in self.regs:
            if reg.name == reg_name:
                if reg.var_value == None:
                    return None
                else:
                    return reg



# class RegisterDirectory():

#     used_regs = ["rcx","rbx","rsi","r8","r9","r10","r11","r12","r13","r14","r15"] #these are the total registers used.

#     class registerData():

#         def __init__(self, register_name):

#             self.name = register_name
#             self.isOpen = True
#             self.var_value = None
#             self.offset = None
#             self.is_tmp = False
#             # self.literal_value = None

#         def update(self, var, offset):
#             self.var_value = var
#             # self.literal_value = lit
#             self.isOpen = False
#             self.offset = offset
#             self.is_tmp = var.startswith("tV_")

#         def free(self):
#             self.isOpen = True
#             self.var_value = None
#             self.offset = None
#             self.is_tmp = False
#             # self.literal_value = None

#     def __init__(self, asm, newAsm_list, stack):
#         # self.real_asm = asm
#         self.newAsm = newAsm_list
#         self.asm = asm
#         self.stack = stack
#         self.regs = []
#         self.last_used = []

#         for reg in self.used_regs:
#             self.regs.append(self.registerData(reg))

#     def find_reg(self, name, idx):
#         """
#         Finds register containing the passed in variable name.

#         First, searches local registers.
#         Second, searches on stack.
#         Else, allocates new register

#         Returns:
#             new RegisterData object or None
#         """
#         newReg = self.var_in_reg(name)
#         if newReg == None:
#             newReg = self.var_in_stack(name)
#             if newReg == None:
#                 newReg = self.get_free(name, idx)
#                 if newReg == None:
#                     return None

#         return newReg

#     def var_in_reg(self, var):
#         """
#         Find register containing passed in variable name.

#         Returns either the node or None
#         """
#         for reg in self.regs:
#             if var == reg.var_value:
#                 return reg
#         return None

#     def var_in_stack(self, var):
#         """
#         Find/Create registerData that contains stack pointer
#         with offset corresponding to the passed in variable name.
#         """
#         offset = self.stack.find_offset(var)
#         if offset == None:
#             return None

#         # regData = self.registerData(f"{offset}(rbp)")
#         regData = self.registerData("rbp")
#         regData.update(var, offset)

#         return regData


#     def get_free(self, var, idx):
#         """
#         Finds lastest register that isnt being used else performs register eviction,
#         updates and returns that register.
#         """

#         #Search for free register.
#         for ind,reg in enumerate(self.regs):
#             if self.regs[ind].isOpen == True:

#                 self.regs[ind].update(var, None)
#                 self.regs[ind].isOpen = False
#                 self.last_used.append(self.regs[ind])

#                 return self.regs[ind]
#             elif (
#                 self.regs[ind].is_tmp
#                     and
#                 self.var_in_reg(self.asm[idx].left) != self.regs[ind]
#                     and
#                 self.var_in_reg(self.asm[idx].right) != self.regs[ind]
#                     and
#                 self.regs[ind] not in self.last_used[-2:]
#                 ):
#                 # print([x.name for x in self.last_used[-3:]])
#                 self.regs[ind].update(var, None)
#                 self.regs[ind].isOpen = False
#                 self.last_used.append(self.regs[ind])

#                 return self.regs[ind]

#         # No free registers, evict register and return it
#         tmpReg = self.evict_register(var, idx)
#         self.last_used.append(tmpReg)
#         return tmpReg



#     def update_reg(self, name, var):
#         """
#         Updates the given register using the name, isopen, var_value_value.
#         """
#         for reg in self.regs:
#             if reg.name == name:
#                 reg.update(var, None)
#                 if reg in self.last_used:
#                     self.last_used.remove(reg)
#                 self.last_used.append(reg)

    # def reg_in_use(self, reg_name):
    #     """
    #     Determines if register is in use.
    #     """
    #     for reg in self.regs:
    #         if reg.name == reg_name:
    #             if reg.var_value == None:
    #                 return False
    #             else:
    #                 return True


#     def free_reg(self, name):
#         """
#         Frees the given register searching by the given register name
#         """
#         for reg in self.regs:
#             if reg.name == name:
#                 self.last_used.remove(reg)
#                 reg.free()

#     def evict_register(self, var, index):
#         """
#         Evicts register that is the last used in the code ahead.
#         """
#         order_used = []
#         for line in self.asm[index:]:
#             if line.leftHasVar:

#                 left = self.var_in_reg(line.left)
#                 if left:
#                     # print(f"appending {left.name} to order_used: {line.left}")
#                     order_used.append(left)

#             if line.rightHasVar:

#                 right = self.var_in_reg(line.right)
#                 if right:
#                     # print(f"appending {right.name} to order_used: {line.right}")
#                     order_used.append(right)

#             if [x for x in self.regs if x not in order_used] == [] and order_used != []:
#                 break

#         #gets the registers not used.
#         # left_over = self.regs - order_used
#         left_over = [x for x in self.regs if x not in order_used]
#         # print("new")
#         # # print(left_over[-1].name)
#         # for i in left_over:
#         #     print(i.name)
#         # This means no available register
#         # if left_over == []:

#         # if order_used:
#         #     left_over.append(order_used.pop())

#         # if order_used != []:
#         # result = left_over.pop() if left_over else self.regs[0]

#         # for i in left_over:
#         #     i.free()

#         # stack_offset = self.stack.find_offset(result.var_value)
#         # if stack_offset == None:
#         #     # need to insert into stack and get offset?
#         #     stack_offset = self.stack.insert(result.var_value)
#         #     pass

#         # Instruction to move this register's value onto stack

#         # Insert instruction into the modified ASM list at adjusted index
#         # print(index)
#         # self.newAsm.append(asmn.ASMNode("sub", "$4", "rsp"))
#         # self.newAsm.append(asmn.ASMNode("mov", result.name, "rbp", rightOffset=stack_offset))
#         # print(node)
#         # self.asm.insert(0, node)
#         # self.asm.insert(0, node)

#         # result.update(var, None)
#         # self.update_reg(result.name, )
#         # self.free_reg(result.name)

#         # else:
#         #     print("we here bois")
#         stack_offset = self.stack.insert(var)
#         result = self.registerData(f"{stack_offset}(rbp)")
#         result.update(var,stack_offset)

#         return result







#         # # We have some registers that will not be used again.
#         # else:

#         #     # NOTE: May need to free leftover regs not sure yet.
#         #     result = left_over.pop()
#         #     self.update_reg(result.name, var)
#         #     return result




