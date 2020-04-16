#this file will solve all our problems. indeed.

x86_regs = ["rax", "rbp", "rsp", "rcx","rdx" ,"rbx" ,"rsi" ,"rdi" ,"r8", "r9" ,"r10" ,"r11" ,"r12","r13","r14","r15"]

class ASMNode():

    def __init__(self, command, left, right, **kwarg):
        
        self.command = command
        self.left = left
        self.right = right

        self.offset = kwarg["offset"] if "offset" in kwarg else None
        self.leftNeedsReg = kwarg["leftNeedsReg"] if "leftNeedsReg" in kwarg else False
        self.rightNeedsReg = kwarg["rightNeedsReg"] if "rightNeedsReg" in kwarg else False

        self.noParams = "noParams" in kwarg

        self.leftLiteral = True if self.left and self.left.startswith("$") else False
        self.rightLiteral = True if self.right and self.right.startswith("$") else False

        # self.leftNeedsReg = True if self.left == None else False
        # self.rightNeedsReg = True if self.right == None else False
            
        self.leftHasVar = True if self.left and not self.leftNeedsReg and self.left not in x86_regs and not self.leftLiteral else False
        self.rightHasVar = True if self.right and not self.rightNeedsReg and self.right not in x86_regs and not self.rightLiteral else False

        self.leftNone = True if self.left == None else False
        self.rightNone = True if self.right == None else False

        

    def __str__(self):
        if self.right:
            return f"{self.command} {self.left}, {self.right}"
        elif self.left:
            return f"{self.command} {self.left}"
        else:
            return f"{self.command}"
