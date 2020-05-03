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

        # Set our virtual stack and directory or registers
        stack = stk.Stack()
        regDir = RegisterDirectory(asm_list, newAsm_list, stack)

        idx = -1

        for instr in asm_list:
            idx += 1

            #In order to accurately allocate registers based on a given situation, we define various cases that have different needs for allocation

            # Case: function declaration
            if instr.functionDecl:
                # Clear the stack
                stack.stk.clear()
                stack.push("BpMov", name="rbp")
                [x.free() for x in regDir.regs if x.name not in ["r15", "r14", "r13", "r12", "rbx"]]

                # Sets up the stack with the parameters for the instruction
                [stack.stk.append(x) for x in instr.stack]

                # Sets up the registers with the correct values
                [regDir.update_reg(x, y) for x, y in instr.regDir.items()]


            # Case: handling parameter
            elif instr.regIsParam:

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

                # if register already in use and not a tmp variable, need to move it to stack to store value
                paramReg = regDir.reg_in_use(instr.right)
                if paramReg and not paramReg.is_tmp():
                    regDir.regToStack(paramReg)
                    pass

            # Case: Dont touch this instruction (labels, ret, etc..)
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
                pass

            # Case: Operation with two registers.
            elif instr.leftNeedsReg and instr.rightNeedsReg:

                newReg = regDir.find_reg(instr.left, idx)
                instr.left = newReg.name

                newReg = regDir.find_reg(instr.right, idx)
                instr.right = newReg.name
                pass

            # Case: Moving a literal to a new register
            elif instr.leftLiteral and instr.rightNeedsReg:
                if(instr.right):
                    newReg = regDir.find_reg(instr.right, idx)
                else:
                    newReg = regDir.find_reg(instr.left, idx)

                ogRight = instr.right
                instr.right = newReg.name
                pass

            # Case: After an operation like add/sub this case is for moving the answer to a tmp variable
            elif instr.leftNeedsReg and instr.rightHasVar:

                # last used register becomes our source register
                newReg = regDir.last_used[-1]
                instr.left = newReg.name

                newReg = regDir.find_reg(instr.right, idx)
                instr.right = newReg.name
                pass

            # Case: Moving a literal to variable.
            elif instr.leftLiteral and instr.rightHasVar:

                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name
                pass

            # Case: variable to register
            elif instr.leftHasVar and instr.rightNeedsReg:

                newReg = regDir.find_reg(instr.left,idx)
                instr.left = newReg.name

                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name

                pass

            # Case: Moving values from variable to variable.
            elif instr.leftHasVar and instr.rightHasVar:

                newReg = regDir.find_reg(instr.left,idx)
                instr.left = newReg.name

                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name
                pass

            # Case: rax instruction
            elif instr.right == "rax" and instr.leftLiteral:
                pass


            # Case: edge cases, with rax or single operand instructions
            elif instr.right == "" or instr.right == "rax":

                if instr.left != "rbp":
                    newReg = regDir.find_reg(instr.left, idx)
                    instr.left = newReg.name

            # Case: right side needs register but left side is hard coded
            elif instr.rightHasVar:
                newReg = regDir.find_reg(instr.right,idx)
                instr.right = newReg.name

            else:
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
            newAsm_list.append(instr)

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
                break


    def free_reg(self, name):
        """
        Frees the given register searching by the given register name

        Args:
            name: The name of the register being freed (i.e rbx, rax, etc.)
        """
        for reg in self.regs:
            if reg.name == name:
                reg.free()
                break

    def evict_register(self, var, index, dont_use):
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

        if result.is_tmp() and (var.startswith("$") or var.startswith("tV_")):
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
