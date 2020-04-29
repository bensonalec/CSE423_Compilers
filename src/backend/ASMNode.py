#this file will solve all our problems. indeed.

x86_regs = ["rax", "rbp", "rsp", "rcx","rdx" ,"rbx" ,"rsi" ,"rdi" ,"r8", "r9" ,"r10" ,"r11" ,"r12", "r13","r14", "r15", "al", "bpl", "spl", "cl", "dl" ,"bl" ,"sil" ,"dil" ,"r8b", "r9b" ,"r10b" ,"r11b" ,"r12b", "r13b", "r14b", "r15b"]

class ASMNode():

    def __init__(self, command, left, right, **kwarg):

        self.command = command
        self.left = left if left else ""
        self.right = right if right else ""
        self.aux = kwarg["aux"] if "aux" in kwarg else None

        # self.offset = kwarg["offset"] if "offset" in kwarg else None
        self.leftOffset = kwarg["leftOffset"] if "leftOffset" in kwarg else None
        self.rightOffset = kwarg["rightOffset"] if "rightOffset" in kwarg else None

        self.leftNeedsReg = kwarg["leftNeedsReg"] if "leftNeedsReg" in kwarg else False
        self.rightNeedsReg = kwarg["rightNeedsReg"] if "rightNeedsReg" in kwarg else False
        self.dontTouch = "dontTouch" in kwarg

        self.regIsParam = "regIsParam" in kwarg
        self.regDir = kwarg["regDir"] if "regDir" in kwarg else {}
        self.stack = kwarg["stack"] if "stack" in kwarg else []
        self.functionDecl = "functionDecl" in kwarg

        self.noParams = "noParams" in kwarg

        self.leftLiteral = True if self.left and self.left.startswith("$") else False
        self.rightLiteral = True if self.right and self.right.startswith("$") else False

        # self.leftNeedsReg = True if self.left == None else False
        # self.rightNeedsReg = True if self.right == None else False

        self.leftHasVar = True if self.left and self.left not in x86_regs else False
        self.rightHasVar = True if self.right and self.right not in x86_regs else False

        # self.tmpVar = True if self.command == "mov" and self.right.startswith("tV_") else False



    def __str__(self):
        if self.aux:
            return f"{self.command} \
{self.aux}, \
{f'{self.leftOffset}' + '(' if self.leftOffset else ''}\
{'%' if self.left in x86_regs else ''}\
{self.left}\
{')' if self.leftOffset else ''}, \
{f'{self.rightOffset}' + '(' if self.rightOffset else ''}\
{'%' if self.right in x86_regs else ''}\
{self.right}\
{')' if self.rightOffset else ''}"
        elif self.right:
            return f"{self.command} \
{f'{self.leftOffset}' + '(' if self.leftOffset else ''}\
{'%' if self.left in x86_regs else ''}\
{self.left}{')' if self.leftOffset else ''}, \
{f'{self.rightOffset}' + '(' if self.rightOffset else ''}\
{'%' if self.right in x86_regs else ''}\
{self.right}\
{')' if self.rightOffset else ''}"
        elif self.left:
            return f"{self.command} \
{f'{self.leftOffset}' + '(' if self.leftOffset else ''}\
{'%' if self.left in x86_regs else ''}\
{self.left}\
{')' if self.leftOffset else ''}"
        else:
            return f"{self.command}"
