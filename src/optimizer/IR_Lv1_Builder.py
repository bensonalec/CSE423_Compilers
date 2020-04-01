"""
This module serves to construct the first linear intermediate representation in the compiler.
"""
import os
import re
import sys
from importlib.machinery import SourceFileLoader

irl = SourceFileLoader("IRLine", f"{os.path.dirname(__file__)}/IRLine.py").load_module()
ast = SourceFileLoader("AST_builder", f"{os.path.dirname(__file__)}/../frontend/AST_builder.py").load_module()

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

            # End of function wrapper
            lines.append("}")

            # NOTE: 'labelDigit' should be the newest and unused digit
            returnDigit = labelDigit

            self.IR = lines

        return self.IR

    def __str__(self):
        return "\n".join([str(x) for x in self.IR]) + "\n"

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

    lines.append(f"{func_name} ({params[:-1]})")
    lines.append("{")
    if func_type != "void":
        lines.append(f"{''.join([x.name for x in function_tuple[0].children[0].children if x.name in ['signed', 'unsigned']])}{' ' if [x.name for x in function_tuple[0].children[0].children if x.name in ['signed', 'unsigned']] else ''}{func_type} D.{returnDigit};")

    return lines

def returnLines(node,returnDigit,labelDigit,successDigit=None,failureDigit=None, prefix=""):
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
            # lines.append(f"{prefix}{{")
            prefix += "  "
            for x in il: lines.append(f"{prefix}{' '.join([y.name for y in x.children[0].children])}{' ' if [y.name for y in x.children[0].children] else ''}{x.children[0].name} {x.children[1].name};")
            lines.append("")

    for element in node.children:
        try:
            splits = [["+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "|=", "&=", "^=", "<=", ">=", "="],["for"],["body"],["branch"],["return"],["call"],["while", "do_while"],["break"],["continue"],["goto"],["label"], ["++", "--"]]
            ind = [splits.index(x) for x in splits if element.name in x]
            ind = ind[0]
            if ind == 0:

                line = irl.IRLine(element, tvs=[], labelList=[labelDigit], prefix=prefix)
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
                        lines.append(f"{prefix}{{")
                        ns = True
                    tmp, labelDigit = returnLines(initNode, returnDigit, labelDigit, prefix=prefix[:-2])
                    for x in tmp: lines.append(f"{prefix}{x}")

                if ns:
                    prefix += "  "

                # Keep track of label for conditional block (if conditional exist)
                conditionLabel = None
                if element.children[1].children != []:

                    # Append an IRGoTo node
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRGoTo(f"<D.{labelDigit}>"))
                    lines.append(entry)

                    conditionLabel = labelDigit
                    labelDigit += 1

                # Append an IRJump node for the label that belongs to the start of the loop
                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRJump(f"<D.{labelDigit}>"))
                lines.append(entry)

                # Assign labels for start/end of loop
                loopStart = labelDigit
                loopEnd = labelDigit + 1
                labelDigit += 2

                # recursivly deal with the body of the loop
                tmp, labelDigit = returnLines(element.children[3], returnDigit, labelDigit, loopStart, loopEnd)
                for x in tmp: lines.append(f"{prefix}{x}")

                # Add the "end-of-loop" assignment/arithmetic
                if element.children[2].children != []:
                    initNode = ast.ASTNode("tmp", None)
                    initNode.children.append(element.children[2])
                    tmp, labelDigit = returnLines(initNode, returnDigit, labelDigit)
                    for x in tmp: lines.append(f"{prefix}{x}")

                # Start of conditionals for the loop
                if conditionLabel != None:
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRJump(f"<D.{conditionLabel}>"))
                    lines.append(entry)

                    tmpNode = element.children[1]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[1])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                    line = irl.IRLine(tmpNode, tvs=[], success=loopStart, failure=loopEnd, labelList=[labelDigit], prefix=prefix)
                    tvs, labelList = line.retrieve()
                    lines.append(line)

                    if labelList != []:
                        labelDigit = labelList[-1]


                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRJump(f"<D.{loopEnd}>"))
                    lines.append(entry)

                else:
                    # No conditional (jump to start of body...always True)
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRGoTo(f"<D.{loopStart}>"))
                    lines.append(entry)

                # increment twice for new index
                labelDigit += 2

                if ns:
                    prefix = prefix[:-2]
                    lines.append(f"{prefix}}}")
                pass

            elif ind == 2:
                tmp, labelDigit = returnLines(element, returnDigit, labelDigit, successDigit, failureDigit, prefix)
                lines.append(f"{prefix}{{")
                for x in tmp: lines.append(f"{prefix}{x}")
                lines.append(f"{prefix}}}")

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
                            lines.append(f"{prefix}{{")
                            prefix += "  "
                            ns = True

                        #Get lines for the body and assign new labeldigit
                        tmp, labelDigit = returnLines(case.children[0], returnDigit, labelDigit, success_label, failure_label)
                        for x in tmp: lines.append(f"{prefix}{x}")

                        if ns:
                            prefix = prefix[:-2]
                            lines.append(f"{prefix}}}")
                        break

                    tmpNode = case.children[0]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(case.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                    #break down argument for if statement into smaller if statements
                    line = irl.IRLine(tmpNode, tvs=[], success=success_label, failure=failure_label, labelList=[labelDigit], prefix=prefix)
                    tvs, labelList = line.retrieve()
                    lines.append(line)

                    if labelList != []:
                        labelDigit = labelList[-1] + 1


                    #Add goto for body statement
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRJump(f"<D.{success_label}>"))
                    lines.append(entry)
                    
                    if [x.children[0] for x in case.children[1].children if x.name == "=" and x.children[0].children[0].name in ["auto", "long double", "double", "float", "long long", "long long int", "long", "int", "short", "char"]]:
                        lines.append(f"{prefix}{{")
                        prefix += "  "
                        ns = True
                    #Get lines for the if body and assign new labeldigit
                    tmp, labelDigit = returnLines(case.children[1], returnDigit,  labelDigit, success_label, failure_label)

                    for x in tmp: lines.append(f"{prefix}{x}")

                    if ns:
                        prefix = prefix[:-2]
                        lines.append(f"{prefix}}}")

                    #append goto for end of if body
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRGoTo(f"<D.{labelDigit}>"))
                    lines.append(entry)

                    end_if.append(labelDigit)
                    labelDigit += 1

                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRJump(f"<D.{failure_label}>"))
                    lines.append(entry)

                for i in end_if:
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRJump(f"<D.{i}>"))
                    lines.append(entry)

            elif ind == 4:
                #Return

                # If returns some type of arithmetic expression, breaks it down.
                if len(element.children) > 0 and element.children[0].children != []:
                    line = irl.IRLine(element.children[0], tvs=[], labelList=[labelDigit], prefix=prefix)
                    tvs, labelList = line.retrieve()
                    lines.append(line)

                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRAssignment(f"D.{returnDigit}", f"{tvs[-1]}"))
                    lines.append(entry)

                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRReturn(f"D.{returnDigit}"))
                    lines.append(entry)

                    if labelList != []:
                        labelDigit = labelList[-1]

                elif len(element.children) > 0 and element.children[0].children == []:
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRAssignment(f"D.{returnDigit}", f"{element.children[0].name}"))
                    lines.append(entry)

                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRReturn(f"D.{returnDigit}"))
                    lines.append(entry)

                # Returns nothing
                else:
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRReturn(None))
                    lines.append(entry)

            elif ind == 5:
                #Function Call
                func_call = element.children[0].name

                # function call has parameters
                if element.children[0] != []:
                    line = irl.IRLine(element.children[0], tvs=[], labelList=[labelDigit], prefix=prefix)
                    tvs, labelList = line.retrieve()
                    lines.append(line)

                    if labelList != []:
                        labelDigit = labelList[-1] + 1

                # no parameters
                else:
                    # Append Empty function call node
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRFunctionCall(func_call, None))
                    lines.append(entry)

            elif ind == 6:
                #While and Do While

                ns = False

                # Jump straight to conditionals for only 'While' statements
                if element.name == "while":
                    entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                    entry.treeList.append(irl.IRGoTo(f"<D.{labelDigit}>"))
                    lines.append(entry)

                # Keep track of label for conditional block
                conditionLabel = labelDigit
                labelDigit += 1

                # Add the label that belongs to the start of the loop
                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRJump(f"<D.{labelDigit}>"))
                lines.append(entry)

                if [x.children[0] for x in element.children[1].children if x.name == "=" and x.children[0].children[0].name in ["auto", "long double", "double", "float", "long long", "long long int", "long", "int", "short", "char"]]:
                        lines.append(f"{prefix}{{")
                        prefix += "  "
                        ns = True

                # Assign labels for start/end of loop
                loopStart = labelDigit
                loopEnd = labelDigit + 1
                labelDigit += 2

                # recursivly deal with the body of the loop
                tmp, labelDigit = returnLines(element.children[1], returnDigit, labelDigit, loopStart, loopEnd)
                for x in tmp: lines.append(f"{prefix}{x}")

                if ns:
                    prefix = prefix[:-2]
                    lines.append(f"{prefix}}}")

                # Start of conditionals for the loop
                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRJump(f"<D.{conditionLabel}>"))
                lines.append(entry)

                tmpNode = element.children[0]
                if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                line = irl.IRLine(tmpNode, tvs=[], success=loopStart, failure=loopEnd, labelList=[labelDigit], prefix=prefix)
                tvs, labelList = line.retrieve()
                lines.append(line)

                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRJump(f"<D.{loopEnd}>"))
                lines.append(entry)

                if labelList != []:
                    labelDigit = labelList[-1]
                # increment twice for new index (twce, in case it was a do while)
                labelDigit += 2

            elif ind == 7:
                # Break
                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRGoTo(f"<D.{failureDigit}>"))
                lines.append(entry)

            elif ind == 8:
                # Continue
                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRGoTo(f"<D.{successDigit}>"))
                lines.append(entry)

            elif ind == 9:
                # Goto
                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRGoTo(f"{element.children[0].name}"))
                lines.append(entry)
            elif ind == 10:
                # Jump Label
                entry = irl.IRLine(node=None, tvs=[], labelList=[labelDigit], prefix=prefix)
                entry.treeList.append(irl.IRJump(f"{element.children[0].name}"))
                lines.append(entry)
                
                if (len(element.children) > 1):
                    temp_lines, labelDigit = returnLines(element.children[1], returnDigit, labelDigit)
                    lines.extend(temp_lines)

            elif ind == 11:
                # Special assignment? (++, --)
                line = irl.IRLine(element, tvs=[], prefix=prefix)
                tvs, labelList = line.retrieve()
                lines.append(line)

            else:
                print("Unsupported at this time")

        except Warning:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass

    lines.append("")
    return lines, labelDigit
