import itertools
import importlib
import re

ast = importlib.import_module("AST_builder", __name__)

opt_level = 1

class LevelOneIR():
    def __init__(self,astHead,symTable):
        self.astHead = astHead
        self.symTable = symTable

    def construct(self):

        sym = self.symTable
        ntv = self.astHead

        varIndex = 0
        lastVarName = "_" + str(varIndex)
        bodyList = []
        all_lines = []

        # list of all bodies within functions in our C program
        for x in self.astHead.children:
            if x.name == "func":
                bodyList.append((x.children[1].name,x.children[3]))

        returnDigit = 1234
        for i in bodyList:
            tmp = returnLines(i[1], f"D.{returnDigit}")
            returnDigit = tmp[1] + 1
            all_lines += tmp[0]
            
            for x in tmp[0]:
                print (x)

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

def returnLines(node, returnVarName, lastLabelIndex = None):
    if lastLabelIndex == None:
        lastLabelIndex = int(returnVarName.split('.')[1])
    lines = []
    for element in node.children:
        splits = [["=","+="],["for"],["body"],["branch"],["return"],["call"],["while","do_while"],["break"],["continue"],["goto"],["label"]]
        ind = [splits.index(x) for x in splits if element.name in x]
        ind = ind[0]
        if ind == 0:
            #Assignment

            varName = element.children[0].children[0].name #temporary
            
            # Initialize variable (if needed)
            if len(element.children[0].children) > 1:
                varType = element.children[0].children[0].name
                varName = element.children[0].children[1].name
                lines.append(f"{varType} {varName};")

            # Breakdown arithmetic nodes
            lines += breakdownArithmetic(element.children[1], varName)

        elif ind == 1:
            print("For loop")
        elif ind == 2:
            print("Body")
        elif ind == 3:
            print("If")
        elif ind == 4: 
            #Return

            # It returns some type of arithmetic, break it down.
            # TODO: it currently breaks down single values like "return 1;"
            #       should I keep this? or test if it is "complicated" arithmetic?
            if len(element.children) > 0:
                lines += breakdownArithmetic(element.children[0], f"{returnVarName}")
                lines.append(f"return {returnVarName};") 
            
            # Returns nothing
            else:
                lines.append(f"return;") 

        elif ind == 5:
            #Function Call
            pass
        elif ind == 6:
            # While and Do While
            conditionLabel = None
            if element.name == "while":
                # Setup checking the condition first
                lastLabelIndex += 1;
                conditionLabel = lastLabelIndex
                lines.append(f"goto <D.{lastLabelIndex}>;")
            
            # Add the label that belongs to the start of the loop
            lastLabelIndex += 1;
            loopStart = lastLabelIndex
            lines.append(f"<D.{lastLabelIndex}>:")

            lastLabelIndex += 1;
            loopEnd = lastLabelIndex

            # recursivly deal with the body of the loop
            tmp, lastLabelIndex = returnLines(element.children[1], returnVarName, lastLabelIndex)
            lines.extend(tmp)
            lines.append(f"<D.{conditionLabel}>:")
            # tmp, lastLabelIndex = breakdownCollation(element.children[0], lastLabelIndex, loopStart, loopEnd)
            # lines.extend(tmp)
            tmp, lastLabelIndex = breakdownExpression(element.children[0], lastLabelIndex, loopStart, loopEnd)
            lines.extend(tmp)
            lines.append(f"<D.{loopEnd}>:")

        elif ind == 7:
            print("Break")
        elif ind == 8:
            print("Continue")
        elif ind == 9:
            print("Goto")
        elif ind == 10:
            print("Label")
        else:
            print("Unsupported at this time")
    
    return lines, lastLabelIndex

def breakdownArithmetic(root, varName):
    spec_ops = ["++", "--"]
    ops = ["+", "-", "*", "/", "%", "<<", ">>", "!", "~"]

    lines = []
    Stack = []
    
    ntv = [root]

    while ntv != []:
        c = ntv[0]

        Stack.append(c.name)
        
        e = c.children

        ntv = e + ntv[1:]

    lastVarName = 0

    last = len(Stack)
    for i in Stack[::-1]:
        ind = last - 1
        if i in spec_ops:
            order = 1 ^ (Stack[ind + 1 : ind + 2].index("NULL"))

            lastVarName += 1
            lines.append(f"_{lastVarName} = {Stack[ind+1:ind+2][order]}")
            lines.insert(-1 - order, f"{Stack[ind+1:ind+2][order]} = {Stack[ind+1:ind+2][order]} {i[0]} 1")
        elif i in ops:

            # two operands
            v1 = Stack[ind+1]
            v2 = Stack[ind+2]

            # append the operation
            lines.append(f"_{lastVarName} = {v1}{i}{v2}")

            # modify the stack to get rid of operands but keep new tmp variable
            Stack = Stack[:ind] + [f"_{lastVarName}"] + Stack[ind+3:]

            # increment tmp variable for IR
            lastVarName += 1

        elif i == "var":

            # modify stack to get rid of 'var'
            Stack = Stack[:ind] + Stack[ind+1:]

        elif i == "call":

            # get name of function call
            call_name = Stack[ind+1]

            #TODO: NEED TO CAPTURE PARAMETERS
            Stack[ind+1] = call_name

            # modify stack to get rid of 'call'
            Stack = Stack[:ind] + Stack[ind+1:]

        else:
            pass

        last -= 1

    # final assignment to the passed in variable
    lines.append(f"{varName} = {Stack[0]}")

    return lines

def breakdownCollation(root, lastLabelIndex, successLabel, failureLabel):
    lines = []
    comp_ops = ["<=", "<", ">=", ">", "==", "!="]
    log_ops = ["||", "&&"]
    un_ops = ["!", "~", "call", "var"]

    successTemplate = "__SUCCESS__"
    failureTemplate = "__FAILURE__"

    cur = root
    stack = []
    ns = []

    while True:
        while cur != None:
            stack.append(cur)
            if cur.children != []:
                cur = cur.children[0]
            else:
                cur = None
        if stack == []:
            break
        cur = stack.pop()
        ns.append(cur)
        if len(cur.children) > 1:
            cur = cur.children[1]
        else:
            cur = None
    
    #ns = [x for x in ns if x.name in comp_ops or x.name in log_ops]
    ns = [x for x in ns if x.name in comp_ops or x.name in log_ops or x.name in un_ops]
    print ([x.name for x in ns])

    successLables = [successLabel]
    failureLables = [failureLabel]
    for i in ns:
        if i.name in comp_ops:
            left = breakdownArithmetic(i.children[0], "left")
            right = breakdownArithmetic(i.children[1], "right")

            if opt_level != 0:
                left[-1] = f"{left[-1].split(' ')[-1]}"
                right[-1] = f"{right[-1].split(' ')[-1]}"
            
                lines.extend(left[:-1])
                lines.extend(right[:-1])
            
            else:
                lines.extend(left)
                lines.extend(right)

            lines.append(f"if ({left[-1].split(' ')[0]} {i.name} {right[-1].split(' ')[0]}) {successTemplate} {failureTemplate}")
        elif i.name in log_ops:
            lines.append(failureTemplate)
            # lastLabelIndex += 1
            # successLables.append(lastLabelIndex)

            # lastLabelIndex += 1
            # failureLables.append(lastLabelIndex)

            # idx = log_ops.index(i.name)

            # if idx == 0:
            #     pass
            # elif idx == 1:
            #     pass
    print(lines)
    # for x in lines: print (x)
    # if len(root.children) == 1:
    #     tmp_root = simplifyBooleanLogic(root)
    #     lastLabelIndex += 1
    #     tmp, lastLabelIndex = breakdownCollation(tmp_root, lastLabelIndex, successLabel)

    #     for j, line in enumerate(tmp):
    #         line = line.replace(successTemplate, f"goto <D.{successLabel}>;")
    #         tmp[j] = line.replace(failureTemplate, f"goto <D.{lastLabelIndex}>;")

    #     return tmp, lastLabelIndex
    # elif len(root.children) == 2:
    #     idx = log_ops.index(root.name) if root.name in log_ops else -1

    #     if idx != -1:
    #         # TODO: Figure out whether this is the highest level or not
    #         # if its the highest use successLabel
    #         # else find the next label to use
    #         cond0, lastLabelIndex = breakdownCollation(root.children[0], lastLabelIndex, successLabel)
    #         lastLabelIndex += 1
    #         firstConditionLabel = lastLabelIndex
    #         cond1, lastLabelIndex = breakdownCollation(root.children[1], lastLabelIndex, successLabel)

    #         if idx == 0:
    #             for j, line in enumerate(cond0):
    #                 line = line.replace(successTemplate, f"goto <D.{successLabel}>;")
    #                 cond0[j] = line.replace(failureTemplate, f"goto <D.{firstConditionLabel}>;")
    #             for j, line in enumerate(cond1):
    #                 line = line.replace(successTemplate, f"goto <D.{successLabel}>;")
    #                 cond1[j] = line.replace(failureTemplate, f"goto <D.{lastLabelIndex}>;")
    #         elif idx == 1:
    #             lastLabelIndex += 1
    #             for j, line in enumerate(cond0):
    #                 line = line.replace(successTemplate, f"goto <D.{firstConditionLabel}>;")
    #                 cond0[j] = line.replace(failureTemplate, f"goto <D.{lastLabelIndex}>;")
    #             for j, line in enumerate(cond1):
    #                 line = line.replace(successTemplate, f"goto <D.{successLabel}>;")
    #                 cond1[j] = line.replace(failureTemplate, f"goto <D.{lastLabelIndex}>;")
            
    #         lines.extend(cond0)
    #         lines.append(f"<D.{firstConditionLabel}>:")
    #         lines.extend(cond1)
    #     else:
    #         if root.name in comp_ops:
    #             left = breakdownArithmetic(root.children[0], "left")
    #             right = breakdownArithmetic(root.children[1], "right")
                
    #             if opt_level != 0:
    #                 left[-1] = f"{left[-1].split(' ')[-1]}"
    #                 right[-1] = f"{right[-1].split(' ')[-1]}"
                
    #                 lines.extend(left[:-1])
    #                 lines.extend(right[:-1])
                
    #             else:
    #                 lines.extend(left)
    #                 lines.extend(right)

    #             lines.append(f"if ({left[-1].split(' ')[0]} {root.name} {right[-1].split(' ')[0]}) {successTemplate} {failureTemplate}")
    return lines, lastLabelIndex

def simplifyBooleanLogic(root):
    """
    This functions simplifies the given root (case) node by converting the names and arrangement of AST nodes.

    Example conversions:
                '!a' --> 'a == 0'
                '~a' --> 'a != -1'
                'a'  --> 'a != 0'
    
    """

    index = 0
    tmp_root = ast.ASTNode("", None)

    if root.name == "var":
        tmp_root.name = "!="
        tmp_root.children.append(root)
        tmp_root.children.append(ast.ASTNode("0", tmp_root))


    # # Iterating through the root node, should be a 'case' node.
    # for node in root.children:
    #     if node.name == "var":
    #         var_node = node
    #         root.children[index] = ast.ASTNode("!=", root)
    #         root.children[index].children.append(var_node)
    #         root.children[index].children.append(ast.ASTNode("0", node.children[0]))
    #         pass
    #     elif node.name == "!":
    #         var_node = node.children[0]
    #         root.children[index] = ast.ASTNode("==", root)
    #         root.children[index].children.append(var_node)
    #         root.children[index].children.append(ast.ASTNode("0", node.children[0]))
    #         pass
    #     elif node.name == "~":
    #         var_node = node.children[0]
    #         root.children[index] = ast.ASTNode("!=", root)
    #         root.children[index].children.append(var_node)
    #         root.children[index].children.append(ast.ASTNode("-1", node.children[0]))
    #         pass
    #     index += 1
    return tmp_root


def breakdownExpression(root, lastLabelIndex, successLabel, failureLabel):
    lines = []
    ns = []

    log_ops = ['||', '&&']
    comp_ops = ["<=", "<", ">=", ">", "==", "!="]
    arth_ops = ["+", "-", "*", "/", "%", "<<", ">>", "!", "~"]
    spec_ops = ["++", "--"]
    ass_ops = ["="]
    id_ops = ["var", "call"]
    ntv = [root]

    successStack = [successLabel]
    failureStack = [failureLabel]

    tvs = []

    while ntv != []:
        cur = ntv[-1]
        ns.insert(0, cur)
        ntv = ntv[:-1] + cur.children

    ns = [x for x in ns if x.name in log_ops or x.name in comp_ops or x.name in arth_ops or x.name in spec_ops or x.name in ass_ops or x.name in id_ops]

    print ([x.name for x in ns])

    for node in ns:
        if node.name in log_ops:

            #ifs = [(x, idx) for idx, x in enumerate(lines) if x.startswith("if") and "__SUCCESS__" in x][-2:]

            index = log_ops.index(node.name)
            # print(ifs)
            if index == 0:
                lastLabelIndex += 1
                # print("LAST::::",lastLabelIndex)

                failureStack.append(lastLabelIndex)

                # for line in ifs:
                    # # tmp = line[0].replace("__SUCCESS__", f"goto <D.{successStack.pop() if len(successStack) > 1 else successStack[0]}>;")
                    # # lines[line[1]] = tmp.replace("__FAILURE__", f"else goto <D.{failureStack.pop() if len(failureStack) > 1 else failureStack[0]}>;")
# 
                # lines.insert(ifs[-1][1]-1, "__FAILURE__")

            if index == 1:
                lastLabelIndex += 1
                # print("LAST::::",lastLabelIndex)
                successStack.append(lastLabelIndex)

                # for line in ifs:
                    # # tmp = line[0].replace("__SUCCESS__", f"goto <D.{successStack.pop() if len(successStack) > 1 else successStack[0]}>;")
                    # # lines[line[1]] = tmp.replace("__FAILURE__", f"else goto <D.{failureStack.pop() if len(failureStack) > 1 else failureStack[0]}>;")
# 
                # ifs[-1][1]
                # starting at the above, iterate backwards
                # for back in range(ifs[-1][1]-1,0,-1):
                    # if line starts with if, break
                    # if(lines[back].startswith("if")):
                        # lines.insert(back+1,"__SUCCESS__")
                        # break
#                lines.insert(ifs[-1][1], f"<D.{lastLabelIndex}>:")


            # for line in ifs:
            #     tmp = line[0].replace("__SUCCESS__", "THIS IS A TEST")
            #     lines[line[1]] = tmp.replace("__FAILURE__", "THIS IS A TEST FAIL")
            # print (ifs)
        elif node.name in comp_ops:
            ops = [tvs.pop() for x in node.children if len(x.children) != 0]
            if ops == [] and len(node.children) > 1:
                lines.append(f"if ({node.children[0].name} {node.name} {node.children[1].name}) __SUCCESS__ __FAILURE__")
            elif len(ops) == 2:
                lines.append(f"if ({ops[1]} {node.name} {ops[0]}) __SUCCESS__ __FAILURE__")
            else:
                pos = [node.children.index(x) for x in node.children if len(x.children) != 0 and len(node.children) > 1]

                if pos == [0]:
                    lines.append(f"if ({ops[0]} {node.name} {node.children[1].name}) __SUCCESS__ __FAILURE__")
                elif pos == [1]:
                    lines.append(f"if ({node.children[0].name} {node.name} {ops[0]}) __SUCCESS__ __FAILURE__")
        elif node.name in arth_ops:
            ops = [tvs.pop() for x in node.children if len(x.children) != 0]

            # Case 1: ops is empty
            if ops == [] and len(node.children) > 1:
                lines.append(f"_{len(tvs)} = {node.children[0].name} {node.name} {node.children[1].name}")
            # Case 2: two elem in ops
            elif len(ops) == 2:
                lines.append(f"_{len(tvs)} = {ops[0]} {node.name} {ops[1]}")
            else:
                pos = [node.children.index(x) for x in node.children if len(x.children) != 0 and len(node.children) > 1]

                # Case 3: one elem in ops but its the left element in the operation
                if pos == [0]:
                    lines.append(f"_{len(tvs)} = {ops[0]} {node.name} {node.children[1].name}")
                # Case 4: one elem in ops but its the right element in the operation
                elif pos == [1]:
                    lines.append(f"_{len(tvs)} = {node.children[0].name} {node.name} {ops[0]}")
                # Case 5: Its a unary operator
                elif pos == []:
                    lines.append(f"_{len(tvs)} = {node.name}{ops[0] if ops != [] else node.children[0].name}")
            
            tvs.append(f"_{len(tvs)}")
        elif node.name in spec_ops:
            pass
            # TODO: fix it so it works 
            # order = 1 ^ (Stack[ind + 1 : ind + 2].index("NULL"))

            # lastVarName += 1
            # lines.append(f"_{lastVarName} = {Stack[ind+1:ind+2][order]}")
            # lines.insert(-1 - order, f"{Stack[ind+1:ind+2][order]} = {Stack[ind+1:ind+2][order]} {i[0]} 1")
        elif node.name in ass_ops:
            pass
        elif node.name in id_ops:
            tvs.append(node.children[0].name)

    while tvs != []:
        lines.append(f"if ({tvs.pop()} != 0) __SUCCESS__ __FAILURE__")

    print(successStack)
    for x in lines: print(type(x))
    op_list = [x for x in ns if x.name in log_ops]
    for node in op_list[::-1]:
        ifs = [(x, idx) for idx, x in enumerate(lines) if x.startswith("if") and "__SUCCESS__" in x][0]
        print(ifs[0])
        index = log_ops.index(node.name)

        if index == 0:
            del op_list[-1]
            tmp = ifs[0].replace("__SUCCESS__", f" goto <D.{successLabel if len(op_list) == 0 else successStack.pop(0) }>;")
            tmp_index = failureLabel if len(op_list) == 0 else failureStack.pop()
            tmp = tmp.replace("__FAILURE__", f"goto <D.{tmp_index}>;")
            lines[ifs[1]] = tmp
            lines.insert(ifs[1]+1, f"<D.{tmp_index}>:")
            
        if index == 1:
            del op_list[-1]
            tmp_index = successLabel if len(op_list) != 0 else  successStack.pop()
            tmp = ifs[0].replace("__SUCCESS__", f" goto <D.{tmp_index}>;")
            lines.insert(ifs[1]+1,f"<D.{tmp_index}>;")
            tmp = tmp.replace("__FAILURE__", f"goto <D.{failureLabel if len(op_list) == 0 else failureStack.pop() }>;")
            lines[ifs[1]] = tmp
            
    ifs = [(x, idx) for idx, x in enumerate(lines) if x.startswith("if") and "__SUCCESS__" in x][0]
    tmp = ifs[0].replace("__SUCCESS__", f" goto <D.{successLabel}>;")
    tmp = tmp.replace("__FAILURE__", f"goto <D.{failureLabel}>;")
    lines[ifs[1]] = tmp
    return lines, lastLabelIndex
