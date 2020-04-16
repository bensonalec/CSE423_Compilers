from copy import copy

class Allocator():

    def allocateRegisters(asm_list):

        # Set up directory of registers
        # We give it assembly list because we may need it to "look ahead" to get next-available-register
        regDir = RegisterDirectory(asm_list)

        for idx, instr in enumerate(asm_list):
            # print(asm_list[idx].leftHasVar)
            # print(asm_list[idx].leftNeedsReg)
            # Case 0: Just the op...like a label?
            if asm_list[idx].noParams:
                print("Case 0")
                pass

            # """
            # Case 1: Moving a literal to a new register

            # left    ->  $1
            # right   ->  tmp
            # """
            elif asm_list[idx].leftLiteral and asm_list[idx].rightNeedsReg:
                newReg = regDir.get_free(var=None, literal=asm_list[idx].left)
                asm_list[idx].right = newReg.name
                print("CASE 1")
                # print(newReg.literal_value)
                pass

            # """
            # Case 2: Moving a literal to variable. 
            #         Need to find register corresponding to that variable and update it.

            # left    ->  $1
            # right   ->  _1
            # """
            elif asm_list[idx].leftLiteral and asm_list[idx].rightHasVar:                
                newReg = regDir.var_in_reg(asm_list[idx].right)
                asm_list[idx].right = newReg.name
                regDir.updateRegister(newReg.name, var=None, literal=asm_list[idx].left)
                print("CASE 2")
                pass
            
            # """
            # Case 3: Moving a variable to new register.
            #         Need to find new register, set values. And free old register holding the variable.

            # left    ->  _1
            # right   ->  tmp
            # """            
            elif asm_list[idx].leftHasVar and asm_list[idx].rightNeedsReg:
                newReg = regDir.get_free(var=asm_list[idx].left, literal=None)
                asm_list[idx].right = newReg.name

                varReg = regDir.var_in_reg(asm_list[idx].left)
                asm_list[idx].left = varReg.name
                regDir.free_reg(varReg.name)
                print("CASE 3")
                pass

            # """
            # Case 4: Find last 2 used registers, free left side, update right side.

            # left    ->  tmp
            # right   ->  tmp
            # """
            elif asm_list[idx].leftNeedsReg and asm_list[idx].rightNeedsReg:
                print(asm_list[idx])

                #NOTE: need to seach for var-names instead of popping last two nodes, if they are variables...

                leftReg = regDir.last_used[-1]
                rightReg = regDir.last_used[-2]
                asm_list[idx].left = leftReg.name
                asm_list[idx].right = rightReg.name
                
                regDir.free_reg(leftReg.name)
                # print(leftReg.var_value, "  ", leftReg.literal_value, "  ", leftReg.name)
                regDir.update_reg(rightReg.name, var=leftReg.var_value, literal=leftReg.literal_value)


                print("CASE 4")
                pass

            # """
            # Case 5: Not sure if this will happen??

            # left    ->  tmp
            # right   ->  _1
            # """
            elif asm_list[idx].leftNeedsReg and asm_list[idx].rightHasVar:
                newReg = regDir.last_used[-1]
                asm_list[idx].left = newReg.name
                
                newReg = regDir.get_free(var=asm_list[idx].right, literal=None)
                asm_list[idx].right = newReg.name

                regDir.free_reg(asm_list[idx].left)

                print("CASE 5")
                pass

            # """
            # Case 6: Not sure if this will happen??

            # left    ->  tmp
            # right   ->  None
            # """
            elif asm_list[idx].leftNeedsReg and asm_list[idx].rightNone:
                print("CASE 6")
                pass

            # """
            # Case 7:

            # left    ->  _1
            # right   ->  a
            # """
            
            elif asm_list[idx].leftHasVar and asm_list[idx].rightHasVar:

                newReg = regDir.var_in_reg(asm_list[idx].left)

                if newReg == None:
                    newReg = regDir.get_free(var=asm_list[idx].left, literal=None)

                if asm_list[idx].left == asm_list[idx].right:
                    asm_list[idx].left = newReg.name
                    asm_list[idx].right = newReg.name

                else:
                    asm_list[idx].left = newReg.name

                    if asm_list[idx].right != "rax":
                        newReg = regDir.get_free(var=asm_list[idx].right, literal=None)
                        asm_list[idx].right = newReg.name

                    regDir.free_reg(asm_list[idx].left)

                print("CASE 7")
                pass
            
            # Case 8: left side needs variable
            # idiv rsi
            elif asm_list[idx].rightNone:
                #assign a a reg for the left side
                if asm_list[idx].left != "rbp":
                    newReg = regDir.last_used[-1]
                    asm_list[idx].left = newReg.name
                    # regDir.free_reg(asm_list[idx].left)

                print("CASE 8")
            
            
            
            # Case 9: left side needs register but right side is hard-coded 
            #       (ie. %rax or something like that)
            
            elif asm_list[idx].leftHasVar:
                #assign a a reg for the left side

                
                if asm_list[idx].left == None:
                    # left is None
                    newReg = regDir.last_used[-2]
                else:
                    # left is a variable
                    newReg = regDir.var_in_reg(asm_list[idx].left)
                
                asm_list[idx].left = newReg.name

                # regDir.free_reg(asm_list[idx].left)
                print("CASE 9")
                pass

            # Case 10: rigt side needs register but left side is hard coded
            
            elif asm_list[idx].rightHasVar:

                if asm_list[idx].right == None:                    
                    newReg = regDir.var_in_reg(asm_list[idx].right)
                else:
                    newReg = regDir.last_used[-2]
                    regDir.update_reg(newReg.name, var=asm_list[idx].right, literal=None)
                
                asm_list[idx].right = newReg.name

                print("Case 10")

            else:
                print("ELSE")
                pass

            # We need to update the assembly list in the register directory.
            # The directory used the assembly list to "look-ahead" in some cases,
            # and needs an updated assembly list.
            regDir.asm.pop(0)
            
            print(asm_list[idx])

        return asm_list
        
 



class RegisterDirectory():

    used_regs = ["rcx","rbx","rsi","r8","r9","r10","r11","r12","r13","r14","r15"] #these are the total registers used.

    class registerData():

        def __init__(self, register_name):
            
            self.name = register_name
            self.isOpen = True            
            self.var_value = None
            self.literal_value = None
            
        def update(self, var, lit):
            self.var_value = var
            self.literal_value = lit

        def free(self):
            self.isOpen = True
            self.var_value = None
            self.literal_value = None
            

    def __init__(self, asm):
        self.asm = copy(asm)
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

    def get_free(self, var, literal):
        """
        Finds lastest register that isnt being used else performs register eviction, 
        updates and returns that register.
        """
        
        #Search for free register.
        for ind,reg in enumerate(self.regs):
            if self.regs[ind].isOpen == True:
                
                self.regs[ind].update(var, literal)
                self.regs[ind].isOpen = False
                self.last_used.append(self.regs[ind])
                
                return self.regs[ind]

        # No free registers, evict register and return it
        return self.evict_register(var, literal)
    
                

    def update_reg(self, name, var, literal):
        """
        Updates the given register using the name, isopen, var_value, literal_value.
        """
        for reg in self.regs:
            if reg.name == name:
                reg.update(var, literal)
                self.last_used.remove(reg)
                self.last_used.append(reg)
                

    def free_reg(self, name):
        """
        Frees the given register searching by the given register name
        """
        for reg in self.regs:
            if reg.name == name:
                self.last_used.remove(reg)
                reg.free()
                

    def evict_register(self, var, literal):
        """
        Evicts register that is the last used in the code ahead. 
        """

        order_used = []
        for line in self.asm:
            if line.leftHasVar and line.rigthHasVar:

                left = self.var_in_reg(line.left)
                right = self.var_in_reg(line.right)

                if left:
                    order_used.append(left)
                if right:
                    order_used.append(right)
                    
            elif line.leftHasVar:
                
                left = self.var_in_reg(line.left)
                if left:
                    order_used.append(left)

            elif line.rigthHasVar:

                right = self.var_in_reg(line.right)
                if right:
                    order_used.append(right)

            else:
                pass

        #gets the registers not used.
        left_over = self.regs - order_used 

        # This means no available register
        if left_over == []:

            #pop last used element, should be register that hasn't been used for longest time.
            result = order_used.pop()
            self.update_reg(result.name, False, var, literal)
            return result

        # We have some registers that will not be used again.
        else:

            # NOTE: May need to free leftover regs not sure yet.
            result = left_over.pop()
            self.update_reg(result.name, False, var, literal)
            return result

    

    