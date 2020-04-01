"""
This module abstracts the necessary lines for the linear IR to allow for easier optimization methods like constant propagation, constant folding, unused references ect.
"""
import importlib

ast = importlib.import_module("AST_builder", __name__)

class IRLine():
    """
    A class that contains all the intermediate representations for a given AST node. Will produce a linear representation when converted to a string
    """
    def __init__(self, node, tvs = [], success = None, failure = None, labelList = [], prefix = "", varval = {}):
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
        self.var_val = varval

        # Based on the node construct the needed intermediate trees in order

        if node.name in self.log_ops:
            self.boolean_breakdown(self.astNode, success, failure)
        else:
            self.expression_breakdown(self.astNode, success, failure)

    def retrieve(self):
        """
        Retrieves the updated tempoary variable storage and list of unavialable label names for the future.

        Returns:
            tvs: The current tempoary variable storage
            labelList: The list of used label names
        """
        return self.tvs, self.labelList, self.var_val

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
                self.treeList.append(
                    IRArth(
                        node,
                        [self.tvs.pop() for x in node.children if len(x.children) != 0],
                        self.tvs
                    )
                )

                self.tvs.append(self.treeList[-1].var)

            elif node.name in self.spec_ops:
                var = self.tvs.pop()

                # Create a temporay AST to deal with storing of the current value of the variable
                tmpNode = ast.ASTNode("=", None)
                tmpNode.children.append(ast.ASTNode(f"_{len(self.tvs)}", tmpNode))
                tmpNode.children.append(ast.ASTNode(var, tmpNode))

                self.treeList.append(
                    IRAssignment(
                        f"_{len(self.tvs)}",
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

                self.tvs.append(tmpNode.children[0].name)

            elif node.name in self.ass_ops:
                if self.ass_ops.index(node.name) == 0:
                    lhs = None
                    rhs = None
                    # Case 1: Assignment is constant. ie. int i = 0
                    if len(node.children[1].children) == 0:
                        lhs = self.tvs.pop()
                        rhs = node.children[1].name
                    # Case 2: Assignment is complex
                    else:
                        lhs = node.children[0].children[len(node.children[0].children)-1].name
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

                    # assign the variable as the left operand of the new expression
                    r.children.append(node.children[0])

                    # assign the remaining operations as the right operand of the new expression
                    r.children.append(node.children[1])

                    self.expression_breakdown(p, success, failure)

            elif node.name in self.id_ops:
                if node.name == "var":
                    self.tvs.append(f"{node.children[len(node.children)-1].name}")
                elif node.name == "call":
                    # list of indices that correspond to the complex parameters of the function call
                    complexP = [node.children[0].children.index(x) for x in node.children[0].children if len(x.children) > 0]
                    simpleP = [x for x in range(len(node.children[0].children)) if x not in complexP]

                    params = [self.tvs.pop() for x in range(len(node.children[0].children)) if x in complexP]
                    self.treeList.append(
                        IRFunction(
                            node,
                            [params.pop() if x in complexP else node.children[0].children[x].name for x in range(len(node.children[0].children))],
                            self.tvs
                        )
                    )

                    self.tvs.append(self.treeList[-1].var)

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

    def constantFolding(self):
        #Perform constant folding for the following operatros:
        #   +,-,/,*,%
        #On the following types:
        #   int,float
        #TODO: Maybe ++, --?
        # print("Folding")
        for it,x in enumerate(self.treeList):
            #check that it's arithmetic
            if "operator" in x.__dict__:
                if(x.operator == "+"):
                    try:
                        if(int(x.lhs) and int(x.rhs)):
                            newValue = str((int(x.lhs) + int(x.rhs)))
                            # self.treeList = [newValue]
                            self.treeList[it] = f"{x.var} = {newValue}"
                    except ValueError:
                        try:
                            if(float(x.lhs) and float(x.rhs)):
                                newValue = str((float(x.lhs) + float(x.rhs)))
                                # self.treeList = [newValue]
                                self.treeList[it] = f"{x.var} = {newValue}"
                        except ValueError:
                            pass
                elif(x.operator == "-"):
                    try:
                        if(int(x.lhs) and int(x.rhs)):
                            newValue = str((int(x.lhs) - int(x.rhs)))
                            # self.treeList = [newValue]
                            self.treeList[it] = f"{x.var} = {newValue}"
                    except ValueError:
                        try:
                            if(float(x.lhs) and float(x.rhs)):
                                newValue = str((float(x.lhs) - float(x.rhs)))
                                # self.treeList = [newValue]
                                self.treeList[it] = f"{x.var} = {newValue}"
                        except ValueError:
                            pass
                elif(x.operator == "*"):
                    try:
                        if(int(x.lhs) and int(x.rhs)):
                            newValue = str((int(x.lhs) * int(x.rhs)))
                            # self.treeList = [newValue]
                            self.treeList[it] = f"{x.var} = {newValue}"
                    except ValueError:
                        try:
                            if(float(x.lhs) and float(x.rhs)):
                                newValue = str((float(x.lhs) * float(x.rhs)))
                                # self.treeList = [newValue]
                                self.treeList[it] = f"{x.var} = {newValue}"
                        except ValueError:
                            pass

                        pass
                elif(x.operator == "/"):
                    try:
                        if(int(x.lhs) and int(x.rhs)):
                            newValue = str((int(x.lhs) / int(x.rhs)))
                            # self.treeList = [newValue]
                            self.treeList[it] = f"{x.var} = {newValue}"
                            print(it)
                    except ValueError:
                        try:
                            if(float(x.lhs) and float(x.rhs)):
                                newValue = str((float(x.lhs) / float(x.rhs)))
                                # self.treeList = [newValue]
                                self.treeList[it] = f"{x.var} = {newValue}"
                        except ValueError:
                            pass

                        pass
                elif(x.operator == "%"):
                    try:
                        if(int(x.lhs) and int(x.rhs)):
                            newValue = str((int(x.lhs) % int(x.rhs)))
                            # self.treeList = [newValue]
                            self.treeList[it] = f"{x.var} = {newValue}"
                    except ValueError:
                        try:
                            if(float(x.lhs) and float(x.rhs)):
                                newValue = str((float(x.lhs) % float(x.rhs)))
                                # self.treeList = [newValue]
                                self.treeList[it] = f"{x.var} = {newValue}"
                        except ValueError:
                            pass


    def constant_propagation(self):
        for i, line in enumerate(self.treeList):
            if isinstance(line, IRIf):
                if line.lhs in self.var_val:
                    line.lhs = self.var_val[line.lhs]
                if line.rhs in self.var_val:
                    line.rhs = self.var_val[line.rhs]
            elif isinstance(line, IRArth):
                if line.lhs in self.var_val:
                    line.lhs = self.var_val[line.lhs]
                if line.rhs in self.var_val:
                    line.rhs = self.var_val[line.rhs]
            elif isinstance(line, IRSpecial):
                pass
                # Assigning a value for a post and pre increment is extremly difficult due to the fact that it regularly occurs in loops and constants arent useful there.
            elif isinstance(line, IRAssignment):
                if line.rhs in self.var_val:
                    line.rhs = self.var_val[line.rhs]
                    self.var_val[line.lhs] = line.rhs
                elif line.rhs.isnumeric():
                    self.var_val[line.lhs] = line.rhs
            elif isinstance(line, IRFunction):
                for j, param in enumerate(line.params):
                    if param in self.var_val:
                        line.params[j] = self.var_val[param]

    def __str__(self):
        return "\n".join([f"{self.prefix}{x}" for x in self.treeList])

class IRNode():
    """
    Abstract intermediate representation node. Base class for all other IR representations other than IRLines.
    """
    def __init__(self):
        pass

    def __str__(self):
        pass

    def __repr__():
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

    def __repr__():
        pass

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

    def __repr__():
        pass

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

    def __repr__():
        pass

class IRArth(IRNode):
    """
    Intermediate representation node for an arithmetic/assignment operation.
    """
    def __init__(self, node, ops, tvs):
        """
        Args:
            node: The AST node for the arithmetical expression
            ops: The potential complex operands for the expression
            tvs: The tempoary variable stack
        """
        self.node = node
        self.var = f"_{len(tvs)}"

        self.operator = node.name
        self.lhs = None
        self.rhs = None

        # Case 1: ops is empty
        if ops == [] and len(node.children) > 1:
            self.lhs = node.children[0].name
            self.rhs = node.children[1].name
        # Case 2: two elem in ops
        elif len(ops) == 2:
            self.lhs = ops[0]
            self.rhs = ops[1]
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

    def __repr__():
        pass

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

    def __str__(self):
        return f"{self.var} = {self.var} {self.node.name[0]} 1;"

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

class IRFunction(IRNode):
    """
    Intermediate representation node for a function call assignment.
    """
    def __init__(self, node, params, tvs):
        """
        Args:
            node: The AST node for the funtion
            params: A list of parameters for the function call
            tvs: The tempoary variable stack
        """
        self.node = node
        self.params = params
        self.var = f"_{len(tvs)}"

    def __str__(self):
        if self.var:
            return f"{self.var} = {self.node.children[0].name}({', '.join(self.params)});"
        else:
            return f"{self.node.children[0].name}({', '.join(self.params)});"
