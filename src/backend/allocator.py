from copy import copy
import importlib
import os
from inspect import getsourcefile
from importlib.machinery import SourceFileLoader

asmn = SourceFileLoader("ASMNode", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/ASMNode.py").load_module()
stk = SourceFileLoader("stack", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/stack.py").load_module()



class Allocator():
    """
    The class that allocates registers properly for a given list of assembly strings
    """
    def allocateRegisters(asm_list):
        """
        Takes in a list of asm strings using variable names, converts these to use proper register allocation

        Args:
            asm_list: A list of ASMNode objects, where each string in the list is an assembly command that uses variables instead of registers

        Returns:
            A list of strings, where each string is an assembly line with proper register allocation
        """
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

            #In order to accurately allocate registers based on a given situation, we define various cases that have different needs for allocation

            if instr.functionDecl:
                # Clear the stack
                stack.stk.clear()
                stack.push("BpMov", name="rbp")
                [x.free() for x in regDir.regs if x.name not in ["r15", "r14", "r13", "r12", "rbx"]]

                # Sets up the stack with the parameters
                # stack.scope_change()
                [stack.stk.append(x) for x in instr.stack]

                # Sets up the registers with the correct values
                [regDir.update_reg(x, y) for x, y in instr.regDir.items()]
                # [regDir.free_reg(x) for x in ["rbx", "r12", "r13", "r14", "r15"]]
                # [x.free() for x in regDir.regs if x.name not in ["r15", "r14", "r13", "r12", "rbx"]]
                pass
                case = 12


            # Case regIsParam
            elif instr.regIsParam:

                # if not instr.left.startswith("$"):
                    # newReg = regDir.find_reg(instr.left, idx)
                tmp = regDir.locate_var(instr.left)
                if isinstance(tmp, int):
                    # variable is stored on the stack
                    tmp = regDir.reg_in_use(instr.right)
                    if not tmp.is_tmp():
                        regDir.regToStack(tmp)
                    regDir.stackToReg(tmp, instr.left)
                    continue
                elif tmp:
                    # variable is stored in a register
                    instr.left = tmp.name
                    pass
                else:
                    # variable is a constant
                    pass
                

                paramReg = regDir.reg_in_use(instr.right)

                # if register already in use
                if paramReg and not paramReg.is_tmp():
                    regDir.regToStack(paramReg)
                    pass
                case = 11

            # Case 0: Dont touch this instruction (labels, ret, etc..)
            elif instr.dontTouch:

                if instr.command == "pop":
                    stack.pop()
                elif instr.command == "push":
                    if instr.leftNeedsReg:
                        reg = regDir.find_reg(instr.left, idx)
                        stack.push("KnownVar", name=instr.left)
                        instr.left = reg.name
                    elif not instr.left.startswith("$"):
                        stack.push("UnknownVar", name=instr.left)
                        [x.free() for x in regDir.regs if x.name == instr.left]
                elif instr.command == "ret":

                    r15 = stack.find_offset("r15", 0) - 8
                    diff = stack.dist_from_base()

                    # print (stack, stack.peek(), r15, diff)

                    # before pop rbp 
                    newAsm_list.extend([
                        asmn.ASMNode("add", f"${diff + r15}", f"%rsp"),
                        asmn.ASMNode("pop", "r15", None),
                        asmn.ASMNode("pop", "r14", None),
                        asmn.ASMNode("pop", "r13", None),
                        asmn.ASMNode("pop", "r12", None),
                        asmn.ASMNode("pop", "rbx", None),
                    ])
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

                newReg = regDir.find_reg(instr.right, idx)
                instr.right = newReg.name
                # print(newReg.var_value)
                # regDir.update_reg(newReg.name, var="")
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

                # if ogRight == "":
                    # regDir.update_reg(newReg.name, instr.left)
                # print("BOI PUTTING ON 20lbs", newReg.var_value)
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

                newReg = regDir.find_reg(instr.right, idx)
                instr.right = newReg.name
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

                # regDir.update_reg(newReg.name, var=instr.right)

                instr.right = newReg.name
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

                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name

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

                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name
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
                case = 10
            else:
                case = "E"
                pass


            # Ensures that shifting only uses the lower byte of the appropriate register
            # if instr.command in ["sal", "sar"]:
            #     if instr.left.endswith("x"):
            #         instr.left = f"{instr.left[1]}l"
            #     elif instr.left.endswith("i") or instr.left.endswith("p"):
            #         instr.left = f"{instr.left[1:]}l"
            #     elif instr.left.startswith("r"):
            #         instr.left = f"{instr.left}b"

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


class registerData():
    """
    The register class, essentially represents a register in our codebase
    """

    def __init__(self, register_name):
        """
        Initialzies the registerData object

        Args:
            register_name: The name of the register (i.e rbx, rax, etc.)
        """
        self.name = register_name
        self.isOpen = True
        self.var_value = None
        # self.literal_value = None

    def update(self, var):
        """
        Updates the variable that is currently in a register (i.e sets rbx to be holding a variable named i)

        Args:
            var: The variable placed into the register object
        """

        self.var_value = var
        self.isOpen = False

    def free(self):
        """
        Frees a register, essentially clears out it's values and then makes it available to be allocated to
        """
        self.isOpen = True
        self.var_value = None

    def is_tmp(self):
        """
        Determines whether a register contains a temporary variable (a variable that is created in our IR, rather than initially in the inputted c file)

        Returns:
            A boolean, where False means it is not holding a temporary variable, and where True means it is holding a temp variable
        """

        if self.var_value:
            return self.var_value.startswith("tV_") or self.var_value.startswith("$")

        return True

    def __str__(self):
        """
        Defines the string representation of a registerData node

        Returns:
            A string representation of registerData, in the form: | name isOpen var_value offset |
        """

        return f"|{self.name} {self.isOpen} {self.var_value}|"

class RegisterDirectory():
    """
    The directory of registers, holds register objects and can determine what's in use, free, etc.
    """
    used_regs = ["rcx","rbx","rdi","rsi","r8","r9","r10","r11","r12","r13","r14","r15"] #these are the total registers used.

    def __init__(self, asm, newAsm_list, stack):
        """
        Initializes the register directory object, creates registerData objects for the various registers we use and appends them to our list of registers

        Args:
            asm: the initial list of asm that the allocator starts with
            newAsm_list: the list of asm strings
            stack: An object of the stack class

        """

        # self.real_asm = asm
        self.newAsm = newAsm_list
        self.asm = asm
        self.stack = stack
        self.regs = []
        self.last_used = []

        #create register objects for each register we will be using
        for reg in self.used_regs:
            self.regs.append(registerData(reg))

    def find_reg(self, name, idx, dont_use=[]):
        """
        Finds register containing the passed in variable name.

        First, searches local registers.
        Second, searches on stack.
        Else, allocates new register

        Args:
            name: the name of the variable being looked for
            idx: the index of the appropraite instruction in the asm list

        Returns:
            new RegisterData object or None
        """

        newReg = self.var_in_reg(name)
        if newReg == None:
            newReg = self.get_free(name, idx, dont_use)
            if newReg == None:
                newReg = self.evict_register(name, idx, dont_use)
            else:
                newreg = self.var_in_stack(name, newReg)

        self.last_used.append(newReg)
        newReg.update(name)

        return newReg

    def var_in_reg(self, var):
        """
        Find register containing passed in variable name.

        Args: 
            var: the variable name that is being looked for in the registers

        Returns:
            either the register that stores this variable, or None
        """
        for reg in self.regs:
            if var == reg.var_value:
                return reg
        return None

    def var_in_stack(self, var, reg):
        """
        Find/Create registerData that contains stack pointer
        with offset corresponding to the passed in variable name.

        Args:
            var: the variable name being looked for
            reg: the register that is storing that variable

        Returns:
            The register that is being updated

        """
        offset = self.stack.find_offset(var)
        if offset == None:
            # reg.update(var)
            return reg

        return self.stackToReg(reg, var)


    def get_free(self, var, idx, dont_use):
        """
        Finds lastest register that isnt being used else performs register eviction,
        updates and returns that register.

        Args:
            var: The variable name that is being freed
            idx: The index of the appropriate instruction in the asm list

        """

        #Search for free register.
        for ind,reg in enumerate(self.regs):
            if self.regs[ind].isOpen == True:

                self.regs[ind].isOpen = False
                return self.regs[ind]

        for ind,reg in enumerate(self.regs):
            if (
                self.regs[ind].is_tmp()
                    and
                self.var_in_reg(self.asm[idx].left) != self.regs[ind]
                    and
                self.regs[ind] not in self.last_used[-2:]
                    and
                self.regs[ind].name not in dont_use
                ):
                self.regs[ind].isOpen = False

                return self.regs[ind]

        return None

    def locate_var(self, var):
        reg = self.var_in_reg(var)
        if reg == None:
            reg = self.stack.find_offset(var)

        return reg

    def update_reg(self, name, var):
        """
        Updates the given register using the name, isopen, var_value_value.

        Args:
            name: The name of the register that is being updated
            var: The name of the variable that is being used to update
        """
        for reg in self.regs:
            if reg.name == name:
                reg.update(var)
                # if reg in self.last_used:
                #     self.last_used.remove(reg)
                break


    def free_reg(self, name):
        """
        Frees the given register searching by the given register name

        Args:
            name: The name of the register being freed (i.e rbx, rax, etc.)
        """
        for reg in self.regs:
            if reg.name == name:
                # self.last_used.remove(reg)
                reg.free()
                break

    def evict_register(self, var, index, dont_use):
        print("in evict")
        """
        Evicts register that is the last used in the code ahead.

        Args:
            var: The name of the variable that is being stored
            index: The index of the item in the asm list

        Returns:
            The register that is being modified
        """
        #determine the order registers are used in
        order_used = copy(self.last_used[-2:])
        for line in self.asm[index:]:
            if line.leftHasVar:

                left = self.var_in_reg(line.left)
                if left and left not in order_used:
                    order_used.append(left)

            if line.rightHasVar:

                right = self.var_in_reg(line.right)
                if right and right not in order_used:
                    order_used.append(right)

            if [x for x in self.regs if x not in order_used] == [] and order_used != []:
                break

        #gets the registers not used.
        left_over = [x for x in self.regs if x not in order_used]
        
        result = None
        try:
            result = left_over.pop()
        except IndexError:
            i = 0
            while self.regs[i] in self.last_used[-2:] or self.regs[i].name in dont_use:
                i += 1
            result = self.regs[i]
        # result = left_over.pop() if left_over else self.regs[0]
        

        if result.is_tmp() and (var.startswith("$") or var.startswith("tV_")):
            # result.update(var)
            return result

        if not result.is_tmp():
            self.regToStack(result)
        
        if self.stack.find_offset(var):
            return self.stackToReg(result, var)
        else:
            return result


    def regToStack(self, reg):
        """
        Moves a register to the stack

        Args:
            reg: The registerData object that is being moved to the stack
        """
        #if the register is not containing a temporary variable
        # if not reg.is_tmp():
        rO = self.stack.find_offset(reg.var_value)
        if not rO:
            rO = self.stack.push("KnownVar", name=reg.var_value)
            self.newAsm.append(asmn.ASMNode("push", reg.name, None))
        else:
            self.newAsm.append(asmn.ASMNode("mov", reg.name, "rbp", rightOffset=rO))
        reg.free()


    def stackToReg(self, reg, var):
        """
        Moves an object on the stack to a register

        Args:
            reg: The register that is being moved to
            var: The variable that is being looked for

        Returns:
            The reigster after the variable has been moved to it from the stack
        """

        offset = self.stack.find_offset(var)
        self.newAsm.append(asmn.ASMNode("mov", "rbp", reg.name, leftOffset=offset))
        # reg.update(var)
        return reg

    def reg_in_use(self, reg_name):
        """
        Determines if register is in use.
        
        Args:
            reg_name: The name of the register that is being used

        Returns:
            Either None or the register that is being updated to
        """
        for reg in self.regs:
            if reg.name == reg_name:
                if reg.var_value == None:
                    return None
                else:
                    return reg
