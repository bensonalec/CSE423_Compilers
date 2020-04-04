"""
This module serves to construct the first linear intermediate representation in the compiler.
"""
import os
import re
import sys

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
            IR: A collection of strings and IRLine objects which can be optimized and/or transformed into assembly.
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

        returnDigit = 1234
        labelDigit = returnDigit + 1
        lines = []

        for i in bodyList:
            # Beginning of fuction wrapper
            lines.extend(beginWrapper(i, returnDigit))

            # Body of function
            tmp_lines , labelDigit = returnLines(i[1], returnDigit, labelDigit)
            lines.extend(tmp_lines)

            # End of function wrapper, add closing bracket
            lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=False)))

            # NOTE: 'labelDigit' should be the newest and unused digit
            returnDigit = labelDigit

            self.IR = lines

        return self.IR


    def __str__(self):
        return "\n".join([str(x) for x in self.IR]) + "\n"

    def optimize(self, opt):
        if opt > 0:
            self.remove_unused_funcs()
            self.remove_unused_vars()

        if opt > 1:
            self.var_values = {func.name : {var.name : 0 for var in self.symTable.symbols if var.entry_type == 0 and var.scope.startswith(f"/{func.name}")} for func in [sym for sym in self.symTable.symbols if sym.entry_type == 1]}
            while 1:
                cf = False
                cp = False
                cur_scope = ""
                for i in range(len(self.IR)):
                    if isinstance(self.IR[i].treeList[0], irl.IRFunctionDecl):
                        cur_scope = self.IR[i].treeList[0].name
                    tmp = self.constant_folding()
                    cf |= tmp

                    tmp, vals = self.constant_propagation(i, copy(self.var_values[cur_scope]))

                    for val in vals.items():
                        if val[0] in self.var_values[cur_scope]:
                            self.var_values[cur_scope][val[0]] = val[1]

                    cp |= tmp

                if not (cp and cf):
                    break

    def remove_unused_vars(self):
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

    def remove_unused_funcs(self):
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

    def constant_folding(self):
        notFound = True
        changed = False
        for line in self.IR:
            for it,x in enumerate(line.treeList):
                if isinstance(x,irl.IRArth):
                    notFound = True
                    op = False
                    #get the operator being used
                    if(x.rhs != None and x.lhs != None):
                        if(x.operator == "+"):
                            op = lambda rhs, lhs : str(rhs + lhs)
                        elif(x.operator == "-"):
                            op = lambda rhs, lhs : str(rhs - lhs)
                        elif(x.operator == "*"):
                            op = lambda rhs, lhs : str(rhs * lhs)
                        elif(x.operator == "/"):
                            op = lambda rhs, lhs : str(rhs / lhs)
                        elif(x.operator == "%"):
                            op = lambda rhs, lhs : str(rhs % lhs)
                        elif(x.operator == "<<"):
                            op = lambda rhs, lhs : str(rhs << lhs)
                        elif(x.operator == ">>"):
                            op = lambda rhs, lhs : str(rhs >> lhs)
                        elif(x.operator == "|"):
                            op = lambda rhs, lhs : str(rhs | lhs)
                        elif(x.operator == "&"):
                            op = lambda rhs, lhs : str(rhs & lhs)
                        elif(x.operator == "^"):
                            op = lambda rhs, lhs : str(rhs ^ lhs)
                    else:
                        if(x.operator == "~"):
                            op = lambda rhs, lhs : str(~lhs)
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
                        newValue = lambda rhs, lhs, op : op(rhs,lhs)
                        newAss = irl.IRAssignment(x.var,newValue(rhs,lhs,op))
                        line.treeList[it] = newAss
                        changed = True
        return changed

    def constant_propagation(self, index, var_val):

        # NOTE: The current issue is that the propogation is goint to have to exit and re enter the function every time to achieve the following:
        # Clear the tempoary variables per line as they are re used
        # Avoid propogating too far so that assignments in the future that may happen after certain other computations and assignments propogate the correct value

        # TODO: Fix to detect whether the reference is necessary or not. Eg, comparisons in loops compared to simple ifs
        # TODO: Ensure that when comming across a value that is not computable or propogatable such as after some control flow, the dictionary value becomes something distinguisable so that the expression is left alone

        changed = False
        for node in self.IR[index].treeList:
            if isinstance(node, irl.IRIf):
                if node.lhs in var_val:
                    node.lhs = var_val[node.lhs]
                    changed = True
                if node.rhs in var_val:
                    node.rhs = var_val[node.rhs]
                    changed = True

            elif isinstance(node, irl.IRArth):
                if node.lhs in var_val:
                    node.lhs = var_val[node.lhs]
                    changed = True
                if node.rhs in var_val:
                    node.rhs = var_val[node.rhs]
                    changed = True

            elif isinstance(node, irl.IRSpecial):
                pass
                # Assigning a value for a post and pre increment is extremly difficult due to the fact that it regularly occurs in loops and constants arent useful there.

            elif isinstance(node, irl.IRAssignment):
                if node.rhs in var_val:
                    node.rhs = var_val[node.rhs]
                    var_val[node.lhs] = node.rhs
                    changed = True
                elif node.rhs.isnumeric():
                    var_val[node.lhs] = node.rhs

            elif isinstance(node, irl.IRFunctionCall):
                for j, param in enumerate(node.params):
                    if param in var_val:
                        node.params[j] = var_val[param]
                        changed = True

        return changed, var_val

def buildBoilerPlate(symTable):
    namesandparams = []
    functionNames = [(x.name,x.type) for x in symTable.symbols if x.is_function]
    params = [(x.name,x.scope,x.type) for x in symTable.symbols if x.is_param]

    for x in functionNames:
        track = 0
        paramsLi = []
        for i in params:
            if x[0] == i[1].split("/")[1]:
                track+=1

                paramsLi.append((i[2],i[0]))
        if track == 0:
            namesandparams.append((x[0],paramsLi,x[1]))
        else:
            namesandparams.append((x[0],paramsLi,x[1]))
    return namesandparams

def beginWrapper(function_tuple, returnDigit):
    """
    Produces the function wrappers and initializes the return digit for the given function.

    Returns:
        lines: The lines of the start of the function
    """
    lines = []
    params = ""
    func_type = function_tuple[0].children[0].name
    func_name = function_tuple[0].children[1].name

    for var in function_tuple[0].children[2].children:
        if var.name == "var":
            params += f"{var.children[0].name} {var.children[1].name},"

    lines.append(irl.IRLine.singleEntry(irl.IRFunctionDecl(func_name, params[:-1])))
    lines.append(irl.IRLine.singleEntry(irl.IRBracket(opening=True)))

    if func_type != "void":
        modifiers = f"{''.join([x.name for x in function_tuple[0].children[0].children if x.name in ['signed', 'unsigned']])}{' ' if [x.name for x in function_tuple[0].children[0].children if x.name in ['signed', 'unsigned']] else ''}"
        lines.append(irl.IRLine.singleEntry(irl.IRVariableInit(modifiers, func_type, f"D.{returnDigit}")))

    return lines

def returnLines(node,returnDigit,labelDigit,successDigit=None,failureDigit=None):
    """
    Produces a linear representation of the content nested within `node`.

    Args:
        node: The AST node.
        returnDigit: The variable to store the return value.
        labelDigit: A list of all previously used label values.
        successDigit: The label value to jump to if there is a `continue`.
        failureDigit: The label value to jump to if there is a `break`.
        prefix: The string prefix for indenting the given line.

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
                lines.append(irl.IRLine.singleEntry(irl.IRVariableInit(modifiers, x.children[0].name, x.children[1].name), [labelDigit]))

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
                tmp, labelDigit = returnLines(element.children[3], returnDigit, labelDigit, loopStart, loopEnd)
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
                        tmp, labelDigit = returnLines(case.children[0], returnDigit, labelDigit, success_label, failure_label)
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
                    tmp, labelDigit = returnLines(case.children[1], returnDigit,  labelDigit, success_label, failure_label)
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
                tmp, labelDigit = returnLines(element.children[1], returnDigit, labelDigit, loopStart, loopEnd)
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
                lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{failureDigit}>"), [labelDigit]))

            elif ind == 8:
                # Continue
                lines.append(irl.IRLine.singleEntry(irl.IRGoTo(f"<D.{successDigit}>"), [labelDigit]))

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
                # Special assignment? (++, --)
                line = irl.IRLine(element, tvs=[])
                tvs, labelList = line.retrieve()
                lines.append(line)

            else:
                print("Unsupported at this time")

        except Warning:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass

    return lines, labelDigit
