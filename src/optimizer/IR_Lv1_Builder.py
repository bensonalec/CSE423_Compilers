"""
This module serves to construct the first linear intermediate representation in the compiler.
"""
import os
import re
import sys
import math

from inspect import getsourcefile
from importlib.machinery import SourceFileLoader
from copy import deepcopy, copy

irl = SourceFileLoader("IRLine", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/IRLine.py").load_module()
ast = SourceFileLoader("AST_builder", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/../frontend/AST_builder.py").load_module()

class LevelOneIR():
    """
    Constructs the linear representation of the input program in order to allow for optimizations such as constant folding, constant proagation, as well as removal of unused variables and functions depending on the optimization level provided as a commandline argument.
    """
    def __init__(self,astHead,symTable):
        """
        Args:
            astHead: The root node of the AST
            symTable: The symbol table for the input
        """
        self.astHead = astHead
        self.symTable = symTable
        self.IR = []

    def construct(self):
        """
        Constructs the linear representation for the object.

        Returns:
            IR: A collection of IRLine objects which can be optimized and/or transformed into assembly.
        """
        sym = self.symTable
        ntv = self.astHead

        varIndex = 0
        lastVarName = "_" + str(varIndex)
        bodyList = []

        # list of all bodies within functions in our C program
        for x in self.astHead.children:
            if x.name == "func":
                # Each entry is the '(func_node, body_node)'
                bodyList.append((x,x.children[3]))

        # Digits are used for contructing unique labels
        returnDigit = 1234
        labelDigit = returnDigit + 1
        lines = []

        for i in bodyList:
            # Beginning of fuction wrapper
            lines.extend(beginWrapper(i, returnDigit))

            # Body of function
            tmp_lines , labelDigit = returnLines(i[1], returnDigit, labelDigit)
            lines.extend(tmp_lines)

            if not isinstance(lines[-1].treeList[-1], irl.IRReturn):
                lines.append(irl.IRLine.singleEntry(irl.IRReturn(None)))

            # End of function wrapper, add closing bracket
            lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=False, functionDecl=True)))

            # NOTE: 'labelDigit' should be the newest and unused digit
            returnDigit = labelDigit

            self.IR = lines

        return self.IR


    def __str__(self):
        return "\n".join([str(x) for x in self.IR]) + "\n"

    def optimize(self, opt):
        """
        Performs the optimizations based on the level of optimization

        Args:
            opt: The level of optimization to be performed.
        """
        if opt > 0:
            self.remove_unused_funcs()
            self.remove_unused_vars()
            pass

        # constant folding/propagation
        if opt > 1:
            # A dictionary containing all the values of variables that can at some point be reduced.
            self.var_values = {
                func.name : {
                    var.name : "Undef"
                    for var in self.symTable.symbols if var.entry_type == 0 and var.scope.startswith(f"/{func.name}")
                }
                for func in [sym for sym in self.symTable.symbols if sym.entry_type == 1]
            }

            # NOTE: As a method of knowing whether it is safe to continue on to the next node in the list the following measures have been implemented:
            # Both constant folding and constant propagation only consider a singular value.
            # They both return a boolean describing whether the node was altered as well as some descriptor of what it did.
                # In the case of constant folding, the descriptor is the new simplified node which then has to be assigned to the correct index.
                # In the case of constant propagation, the descriptor is a dictionary containing the updated values relevant to the scope of the IRLine object meaning that tempoary variables are stored within the IRLine but now within the scope as a whole.
            # The idea is that while either of these methods can alter the node you keep executing them on the node so that if the loop terminates the program is sure that the node cannot be reduced further.
            # Another final optimization that can be done would be to check if all the nodes in an IRLine object are `IRAssignment`, if so the last one is the only `IRAssignment` node needed, and the others can be removed.

            prev_maj = 0
            cur_scope = ""
            tmp_vals = {}
            for major, minor, node in [(major, minor, node) for major, tl in enumerate(self.IR) for minor, node in enumerate(tl.treeList)]:
                if major != prev_maj:
                    tmp_vals = {}

                if isinstance(node, irl.IRFunctionDecl):
                    cur_scope = node.name
                elif isinstance(node, irl.IRGoTo) or isinstance(node, irl.IRJump) or isinstance(node, irl.IRIf):
                    for val in tmp_vals.items():
                        if val[0] in self.var_values[cur_scope]:
                            self.var_values[cur_scope][val[0]] = "Undef"
                        tmp_vals[val[0]] = "Undef"
                else:
                    for val in self.var_values[cur_scope].items():
                        tmp_vals[val[0]] = val[1]

                ncf = False
                ncp = False

                while 1:
                    ncf, tmp = self.constant_folding(node)

                    if ncf:
                        self.IR[major].treeList[minor] = tmp
                        node = tmp

                    ncp, vals = self.constant_propagation(node, tmp_vals)

                    for val in vals.items():
                        if val[0] in self.var_values[cur_scope]:
                            self.var_values[cur_scope][val[0]] = val[1]
                        tmp_vals[val[0]] = val[1]

                    if not (ncf or ncp):
                        break
                prev_maj = major

            self.cleanup()

    def remove_unused_vars(self):
        """
        Removes unused variables based on the number of references found in the symbol table
        """
        ir = self.IR
        scope = ""

        #get variables to remove
        vars_temp = [[x.name, x.scope] for x in self.symTable.symbols if x.entry_type != 2 and x.entry_type != 1 and x.entry_type != 3 and len(x.references) == 0]
        #get function from symbol table.
        funcs = [x.name for x in self.symTable.symbols if x.entry_type == 1]

        final_ir = []

        for irLine in ir:

            for idx, irNode in enumerate(irLine.treeList):
                #check if function declaration, to set new scope
                if isinstance(irNode, irl.IRFunctionDecl):
                    scope = irNode.name

                #check if declaration
                if isinstance(irNode, irl.IRVariableInit):
                    #check if variable needs to be skippped
                    if [x for x in vars_temp if x[0] == irNode.var and scope in x[1]] != []:
                        del irLine.treeList[idx]

                #check if usage
                elif(isinstance(irNode, irl.IRAssignment)):
                    if [x for x in vars_temp if x[0] == irNode.lhs and scope in x[1]] != []:
                        del irLine.treeList[idx]

            #irLine has no irNode inside...so we dont add it to new IR list
            if irLine.treeList == []:
                pass
            else:
                final_ir.append(irLine)


        self.IR = final_ir

    def cleanup(self):
        """
        Cleans up the IR by looking at the considering the number of references withing the local `IRLine` object. This allows for the removal of unused tempoary variables.
        """

        class ref():
            def __init__(self, init_index, init_ref_type, side):
                self.refs = [init_index]
                self.ref_types = [init_ref_type]
                self.side = [side]

            def add(self, index, ref_type, side):
                self.refs.append(index)
                self.ref_types.append(ref_type)
                self.side.append(side)

            def __str__(self):
                return f"\t{self.refs}\t{self.ref_types}\t{self.side}"

            def __repr__(self):
                return self.__str__()

        gr = {}
        for line in self.IR:
            lr = {}

            for i, node in enumerate(line.treeList):
                if isinstance(node, irl.IRAssignment):
                    if node.lhs in lr:
                        lr[node.lhs].add(i, "assignment", 0)
                    else:
                        lr[node.lhs] = ref(i, "assignment", 0)

                    tmp = node.rhs.lstrip('-+').replace('.', '', 1)
                    if node.rhs in lr and not tmp.isnumeric():
                        lr[node.rhs].add(i, "assignment", 1)
                    elif not tmp.isnumeric():
                        lr[node.rhs] = ref(i, "assignment", 1)
                elif isinstance(node, irl.IRArth):
                    if node.var in lr:
                        lr[node.var].add(i, "assignment", 0)
                    else:
                        lr[node.var] = ref(i, "assignment", 0)

                    tmp = node.lhs.lstrip('-+').replace('.', '', 1)
                    if node.lhs in lr and not tmp.isnumeric():
                        lr[node.lhs].add(i, "arithmetic", 1)
                    elif not tmp.isnumeric():
                        lr[node.lhs] = ref(i, "arithmetic", 1)

                    if node.rhs:
                        tmp = node.rhs.lstrip('-+').replace('.', '', 1)
                        if node.rhs in lr and not tmp.isnumeric():
                            lr[node.rhs].add(i, "arithmetic", 2)
                        elif not tmp.isnumeric():
                            lr[node.rhs] = ref(i, "arithmetic", 2)
                elif isinstance(node, irl.IRFunctionAssign):
                    if node.lhs in lr:
                        lr[node.lhs].add(i, "assignment", 0)
                    else:
                        lr[node.lhs] = ref(i, "assignment", 0)

                    for param in node.params:
                        tmp = node.lhs.lstrip('-+').replace('.', '', 1)
                        if param in lr and not tmp.isnumeric():
                            lr[node.lhs].add(i, "param", 1)
                        elif not tmp.isnumeric():
                            lr[node.lhs] = ref(i, "param", 1)
                elif isinstance(node, irl.IRIf):
                    tmp = node.lhs.lstrip('-+').replace('.', '', 1)
                    if node.lhs in lr and not tmp.isnumeric():
                        lr[node.lhs].add(i, "collation", 1)
                    elif not tmp.isnumeric():
                        lr[node.lhs] = ref(i, "collation", 1)

                    tmp = node.rhs.lstrip('-+').replace('.', '', 1)
                    if node.rhs in lr and not tmp.isnumeric():
                        lr[node.rhs].add(i, "collation", 2)
                    elif not tmp.isnumeric():
                        lr[node.rhs] = ref(i, "collation", 2)
                elif isinstance(node, irl.IRSpecial):
                    if node.var in lr:
                        lr[node.var].add(i, "assignment", 0)
                        lr[node.var].add(i, "assignment", 1)
                    else:
                        lr[node.var] = ref(i, "assignment", 0)
                        lr[node.var].add(i, "assignment", 1)
                elif isinstance(node, irl.IRReturn):
                    if node.value:
                        tmp = node.value.lstrip('-+').replace('.', '', 1)
                        if node.value in lr:
                            lr[node.value].add(i, "return", 0)
                        elif not tmp.isnumeric():
                            lr[node.value] = ref(i, "return", 0)
            rem_list = []

            for var in lr.items():
                # print(var)
                for i, typ in enumerate(var[1].ref_types):
                    if (
                        i+1 < len(var[1].ref_types)
                        and
                        typ == "assignment"
                        and
                        var[1].side[i] == 0
                        and
                        var[1].side[i+1] == 0
                        and
                        var[1].ref_types[i+1] == "assignment"
                        ):
                        rem_list.append(var[1].refs[i])
                    elif (
                        i+1 == len(var[1].ref_types)
                        and
                        typ == "assignment"
                        and
                        var[1].side[i] == 0
                        # and
                        # var[1].side[i+1] == 0
                        and
                        (
                            var[1].refs[i]+1 != len(line.treeList)
                            or
                            len(var[1].ref_types) > 1)
                        ):
                        rem_list.append(var[1].refs[i])

                # iterate over reference types and see if there are two assignments after each other.


            for node in reversed(sorted(rem_list)):
                line.treeList.pop(node)

    def remove_unused_funcs(self):
        """
        Removes function that are not reference in the symbol table. They can be removed if not used.
        """



        ir = self.IR
        inFunction = False
        to_remove = []

        for idx, irLine in enumerate(ir):

            # Only need to focus on first Node in each IRLine
            ir_firstNode = irLine.treeList[0]

            # Delete IRLine if we are in a 'unused' function
            # Mark 'inFunction' to False if beginning of new function
            if inFunction == True:
                if isinstance(ir_firstNode, irl.IRFunctionDecl):
                    inFunction = False
                else:
                    to_remove.append(idx)
                    continue

            # Check for function
            if isinstance(ir_firstNode, irl.IRFunctionDecl):
                func_name = ir_firstNode.name
                referenceNum = len([x.references for x in self.symTable.symbols if func_name == x.name and x.entry_type == 1][0])

                # If reference is 0, it is unused
                if referenceNum == 0 and func_name != "main":
                    to_remove.append(idx)
                    inFunction = True

        # Actually delete unused function IRLine's
        for i in to_remove[::-1]:
            del ir[i]


        self.IR = ir

    def constant_folding(self,x):
        """
        Peforms constant folding  on a given line in the IR

        Args:
            x: an IRNode object

        Returns:
            A boolean indicating whether it changed anything, and the node that has been modified
        """
        changed = False
        if isinstance(x,irl.IRArth):
            notFound = True
            op = False
            #get the operator being used
            if(x.rhs != None and x.lhs != None):
                if(x.operator == "+"):
                    op = lambda lhs, rhs : lhs + rhs
                elif(x.operator == "-"):
                    op = lambda lhs, rhs : lhs - rhs
                elif(x.operator == "*"):
                    op = lambda lhs, rhs : lhs * rhs
                elif(x.operator == "/"):
                    op = lambda lhs, rhs : lhs / rhs
                elif(x.operator == "%"):
                    op = lambda lhs, rhs : math.fmod(lhs, rhs)
                elif(x.operator == "<<"):
                    # There is an edge case around the changes of architectures so that values may differ depending on the architecture you are using. eg 10 << 31 compared to 10 << 20
                    op = lambda lhs, rhs : lhs << rhs
                elif(x.operator == ">>"):
                    # There is an edge case around the changes of architectures so that values may differ depending on the architecture you are using. eg 10 >> 31 compared to 10 >> 20
                    op = lambda lhs, rhs : lhs >> rhs
                elif(x.operator == "|"):
                    op = lambda lhs, rhs : lhs | rhs
                elif(x.operator == "&"):
                    op = lambda lhs, rhs : lhs & rhs
                elif(x.operator == "^"):
                    op = lambda lhs, rhs : lhs ^ rhs
            else:
                if(x.operator == "~"):
                    op = lambda lhs, rhs : ~lhs
                elif(x.operator == "-"):
                    op = lambda lhs, rhs : 0 - lhs
                elif(x.operator == "+"):
                    op = lambda lhs, rhs : 0 + lhs
                elif(x.operator == "!"):
                    op = lambda lhs, rhs : not lhs
            #get the left hand side and the right hand side
            try:
                lhs = int(x.lhs)
                if(not x.rhs == None):
                    rhs = int(x.rhs)
                else:
                    rhs = None
                notFound = False
            except ValueError:
                try:
                    lhs = float(x.lhs)
                    if(not x.rhs == None):
                        rhs = float(x.rhs)
                    else:
                        rhs = None
                    notFound = False
                except ValueError:
                    pass

            #if we found all components, replace the node
            if(not notFound and op):
                if rhs and rhs < 0:
                    if x.operator == "<<" or x.operator == ">>":
                        raise ValueError("shifting by negative number is undefined behavior.")

                newValue = lambda lhs, rhs, op : op(lhs,rhs)
                val = newValue(lhs,rhs,op) if isinstance(lhs, float) or isinstance(rhs, float) else math.floor(newValue(lhs,rhs,op))
                newAss = irl.IRAssignment(x.var, str(val))
                changed = True
                return changed,newAss
        return changed,x

    def constant_propagation(self, node, var_val):
        """
        Performs constant propagation on a given IRNode if deemed possible.

        Args:
            node: The IRNode object to be considered
            var_val: A dictionary of all the variables and their values which are deemed safe to replace

        Returns:
            The return value describes whether any propogation occurred during the function call
        """
        # NOTE: The current issue is that the propogation is goint to have to exit and re enter the function every time to achieve the following:
        # Clear the tempoary variables per line as they are re used
        # Avoid propogating too far so that assignments in the future that may happen after certain other computations and assignments propogate the correct value

        # TODO: Fix to detect whether the reference is necessary or not. Eg, comparisons in loops compared to simple ifs
        # TODO: Ensure that when comming across a value that is not computable or propogatable such as after some control flow, the dictionary value becomes something distinguisable so that the expression is left alone
        changed = False
        if isinstance(node, irl.IRIf):
            if node.lhs in var_val and var_val[node.lhs] != "Undef":
                node.lhs = var_val[node.lhs]
                changed = True
            if node.rhs in var_val and var_val[node.rhs] != "Undef":
                node.rhs = var_val[node.rhs]
                changed = True

        elif isinstance(node, irl.IRArth):
            if node.lhs in var_val and var_val[node.lhs] != "Undef":
                node.lhs = var_val[node.lhs]
                changed = True
            if node.rhs in var_val and var_val[node.rhs] != "Undef":
                node.rhs = var_val[node.rhs]
                changed = True

        elif isinstance(node, irl.IRAssignment):
            if node.rhs in var_val and var_val[node.rhs] != "Undef":
                node.rhs = var_val[node.rhs]
                var_val[node.lhs] = node.rhs
                changed = True
            else:
                tmp = node.rhs.lstrip('-+').replace('.', '', 1)
                if tmp.isnumeric():
                    var_val[node.lhs] = node.rhs

        elif isinstance(node, irl.IRFunctionAssign):
            for j, param in enumerate(node.params):
                if param in var_val and var_val[param] != None:
                    node.params[j] = var_val[param]
                    changed = True

        return changed, var_val

    def __str__(self):
        return "\n".join(self.IR) + "\n"

def beginWrapper(function_tuple, returnDigit):
    """
    Produces the function wrappers and initializes the return digit for the given function.

    Returns:
        lines: The lines of the start of the function
    """
    lines = []
    params = []
    func_type = function_tuple[0].children[0].name
    func_name = function_tuple[0].children[1].name

    for var in function_tuple[0].children[2].children:
        if var.name == "var":

            # list of all modifiers
            modifiers = f"{' '.join([x.name for x in var.children[0].children])}{' ' if [x.name for x in var.children[0].children] else ''}"

            # append entry for parameter
            params.append(f"{' '.join([modifiers])}{var.children[0].name} rV_{var.children[1].name}")

    lines.append(irl.IRLine.singleEntry(irl.IRFunctionDecl(func_name, params)))
    lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=True, functionDecl=True)))

    if func_type != "void":
        modifiers = f"{''.join([x.name for x in function_tuple[0].children[0].children if x.name in ['signed', 'unsigned']])}{' ' if [x.name for x in function_tuple[0].children[0].children if x.name in ['signed', 'unsigned']] else ''}"
        lines.append(irl.IRLine.singleEntry(irl.IRVariableInit(modifiers, func_type, f"D.{returnDigit}")))

    return lines

def returnLines(node,returnDigit,labelDigit,successDigit=None,failureDigit=None, breakDigit=None, continueDigit=None):
    """
    Produces a linear representation of the content nested within `node`.

    Args:
        node: The AST node.
        returnDigit: The variable to store the return value.
        labelDigit: A list of all previously used label values.
        successDigit: The label value to jump to if there is a `continue`.
        failureDigit: The label value to jump to if there is a `break`.
        breakDigit: The label used for break statements to have a correct label so the control flow is correct.

        continueDigit: The label used for a continue statement to know the 'ultimate' success of whatever block it is in

    Returns:
        lines: The lines produced from the content.
        labelDigit: The list of all used label values.
    """
    lines = []
    if node.name == "body":
        il = [x.children[0] for x in node.children if x.name == "=" and x.children[0].children[0].name in ["auto", "long double", "double", "float", "long long", "long long int", "long", "int", "short", "char"]]

        # It is the scopes responsibility to ensure that the content is wrapped in braces
        if il:
            for x in il:
                modifiers = f"{' '.join([y.name for y in x.children[0].children])}{' ' if [y.name for y in x.children[0].children] else ''}"
                lines.append(irl.IRLine.singleEntry(irl.IRVariableInit(modifiers, x.children[0].name, f"rV_{x.children[1].name}"), [labelDigit]))

    for element in node.children:
        try:
            splits = [["+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "|=", "&=", "^=", "<=", ">=", "="],["for"],["body"],["branch"],["return"],["call"],["while", "do_while"],["break"],["continue"],["goto"],["label"], ["++", "--"]]
            ind = [splits.index(x) for x in splits if element.name in x]
            ind = ind[0]
            if ind == 0:
                line = irl.IRLine(element, tvs=[], labelList=[labelDigit])
                tvs, labelList = line.retrieve()
                lines.append(line)

                if labelList != []:
                    labelDigit = labelList[-1]

            elif ind == 1:
                # For Loop
                ns = False
                # Initialize variable
                if element.children[0].children != []:
                    initNode = ast.ASTNode("body", None)
                    initNode.children.append(element.children[0])
                    if [x.children[0] for x in initNode.children if x.name == "=" and x.children[0].children[0].name in ["auto", "long double", "double", "float", "long long", "long long int", "long", "int", "short", "char"]]:
                        # Append an IRBracket node
                        lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=True), [labelDigit]))
                        ns = True
                    tmp, labelDigit = returnLines(initNode, returnDigit, labelDigit)
                    lines.extend(tmp)

                # Keep track of label for conditional block (if conditional exist)
                conditionLabel = None
                if element.children[1].children != []:

                    # Append an IRGoTo node
                    lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{labelDigit}>"), [labelDigit]))

                    conditionLabel = labelDigit
                    labelDigit += 1

                # Append an IRJump node for the label that belongs to the start of the loop
                lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{labelDigit}>"), [labelDigit]))

                # Assign labels for start/end of loop
                loopStart = labelDigit
                loopEnd = labelDigit + 1
                labelDigit += 2

                # recursivly deal with the body of the loop
                tmp, labelDigit = returnLines(element.children[3], returnDigit, labelDigit, loopStart, loopEnd, breakDigit=loopEnd, continueDigit=loopStart)
                lines.extend(tmp)

                # Add the "end-of-loop" assignment/arithmetic
                if element.children[2].children != []:
                    initNode = ast.ASTNode("tmp", None)
                    initNode.children.append(element.children[2])
                    tmp, labelDigit = returnLines(initNode, returnDigit, labelDigit)
                    lines.extend(tmp)

                # Start of conditionals for the loop
                if conditionLabel != None:
                    lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{conditionLabel}>"), [labelDigit]))

                    tmpNode = element.children[1]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[1])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                    line = irl.IRLine(tmpNode, tvs=[], success=loopStart, failure=loopEnd, labelList=[labelDigit])
                    tvs, labelList = line.retrieve()
                    lines.append(line)

                    if labelList != []:
                        labelDigit = labelList[-1]

                    lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{loopEnd}>"), [labelDigit]))

                else:
                    # No conditional (jump to start of body...always True)
                    lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{loopStart}>"), [labelDigit]))

                # increment twice for new index
                labelDigit += 2

                if ns:
                    # Append an IRBracket node
                    lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=False), [labelDigit]))

            elif ind == 2:
                # Append an IRBracket node
                lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=True), [labelDigit]))

                tmp, labelDigit = returnLines(element, returnDigit, labelDigit, successDigit, failureDigit)
                lines.extend(tmp)

                # Append an IRBracket node
                lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=False), [labelDigit]))

            elif ind == 3:
                # If/Else statement(s)

                # list of goto labels to be appended at end of if blocks
                end_if = []

                #for each case in a branch
                for case in element.children:
                    ns = False
                    #create label for body if true and label to skip to correct place if false.
                    success_label = labelDigit
                    labelDigit += 1
                    failure_label = labelDigit
                    labelDigit += 1

                    #default is an 'else'. Only has one child, body
                    if case.name == "default":
                        if [x.children[0] for x in case.children[0].children if x.name == "=" and x.children[0].children[0].name in ["auto", "long double", "double", "float", "long long", "long long int", "long", "int", "short", "char"]]:
                            # Append an IRBracket node
                            lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=True), [labelDigit]))
                            ns = True

                        #Get lines for the body and assign new labeldigit
                        tmp, labelDigit = returnLines(case.children[0], returnDigit, labelDigit, success_label, failure_label, failureDigit, successDigit)
                        lines.extend(tmp)

                        if ns:
                            # Append an IRBracket node
                            lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=False), [labelDigit]))

                        break

                    tmpNode = case.children[0]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(case.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                    #break down argument for if statement into smaller if statements
                    line = irl.IRLine(tmpNode, tvs=[], success=success_label, failure=failure_label, labelList=[labelDigit])
                    tvs, labelList = line.retrieve()
                    lines.append(line)

                    if labelList != []:
                        labelDigit = labelList[-1] + 1


                    #Add goto for body statement
                    lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{success_label}>"), [labelDigit]))

                    if [x.children[0] for x in case.children[1].children if x.name == "=" and x.children[0].children[0].name in ["auto", "long double", "double", "float", "long long", "long long int", "long", "int", "short", "char"]]:
                        # Append an IRBracket node
                        lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=True), [labelDigit]))
                        ns = True

                    #Get lines for the if body and assign new labeldigit
                    tmp, labelDigit = returnLines(case.children[1], returnDigit,  labelDigit, success_label, failure_label, failureDigit, successDigit)
                    lines.extend(tmp)

                    if ns:
                        # Append an IRBracket node
                        lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=False), [labelDigit]))

                    #append goto for end of if body
                    lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{labelDigit}>"), [labelDigit]))

                    end_if.append(labelDigit)
                    labelDigit += 1

                    lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{failure_label}>"), [labelDigit]))

                for i in end_if:
                    lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{i}>"), [labelDigit]))

            elif ind == 4:
                #Return

                # If returns some type of arithmetic expression, breaks it down.
                if len(element.children) > 0 and element.children[0].children != []:
                    line = irl.IRLine(element.children[0], tvs=[], labelList=[labelDigit])
                    tvs, labelList = line.retrieve()
                    if line.treeList != []:
                        lines.append(line)
                        lines[-1].treeList.append(irl.IRAssignment(f"D.{returnDigit}", f"{tvs[-1]}"))

                    else:
                        lines.append(irl.IRLine.singleEntry(irl.IRAssignment(f"D.{returnDigit}", f"{tvs[-1]}"), [labelDigit]))

                    lines.append(irl.IRLine.singleEntry(irl.IRReturn(f"D.{returnDigit}"), [labelDigit]))

                    if labelList != []:
                        labelDigit = labelList[-1]

                elif len(element.children) > 0 and element.children[0].children == []:
                    lines.append(irl.IRLine.singleEntry(irl.IRAssignment(f"D.{returnDigit}", f"{element.children[0].name}"), [labelDigit]))
                    lines.append(irl.IRLine.singleEntry(irl.IRReturn(f"D.{returnDigit}"), [labelDigit]))

                # Returns nothing
                else:
                    lines.append(irl.IRLine.singleEntry(irl.IRReturn(None), [labelDigit]))

            elif ind == 5:
                #Function Call
                func_call = element.children[0].name

                # function call has parameters
                if element.children[0] != []:
                    line = irl.IRLine(element.children[0], tvs=[], labelList=[labelDigit])
                    tvs, labelList = line.retrieve()
                    lines.append(line)

                    if labelList != []:
                        labelDigit = labelList[-1] + 1

                # no parameters
                else:
                    # Append Empty function call node
                    lines.append(irl.IRLine.singleEntry(irl.IRFunctionCall(func_call, None), [labelDigit]))

            elif ind == 6:
                #While and Do While

                ns = False

                # Jump straight to conditionals for only 'While' statements
                if element.name == "while":
                    lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{labelDigit}>"), [labelDigit]))

                # Keep track of label for conditional block
                conditionLabel = labelDigit
                labelDigit += 1

                # Add the label that belongs to the start of the loop
                lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{labelDigit}>"), [labelDigit]))

                if [x.children[0] for x in element.children[1].children if x.name == "=" and x.children[0].children[0].name in ["auto", "long double", "double", "float", "long long", "long long int", "long", "int", "short", "char"]]:
                        # Append an IRBracket node
                        lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=True), [labelDigit]))
                        ns = True

                # Assign labels for start/end of loop
                loopStart = labelDigit
                loopEnd = labelDigit + 1
                labelDigit += 2

                # recursivly deal with the body of the loop
                tmp, labelDigit = returnLines(element.children[1], returnDigit, labelDigit, loopStart, loopEnd, breakDigit=loopEnd, continueDigit=loopStart)
                lines.extend(tmp)

                if ns:
                    # Append an IRBracket node
                    lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=False), [labelDigit]))

                # Start of conditionals for the loop
                lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{conditionLabel}>"), [labelDigit]))

                tmpNode = element.children[0]
                if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                line = irl.IRLine(tmpNode, tvs=[], success=loopStart, failure=loopEnd, labelList=[labelDigit])
                tvs, labelList = line.retrieve()
                lines.append(line)

                lines.append(irl.IRLine.singleEntry(irl.IRJump(f"<D.{loopEnd}>"), [labelDigit]))

                if labelList != []:
                    labelDigit = labelList[-1]
                # increment twice for new index (twce, in case it was a do while)
                labelDigit += 2

            elif ind == 7:
                # Break
                if breakDigit:
                    lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{breakDigit}>"), [labelDigit]))

            elif ind == 8:
                # Continue
                if continueDigit:
                    lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{continueDigit}>"), [labelDigit]))

            elif ind == 9:
                # Goto
                lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"{element.children[0].name}"), [labelDigit]))
            elif ind == 10:
                # Jump Label
                lines.append(irl.IRLine.singleEntry(irl.IRJump(f"{element.children[0].name}"), [labelDigit]))

                if (len(element.children) > 1):
                    temp_lines, labelDigit = returnLines(element.children[1], returnDigit, labelDigit)

                    lines.extend(temp_lines)

            elif ind == 11:
                # Special assignment (++, --)
                line = irl.IRLine(element, tvs=[])
                tvs, labelList = line.retrieve()
                lines.append(line)

            else:
                pass
                # print("Unsupported at this time")

        except Warning:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            pass

    return lines, labelDigit
