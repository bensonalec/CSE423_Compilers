"""
This module abstracts the necessary lines for the linear IR to allow for easier optimization methods like constant propagation, constant folding, unused references ect.
"""
import importlib
import os
from inspect import getsourcefile
from importlib.machinery import SourceFileLoader

ast = SourceFileLoader("AST_builder", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../frontend/AST_builder.py").load_module()
asmn = SourceFileLoader("ASMNode", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../backend/ASMNode.py").load_module()
stk = SourceFileLoader("stack", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../backend/stack.py").load_module()

global tmpVarIndex
tmpVarIndex = 0

class IRLine():
    """
    A class that contains all the intermediate representations for a given AST node. Will produce a linear representation when converted to a string
    """
    def __init__(self, node, tvs = [], success = None, failure = None, labelList = [], prefix = ""):
        """
        Args:
            node: The AST node corresponding to the collection of lines
            tvs: The current tempoary variable storage
            success: The success label
            failure: The failure label
            labelList: The list of used label names
            prefix: The output prefix
        """

        self.astNode = node
        self.treeList = []

        self.tvs = tvs
        self.labelList = labelList
        self.prefix = prefix

        self.log_ops = ['||', '&&']
        self.comp_ops = ["<=", "<", ">=", ">", "==", "!="]
        self.arth_ops = ["+", "-", "*", "/", "%", "<<", ">>", "|", "&", "^", "!", "~"]
        self.spec_ops = ["++", "--"]
        self.ass_ops = ["=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "|=", "&=", "^="]
        self.id_ops = ["var", "call"]

        # Based on the node construct the needed intermediate trees in order
        if node == None:
            # There was no AST node passed in. This is the case when there
            # are no complex IR instructions that need to be broken down.
            # IRNode will be added manually to self.treeList.
            pass

        elif node.name in self.log_ops:
            self.boolean_breakdown(self.astNode, success, failure)
        else:
            self.expression_breakdown(self.astNode, success, failure)


    def retrieve(self):
        """
        Retrieves the updated tempoary variable storage and list of unavailable label names for the future.

        Returns:
            tvs: The current tempoary variable storage
            labelList: The list of used label names
        """
        return self.tvs, self.labelList

    def expression_breakdown(self, root, success, failure):
        """
        Breaks down smaller expressions in order to evaluate them

        Args:
            root: The root AST node
            success: The success label
            failure: The failure label
        """
        if success not in self.labelList and success != None:
            self.labelList.append(success)
        if failure not in self.labelList and failure != None:
            self.labelList.append(failure)

        ns = root.list_POT()
        global tmpVarIndex
        ns = [x for x in ns if x.name in self.arth_ops or x.name in self.spec_ops or x.name in self.ass_ops or x.name in self.id_ops or x.name in self.comp_ops]
        for node in ns:
            if node.name in self.comp_ops:
                self.treeList.append(
                    IRIf(
                        node,
                        success,
                        failure,
                        [self.tvs.pop() for x in node.children if len(x.children) != 0]
                    )
                )

            elif node.name in self.arth_ops:
                tmpVarIndex += 1
                self.treeList.append(
                    IRArth(
                        node,
                        [self.tvs.pop() for x in node.children if len(x.children) != 0],
                        f"tV_{tmpVarIndex}"
                    )
                )

                self.tvs.append(f"tV_{tmpVarIndex}")

            elif node.name in self.spec_ops:
                var = self.tvs.pop()

                tmpVarIndex += 1

                # Create a temporay AST to deal with storing of the current value of the variable
                # tmpNode = ast.ASTNode("=", None)
                # tmpNode.children.append(ast.ASTNode(f"_{tmpVarIndex}", tmpNode))
                # tmpNode.children.append(ast.ASTNode(var, tmpNode))

                self.treeList.append(
                    IRAssignment(
                        f"tV_{tmpVarIndex}",
                        var
                    )
                )
                if [node.children.index(x) for x in node.children if x.name == "NULL"][0] == 1:
                    self.treeList.append(
                        IRSpecial(
                            node,
                            var
                        )
                    )
                else:
                    self.treeList.insert(len(self.treeList) - 2,
                        IRSpecial(
                            node,
                            var
                        )
                    )

                self.tvs.append(f"tV_{tmpVarIndex}")

            elif node.name in self.ass_ops:
                if self.ass_ops.index(node.name) == 0:
                    lhs = None
                    rhs = None
                    # Case 1: Assignment is constant. ie. int i = 0
                    if len(node.children[1].children) == 0:
                        lhs = self.tvs.pop()
                        rhs = f"{node.children[1].name}"
                    # Case 2: Assignment is complex
                    else:
                        lhs = f"rV_{node.children[0].children[len(node.children[0].children)-1].name}"
                        rhs = self.tvs.pop()

                    self.treeList.append(
                            IRAssignment(
                                lhs,
                                rhs
                            )
                        )
                else:
                    # create a temporary parent node
                    p = ast.ASTNode("=", None)

                    # append the variable who is assigned a value as its first child
                    p.children.append(node.children[0])

                    # create a right subtree with the correct operation
                    r = ast.ASTNode(node.name[:-1], p)
                    p.children.append(r)

                    rc = None
                    lc = None

                    # assign the variable as the left operand of the new expression
                    if len(node.children[1].children) > 0:
                        rc = ast.ASTNode(self.tvs.pop(), r)
                    else:
                        rc = node.children[1]

                    # assign the variable as the left operand of the new expression
                    if len(node.children[0].children) > 0:
                        lc = ast.ASTNode(self.tvs.pop(), r)
                    else:
                        lc = node.children[0]

                    # assign the remaining operations as the right operand of the new expression

                    r.children.append(lc)
                    r.children.append(rc)

                    self.expression_breakdown(p, success, failure)

            elif node.name in self.id_ops:
                if node.name == "var":
                    self.tvs.append(f"rV_{node.children[len(node.children)-1].name}")
                elif node.name == "call":
                    # list of indices that correspond to the complex parameters of the function call
                    complexP = [node.children[0].children.index(x) for x in node.children[0].children if len(x.children) > 0]
                    simpleP = [x for x in range(len(node.children[0].children)) if x not in complexP]

                    params = [self.tvs.pop() for x in range(len(node.children[0].children)) if x in complexP]

                    tmpVarIndex += 1
                    self.treeList.append(
                        IRFunctionAssign(
                            node,
                            [params.pop() if x in complexP else node.children[0].children[x].name for x in range(len(node.children[0].children))],
                            f"tV_{tmpVarIndex}"
                        )
                    )

                    self.tvs.append(self.treeList[-1].lhs)

    def boolean_breakdown(self, root, success, failure):
        """
        Breaks down larger boolean expressions in order to evaluate them

        Args:
            root: The root AST node
            success: The success label
            failure: The failure label
        """
        if success not in self.labelList and success != None:
            self.labelList.append(success)
        if failure not in self.labelList and failure != None:
            self.labelList.append(failure)

        index = self.log_ops.index(root.name)
        if index == 0:
            # OR
            tmp_label = max(self.labelList)
            self.labelList.append(tmp_label+1)
            tmpNode = root.children[0]
            if tmpNode.name not in self.comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[0])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))

            if tmpNode.name in self.log_ops:
                self.boolean_breakdown(tmpNode, success, tmp_label)
            else:
                self.expression_breakdown(tmpNode, success, tmp_label)

            self.treeList.append(IRJump(f"<D.{tmp_label}>"))

            tmpNode = root.children[1]
            if tmpNode.name not in self.comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[1])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))

            if tmpNode.name in self.log_ops:
                self.boolean_breakdown(tmpNode, success, failure)
            else:
                self.expression_breakdown(tmpNode, success, failure)

        elif index == 1:
            # AND
            tmp_label = max(self.labelList)
            self.labelList.append(tmp_label+1)
            tmpNode = root.children[0]
            if tmpNode.name not in self.comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[0])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))

            if tmpNode.name in self.log_ops:
                self.boolean_breakdown(tmpNode, tmp_label, failure)
            else:
                self.expression_breakdown(tmpNode, tmp_label, failure)

            self.treeList.append(IRJump(f"<D.{tmp_label}>"))

            tmpNode = root.children[1]
            if tmpNode.name not in self.comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[1])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))

            if tmpNode.name in self.log_ops:
                self.boolean_breakdown(tmpNode, success, failure)
            else:
                self.expression_breakdown(tmpNode, success, failure)

    def __str__(self):
        return "\n".join([str(x) for x in self.treeList])

    @staticmethod
    def singleEntry(irNode, labelDigit=None, prefix=""):
        """
        Creates a new instance of an IRLine but with only one entry.

        Args:
            irNode: The given 'IRNode' entry for this new IRLine.
            labelList: The list of used label names.
            prefix: The output prefix.
        """
        entry = IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
        entry.treeList.append(irNode)
        return entry

class IRNode():
    """
    Abstract intermediate representation node. Base class for all other IR representations other than IRLines.
    """
    def __init__(self):
        pass

    def __str__(self):
        pass

    def asm(self):
        pass


class IRJump(IRNode):
    """
    Intermediate representation node for a jump label.
    """
    def __init__(self, name):
        """
        Args:
            name: Name of the jump label
        """
        self.name = name

    def __str__(self):
        return f"{self.name}:"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRJump
        """
        return [asmn.ASMNode(f"{self.name.replace('<','').replace('>','')}:",None,None,dontTouch=True)]


class IRGoTo(IRNode):
    """
    Intermediate representation node for a goto label.
    """
    def __init__(self, name):
        """
        Args:
            name: Name of the label which is jumped to
        """
        self.name = name

    def __str__(self):
        return f"goto {self.name};"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRGoTo
        """

        return [asmn.ASMNode("jmp", self.name.replace("<","").replace(">",""), None, dontTouch=True)]

class IRIf(IRNode):
    """
    Intermediate representation node for an if statement. If statements are constructed to represent actual If Statements, While Loops, and For Loops in C.
    """
    def __init__(self, node, success, failure, ops):
        """
        Args:
            node: `AST-node` for the given
            success: Success label digit
            failure: Failure label digit
            ops: The potential complex operands for the left/right hand side of the comparison
        """
        if(node == None and success == None and failure == None and ops == None):
            pass
        else:
            self.node = node
            self.success = success
            self.failure = failure
            self.children = []

            self.comp = node.name
            self.lhs = None
            self.rhs = None

            # Case 1: ops is empty
            if ops == [] and len(node.children) > 1:
                self.lhs = node.children[0].name
                self.rhs = node.children[1].name

            # Case 2: two elem in ops
            elif len(ops) == 2:
                self.lhs = ops[1]
                self.rhs = ops[0]

            else:
                pos = [node.children.index(x) for x in node.children if len(x.children) != 0 and len(node.children) > 1]

                # Case 3: one elem in ops but its the left element in the operation
                if pos == [0]:
                    self.lhs = ops[0]
                    self.rhs = node.children[1].name

                # Case 4: one elem in ops but its the right element in the operation
                elif pos == [1]:
                    self.lhs = node.children[0].name
                    self.rhs = ops[0]

    def __str__(self):
        return f"if ({self.lhs} {self.comp} {self.rhs}) goto <D.{self.success}>; else goto <D.{self.failure}>;"
    def fileInit(self,lhs,rhs,compOp,succ,fail):
        """
        Args:
            lhs: left side of the comparison
            rhs: right side of the comparison
            compOp: comparison operator
            succ: success label
            fail: failure label
        """
        self.lhs = lhs
        self.rhs = rhs
        self.comp = compOp
        self.success = succ
        self.failure = fail

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRIf
        """

        l = []

        i = 0
        v1 = self.lhs
        v2 = self.rhs

        c_op = ""
        j_op = ""

        try:
            v1 = int(v1)
        except ValueError:
            try:
                v1 = float(v1)
            except ValueError:
                pass

        try:
            v2 = int(v2)
        except ValueError:
            try:
                v2 = float(v2)
            except ValueError:
                pass

        if v1 == v2:
            if self.comp in ["==", "<=", ">="]:
                return [asmn.ASMNode("jmp", f"D.{self.success}", None, dontTouch=True)]
            else:
                return [asmn.ASMNode("jmp", f"D.{self.failure}", None, dontTouch=True)]
        else:
            
            if isinstance(v1, int):
                if v1 == 0:
                    l.append(asmn.ASMNode("xor", None, None, leftNeedsReg=True, rightNeedsReg=True))
                    v1 = None
                else:
                    l.append(asmn.ASMNode("mov", f"${v1}", None, rightNeedsReg=True))
                    v1 = f"${v1}"
            if isinstance(v2, int):
                if v2 == 0:
                    l.append(asmn.ASMNode("xor",  None, None, leftNeedsReg=True, rightNeedsReg=True))
                    v2 = None
                else:
                    l.append(asmn.ASMNode("mov", f"${v2}", None, rightNeedsReg=True))
                    v2 = f"${v2}"

        if self.comp == "==":
            c_op = "test"
            j_op = "je"
        elif self.comp == "!=":
            c_op = "test"
            j_op = "jne"
        elif self.comp == "<=":
            c_op = "cmp"
            j_op = "jle"
        elif self.comp == ">=":
            c_op = "cmp"
            j_op = "jge"
        elif self.comp == "<":
            c_op = "cmp"
            j_op = "jl"
        elif self.comp == ">":
            c_op = "cmp"
            j_op = "jg"
        l.append(asmn.ASMNode(c_op, v1, v2, leftNeedsReg=True, rightNeedsReg=True))
        l.append(asmn.ASMNode(j_op, f"D.{self.success}", None, dontTouch=True))
        l.append(asmn.ASMNode("jmp", f"D.{self.failure}", None,dontTouch = True))

        return l

class IRArth(IRNode):
    """
    Intermediate representation node for an arithmetic/assignment operation.
    """
    def __init__(self, node, ops, varName):
        """
        Args:
            node: The AST node for the arithmetical expression
            ops: The potential complex operands for the expression
            tvs: The tempoary variable stack
        """
        if(node == None and ops == None):
            pass
        else:
            self.node = node
            self.var = varName

            self.operator = node.name
            self.lhs = None
            self.rhs = None

            # Case 1: ops is empty
            if ops == [] and len(node.children) > 1:
                self.lhs = node.children[0].name
                self.rhs = node.children[1].name
            # Case 2: two elem in ops
            elif len(ops) == 2:
                self.lhs = ops[1]
                self.rhs = ops[0]
            else:
                pos = [node.children.index(x) for x in node.children if len(x.children) != 0 and len(node.children) > 1]

                # Case 3: one elem in ops but its the left element in the operation
                if pos == [0]:
                    self.lhs = ops[0]
                    self.rhs = node.children[1].name
                # Case 4: one elem in ops but its the right element in the operation
                elif pos == [1]:
                    self.lhs = node.children[0].name
                    self.rhs = ops[0]
                # Case 5: Its a unary operator
                elif pos == []:
                    self.lhs = ops[0] if ops != [] else node.children[0].name


    def __str__(self):
        if self.rhs:
            return f"{self.var} = {self.lhs} {self.operator} {self.rhs};"
        else:
            return f"{self.var} = {self.operator}{self.lhs};"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRArht node
        """

        l = []

        i = 0
        spec_op = False

        v1 = self.lhs
        v2 = self.rhs

        asm_op = ""

        try:
            v1 = int(v1)
        except ValueError:
            try:
                v1 = float(v1)
            except ValueError:
                pass

        if v2:
            try:
                v2 = int(v2)
            except ValueError:
                try:
                    v2 = float(v2)
                except ValueError:
                    pass

        v1InReg = False
        v2InReg = False

        if isinstance(v1, int):
            v1 = f"${v1}"
        if isinstance(v2, int):
            if v2 == 0:
                l.append(asmn.ASMNode("xor",  self.var,  self.var, leftNeedsReg=True, rightNeedsReg=True))
            v2 = f"${v2}"

        if self.operator == "+":
            asm_op = "add"
            if v2 == None:
                l.extend([
                    asmn.ASMNode("mov", v1, self.var, rightNeedsReg=True),
                ])
                spec_op = True
        elif self.operator == "-":
            if v2 == None:
                l.extend([
                    asmn.ASMNode("mov", v1, self.var, rightNeedsReg=True),
                    asmn.ASMNode("neg", self.var, None, leftNeedsReg=True),
                ])
                spec_op = True
            else:
                l.extend([
                    asmn.ASMNode("mov", v1, self.var),
                    asmn.ASMNode("sub", v2, self.var)
                ])
                spec_op = True
        elif self.operator == "*":
            asm_op = "imul"
            if v1.startswith("$"):
                l.extend([
                    asmn.ASMNode("mov",v2,self.var),
                    asmn.ASMNode("imul",self.var,self.var,aux=v1)
                ])
                spec_op = True
        elif self.operator == "/":
            if v2.startswith("$"):
                l.append(asmn.ASMNode("mov", v2, None, rightNeedsReg=True))
            l.extend([
                asmn.ASMNode("xor", "rdx", "rdx", dontTouch=True),
                asmn.ASMNode("mov", v1, "rax"),
                asmn.ASMNode("idiv", v2, None,leftNeedsReg=True),
                asmn.ASMNode("mov", "rax", self.var)
            ])
            spec_op = True
        elif self.operator == "%":
            if v2.startswith("$"):
                l.append(asmn.ASMNode("mov", v2, None, rightNeedsReg=True))
            l.extend([
                asmn.ASMNode("xor", "rdx", "rdx", dontTouch=True),
                asmn.ASMNode("mov", v1, "rax"),
                asmn.ASMNode("idiv", v2, None,leftNeedsReg=True),
                asmn.ASMNode("mov", "rdx", self.var)
            ])
            spec_op = True
        elif self.operator == "<<":
            asm_op = "sal"
            l.append(asmn.ASMNode("mov", v1, self.var, rightNeedsReg=True))
            if v2.startswith("$"):
                l.append(asmn.ASMNode("sal", v2, self.var))
            else:
                l.extend([
                    asmn.ASMNode("mov", v2, "rcx", dontTouch=True),
                    asmn.ASMNode("sal", "cl", self.var)
                ])
            spec_op = True
        elif self.operator == ">>":
            asm_op = "sar"
            l.append(asmn.ASMNode("mov", v1, self.var, rightNeedsReg=True))
            if v2.startswith("$"):
                l.append(asmn.ASMNode("sar", v2, self.var))
            else:
                l.extend([
                    asmn.ASMNode("mov", v2, "rcx", dontTouch=True),
                    asmn.ASMNode("sar", "cl", self.var)
                ])
            spec_op = True
        elif self.operator == "|":
            asm_op = "or"
        elif self.operator == "&":
            asm_op = "and"
        elif self.operator == "^":
            asm_op = "xor"
        elif self.operator == "!":
            l.extend([
                asmn.ASMNode("mov", v1, self.var, rightNeedsReg=True),
                asmn.ASMNode("xor", "rax", "rax", dontTouch=True),
                asmn.ASMNode("test", self.var, self.var, leftNeedsReg=True, rightNeedsReg=True),
                asmn.ASMNode("sete", "al", None, dontTouch=True),
                asmn.ASMNode("mov", "rax", self.var, rightNeedsReg=True)
            ])
            spec_op = True
        elif self.operator == "~":
            l.extend([
                asmn.ASMNode("mov", v1, self.var, rightNeedsReg=True),
                asmn.ASMNode("not", self.var, None, leftNeedsReg=True),
                ])
            spec_op = True

        if not spec_op:

            if v2 != self.var:
                l.append(
                    asmn.ASMNode("mov", v2, self.var, rightNeedsReg=True)
                )
                v2 = self.var

            l.extend([
                asmn.ASMNode(asm_op, v1, v2, rightNeedsReg=True),
            ])

        return l

    def fileInit(self,leftHand,op,rightHand,varName):
        """
        Args:
            leftHand: Left hand side of the op.
            op: The operator of the arithmatic function
            rightHand: Right hand side of the op.
            varname: Name of the variable
        """
        self.lhs = leftHand
        self.rhs = rightHand
        self.operator = op
        self.var = varName

class IRSpecial(IRNode):
    """
    Intermediate representation node for a special operation assignment. Special operations consist of pre/post increment and decrement operations.
    """
    def __init__(self, node, var):
        """
        Args:
            node: The AST node for the operation
            var: The variable which the operation is applied to
        """
        self.node = node
        self.var = var
        self.operation = self.node.name[0]


    def __str__(self):
        return f"{self.var} = {self.var} {self.operation} 1;"

    def asm(self):
        """
        Constructs assembly string of a special (i.e. inc/dec) instruction
        Returns:
            List of necessary ASMNodes representing assembly code.
        """

        if self.operation == "+":
            return [asmn.ASMNode("inc", self.var, None)]
        elif self.operation == '-':
            return [asmn.ASMNode("dec", self.var, None)]



class IRAssignment(IRNode):
    """
    Intermediate representation node for an assignment operation.
    """
    def __init__(self, lhs, rhs):
        """
        Args:
            lhs: The left hand side of the assignment
            rhs: The right hand side of the assignment
        """
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return f"{self.lhs} = {self.rhs};"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRAssignment
        """
        l = []

        op = "mov"
        v = self.rhs

        try:
            v = int(self.rhs)

            if v == 0:
                return [asmn.ASMNode("xor", self.lhs, self.lhs)]
            else:
                return [asmn.ASMNode("mov", f"${v}", self.lhs)]
        except ValueError:
            try:
                v = float(self.rhs)
                modif = "$"
            except ValueError:
                return [asmn.ASMNode(op, f"{v}", self.lhs,leftNeedsReg=True, rightNeedsReg=True)]
                pass
            # TODO: Understand how floating point registers work while not going bald like ben.
        return [asmn.ASMNode(op, f"{v}", self.lhs)]

class IRFunctionAssign(IRNode):
    """
    Intermediate representation node for a function call assignment.
    """
    def __init__(self, node, params, varName):
        """
        Args:
            node: The AST node for the funtion
            params: A list of parameters for the function call
            tvs: The tempoary variable stack
        """
        if(node == None and params == None):
            pass
        else:
            self.node = node
            self.name = self.node.children[0].name
            self.params = params
            self.lhs = varName

    def __str__(self):
        return f"{self.lhs} = {self.name}({', '.join(self.params)});"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRFunctionAssign
        """
        asm_calls = []

        fourByteRegisters = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]

        push_param = [x for i, x in enumerate(self.params) if i >= 6]
        reg_param = [x for i, x in enumerate(self.params) if i < 6]
        reg_param.reverse()

        for x in push_param:
            try:
                x = f"${int(x)}"
            except ValueError:
                pass
            asm_calls.append(asmn.ASMNode("push", x, None, leftNeedsReg=True if not x.startswith("$") else False, dontTouch=True))

        while len(fourByteRegisters) > len(reg_param):
            fourByteRegisters.pop()

        for x in reg_param:
            try:
                x = f"${int(x)}"
            except ValueError:
                pass
            asm_calls.append(asmn.ASMNode("mov", x, fourByteRegisters.pop(), regIsParam=True, leftNeedsReg=True if not x.startswith("$") else False))

        asm_calls.extend([
            asmn.ASMNode("call", self.name, None, dontTouch=True),
            asmn.ASMNode("mov", "rax", self.lhs)
        ])

        return asm_calls

    def LineFromFile(self,lhs,func_name,params):
        """
        Args:
            lhs: left hand side of the assignment.
            func_name: name of the function call.
            params: parameters of the function call.
        """
        self.lhs = lhs
        self.name = func_name
        self.params = params


class IRFunctionDecl(IRNode):
    """
    Intermediate representation node for a function declaration.
    """
    def __init__(self, name, params):
        """
        Args:
            name: Name of function call.
            params: The function params as a string
        """
        self.name = name
        self.params = params

    def __str__(self):
        return f"{self.name} ({', '.join(self.params)})"

    def asm(self):
        """
        Constructs assembly Nodes of a function declaration

        Returns:
            List of ASM Nodes representing assembly code.
        """

        # value: register name
        # key: used/unused (1/0)
        fourByteRegisters = {"rdi": 0, "rsi": 0, "rdx": 0, "rcx": 0, "r8": 0, "r9": 0}
        eightByteRegisters = {"XMM0": 0, "XMM1": 0, "XMM2": 0, "XMM3": 0, "XMM4": 0, "XMM5": 0, "XMM6": 0, "XMM7": 0}

        asmLs = []

        regdir = {}
        stack = []

        for idx, var in enumerate(self.params):
            if idx < 6:
                source_reg = [x for x, y in fourByteRegisters.items() if y == 0][0]
                fourByteRegisters[source_reg] = 1

                regdir[source_reg] = var.split(' ')[-1]
            else:
                stack.append(stk.stackObj(Type="KnownVar", Name=var.split(' ')[-1]))

        asmLs.extend([
            asmn.ASMNode(None, None, None,boilerPlate=f".globl\t{self.name}"),
            asmn.ASMNode(None, None, None,boilerPlate=f".type\t{self.name},\t@function"),
            asmn.ASMNode(f"{self.name}:",None,None, functionDecl=True, regDir=regdir, stack=stack),
            asmn.ASMNode("mov", "rsp", "rbp", dontTouch=True),
            asmn.ASMNode("push", "rbx", None, dontTouch=True),
            asmn.ASMNode("push", "r12", None, dontTouch=True),
            asmn.ASMNode("push", "r13", None, dontTouch=True),
            asmn.ASMNode("push", "r14", None, dontTouch=True),
            asmn.ASMNode("push", "r15", None, dontTouch=True),
        ])

        return asmLs

class IRReturn(IRNode):
    """
    Intermediate representation node for a return.
    """
    def __init__(self, value):
        """
        Args:
            value: The return value. Can be 'None' for void functions.
        """
        self.value = value

    def __str__(self):
        if self.value:
            return f"return {self.value};"
        else:
            return f"return;"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRReturn
        """

        asml = []
        if self.value:
            asml.append(asmn.ASMNode("mov", self.value, "rax"))
        asml.extend([
            asmn.ASMNode("ret", None, None, dontTouch=True)
        ])

        return asml

class IRBracket(IRNode):
    """
    Intermediate representation node for a bracket
    """
    def __init__(self, opening, functionDecl=False):
        """
        Args:
            opening: Either True or False depending on if bracket is open/close
        """
        self.opening = opening
        self.functionDecl = functionDecl

    def __str__(self):
        if self.opening == True:
            return "{"
        else:
            return "}"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRBracket
        """

        if self.functionDecl:
            return []
        else:
            return []
        # TODO: determine how many local variables exist within the scope in order to move the stack pointer.

class IRVariableInit(IRNode):
    """
    Intermediate representation node for a variable initialization.
    """
    def __init__(self, modifiers, typ, var):
        """
        Args:
            modifiers:
            type:
            var:
        """
        self.modifiers = modifiers

        self.typ = typ

        self.var = var

    def __str__(self):
        return f"{self.modifiers}{self.typ} {self.var};"

    def asm(self):
        """
        Generates assembly representation of this node, using the variable names instead of registers

        Returns:
            The assembly representation of an IRVariableInit
        """

        return []
