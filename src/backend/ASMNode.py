x64_regs = ["rax", "rbp", "rsp", "rcx","rdx" ,"rbx" ,"rsi" ,"rdi" ,"r8", "r9" ,"r10" ,"r11" ,"r12", "r13","r14", "r15", "al", "bpl", "spl", "cl", "dl" ,"bl" ,"sil" ,"dil" ,"r8b", "r9b" ,"r10b" ,"r11b" ,"r12b", "r13b", "r14b", "r15b"]

class ASMNode():
    """
    The class for a node of assembly, essentially each node is a line in assembly
    """
    def __init__(self, command, left, right, **kwarg):
        """
        Initializes the ASMNode object

        Args:
            command: The operation (mov, add, etc.)
            left: The left side of the operation (mov x,y), left is x
            right: The right side of the operation (mov x,y) right is y
            kwargs: A dictionary of values that give various metadata about the command (will it need a register, is it a constant, etc.)

        """
        self.command = command
        self.left = left if left else ""
        self.right = right if right else ""
        self.aux = kwarg["aux"] if "aux" in kwarg else None

        #determine the left and right offset
        self.leftOffset = kwarg["leftOffset"] if "leftOffset" in kwarg else None
        self.rightOffset = kwarg["rightOffset"] if "rightOffset" in kwarg else None

        #determine if the left operand needs a register, or if the right operand needs a register
        self.leftNeedsReg = kwarg["leftNeedsReg"] if "leftNeedsReg" in kwarg else False
        self.rightNeedsReg = kwarg["rightNeedsReg"] if "rightNeedsReg" in kwarg else False

        #assembly node is fully constructed and shouldnt be modified
        self.dontTouch = "dontTouch" in kwarg

        #determine if the register is a paramater
        self.regIsParam = "regIsParam" in kwarg

        #assembly nodes like 'function declaration' store a regDir and stack for passed in parameters
        self.regDir = kwarg["regDir"] if "regDir" in kwarg else {}
        self.stack = kwarg["stack"] if "stack" in kwarg else []

        #determine if the register is in a function declaration
        self.functionDecl = "functionDecl" in kwarg

        #determines if there are no paramters
        self.noParams = "noParams" in kwarg

        #determine if the left and right operands are literals
        self.leftLiteral = True if self.left and self.left.startswith("$") else False
        self.rightLiteral = True if self.right and self.right.startswith("$") else False

        #determine if the left has a variable
        self.leftHasVar = True if self.left and self.left not in x64_regs else False
        #determine if the right has a variable
        self.rightHasVar = True if self.right and self.right not in x64_regs else False

        self.boilerPlate = kwarg["boilerPlate"] if "boilerPlate" in kwarg else None

    def __str__(self):
        """
        Returns the string representation of an ASMNode

        Returns:
            The string representation of the given node
        """
        #determine the proper string representation of the assembly line
        if self.aux:
            return f"""{self.command} \
{self.aux},\
{f'{self.leftOffset}' + '(' if self.leftOffset else ''}\
{'%' if self.left in x64_regs else ''}\
{self.left}\
{')' if self.leftOffset else ''}, \
{f'{self.rightOffset}' + '(' if self.rightOffset else ''}\
{'%' if self.right in x64_regs else ''}\
{self.right}\
{')' if self.rightOffset else ''}"""
        elif self.right:
            return f"""{self.command} \
{f'{self.leftOffset}' + '(' if self.leftOffset else ''}\
{'%' if self.left in x64_regs else ''}\
{self.left}{')' if self.leftOffset else ''}, \
{f'{self.rightOffset}' + '(' if self.rightOffset else ''}\
{'%' if self.right in x64_regs else ''}\
{self.right}\
{')' if self.rightOffset else ''}"""
        elif self.left:
            return f"""{self.command} \
{f'{self.leftOffset}' + '(' if self.leftOffset else ''}\
{'%' if self.left in x64_regs else ''}\
{self.left}\
{')' if self.leftOffset else ''}"""
        elif self.boilerPlate:
            return f"""{self.boilerPlate}"""
        else:
            return f"{self.command}"
