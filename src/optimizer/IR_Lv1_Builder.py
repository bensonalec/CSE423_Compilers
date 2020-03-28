import re
import sys
import importlib

simp = importlib.import_module("simplify", __name__)
ast = importlib.import_module("AST_builder", __name__)

class LevelOneIR():
    def __init__(self,astHead,symTable):
        self.astHead = astHead
        self.symTable = symTable
        self.IR = []

    def construct(self):

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
        return "\n".join(self.IR) + "\n"

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
                tmp, tvs, labelList = simp.breakdownExpression(element, tvs=[], labelList=[labelDigit])
                for x in tmp: lines.append(f"{prefix}{x}")
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
                    lines.append(f"{prefix}goto <D.{labelDigit}>;")
                    conditionLabel = labelDigit
                    labelDigit += 1

                # Add the label that belongs to the start of the loop
                lines.append(f"{prefix}<D.{labelDigit}>:")

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
                    lines.append(f"{prefix}<D.{conditionLabel}>:")
                    # TODO: Create tempoary AST if its a unary logical comparison
                    tmpNode = element.children[1]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[1])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))
                    tmp, tvs, labelList = simp.breakdownExpression(tmpNode, tvs=[], success=loopStart, failure=loopEnd, labelList=[labelDigit])
                    for x in tmp: lines.append(f"{prefix}{x}")
                    lines.append(f"{prefix}<D.{loopEnd}>:")
                    if labelList != []:
                        labelDigit = labelList[-1]
                else:
                    # No conditional (jump to start of body...always True)
                    lines.append(f"{prefix}goto <D.{loopStart}>;")

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

                    # TODO: Create tempoary AST if its a unary logical comparison
                    tmpNode = case.children[0]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(case.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                    #break down argument for if statement into smaller if statements
                    temp_lines, tvs, labelList = simp.breakdownExpression(tmpNode, tvs=[], success=success_label, failure=failure_label, labelList=[labelDigit])

                    if labelList != []:
                        labelDigit = labelList[-1] + 1

                    #adds broken down if statement
                    for x in temp_lines: lines.append(f"{prefix}{x}")

                    #Add goto for body statement
                    lines.append(f"{prefix}<D.{success_label}>:")
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
                    lines.append(f'{prefix}goto <D.{labelDigit}>;')
                    end_if.append(labelDigit)
                    labelDigit += 1

                    lines.append(f"{prefix}<D.{failure_label}>:")

                for i in end_if:
                    lines.append(f'{prefix}<D.{i}>:')

            elif ind == 4:
                #Return

                # If returns some type of arithmetic expression, breaks it down.
                if len(element.children) > 0 and element.children[0].children != []:
                    tmp, tvs, labelList = simp.breakdownExpression(element.children[0], tvs=[], labelList=[labelDigit])
                    for x in tmp: lines.append(f"{prefix}{x}")
                    lines.append(f"{prefix}D.{returnDigit} = {tvs[-1]};")
                    lines.append(f"{prefix}return D.{returnDigit};")
                    if labelList != []:
                        labelDigit = labelList[-1]

                elif len(element.children) > 0 and element.children[0].children == []:
                    lines.append(f"{prefix}D.{returnDigit} = {element.children[0].name};")
                    lines.append(f"{prefix}return D.{returnDigit};")

                # Returns nothing
                else:
                    lines.append(f"{prefix}return;")

            elif ind == 5:
                #Function Call
                func_call = element.children[0].name

                # function call has parameters
                if element.children[0] != []:
                    tmp, tvs, labelList = simp.breakdownExpression(element, tvs=[], labelList=[labelDigit])
                    tmp[-1] = tmp[-1].split(' = ')[1]
                    for x in tmp: lines.append(f"{prefix}{x}")
                    if labelList != []:
                        labelDigit = labelList[-1] + 1

                # no parameters
                else:
                    lines.append(f"{prefix}{func_call}();")

            elif ind == 6:
                #While and Do While

                ns = False

                # Jump straight to conditionals for only 'While' statements
                if element.name == "while":
                    lines.append(f"{prefix}goto <D.{labelDigit}>;")

                # Keep track of label for conditional block
                conditionLabel = labelDigit
                labelDigit += 1

                # Add the label that belongs to the start of the loop
                lines.append(f"{prefix}<D.{labelDigit}>:")

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
                lines.append(f"{prefix}<D.{conditionLabel}>:")
                # TODO: Create tempoary AST if its a unary logical comparison
                tmpNode = element.children[0]
                if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))
                tmp, tvs, labelList = simp.breakdownExpression(tmpNode, tvs=[], success=loopStart, failure=loopEnd, labelList=[labelDigit])

                for x in tmp: lines.append(f"{prefix}{x}")
                lines.append(f"{prefix}<D.{loopEnd}>:")

                if labelList != []:
                    labelDigit = labelList[-1]
                # increment twice for new index (twce, in case it was a do while)
                labelDigit += 2

            elif ind == 7:
                # Break
                lines.append(f"{prefix}goto <D.{failureDigit}>;")

            elif ind == 8:
                # Continue
                lines.append(f"{prefix}goto <D.{successDigit}>;")

            elif ind == 9:
                lines.append(f"goto {element.children[0].name}")
            elif ind == 10:
                lines.append(f"{element.children[0].name}:")
                if (len(element.children) > 1):
                    temp_lines, labelDigit = returnLines(element.children[1], returnDigit, labelDigit)
                    lines.extend(temp_lines)

            elif ind == 11:
                tmp, tvs, labelList_ = simp.breakdownExpression(element, tvs=[])
                for x in tmp: lines.append(f"{prefix}{x}")
            else:
                print("Unsupported at this time")

        except Warning:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass

    lines.append("")
    return lines, labelDigit
