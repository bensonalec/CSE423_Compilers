import re
import sys

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

        # list of all bodies within functions in our C program
        for x in self.astHead.children:
            if x.name == "func":
                bodyList.append((x.children[1].name,x.children[3]))

        returnDigit = 1234
        for i in bodyList:
            for x in returnLines(i[1], returnDigit):
                print(x)
            returnDigit += 1

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

def returnLines(node,returnDigit):
    lines = []
    for element in node.children:
        #try:
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

            #move this eventually



            end_if = []



            for i in element.children:

                if i.name == "default":
                    lines.append(returnLines(i.children[0],returnDigit))
                    continue

                lines, returnDigit = breakdownBoolean(i, returnDigit, "SUCCESS", "FAILURE")

                # cases = []
                # syms = []
                # temp = i
                # while(temp.children[0].name == "&&" or temp.children[0].name == "||"):
                #     syms.append(temp.children[0])
                #     cases.append(temp.children[1])
                #     temp = temp.children[0]
                # for k in temp.children:
                #     cases.append(k)

                # tmp_lab = []
                # for ind, case in enumerate(cases[::-1]):

                #     if case.name == "body":
                #         continue

                #     if ind == 0:
                #         cur_opp = syms.pop()
                #         next_opp = cur_opp
                #     else:
                #         cur_opp = next_opp
                #         if syms != []:
                #             next_opp = syms.pop()
                #         else:
                #             next_opp = None

                #     print(f'Case = {case.name}')
                #     print(f'Cur_op = {cur_opp.name}')
                #     if next_opp:
                #         print(f'Next_op = {next_opp.name}')
                #     else: 
                #         print(f'Next_op = None')


                #     temp_label1 = f'<D.{returnDigit}>'
                #     returnDigit += 1
                #     temp_label2 = f'<D.{returnDigit}>'
                #     returnDigit += 1

                #     print('asdfasd')
                #     print(case.children[1].name)

                #     asdf, returnDigit = breakdownExpression(case.children[1], returnDigit, "foo", "bar")

                #     # print("STAR")
                #     # for i in asdf:
                #     #     print(i)
                #     # print("SDF")


                #     if cur_opp.name == "&&" and not next_opp == None:
                #         if next_opp.name == "||":
                #             lines.append(f'if ({build_case(case)}) goto {temp_label2}; else goto {temp_label1}')
                #             lines.append(f'{temp_label1}:')
                #             tmp_lab.append(temp_label2)
                #         else:
                #             lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                #             lines.append(f'{temp_label1}:')
                #             tmp_lab.append(temp_label2)
                #     elif cur_opp.name == "||" and not next_opp == None:
                #         if next_opp.name == "&&":
                #             lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                #             lines.append(f'{temp_label1}:')
                #             tmp_lab.append(temp_label2)                           
                #         else:
                #             lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                #             lines.append(f'{temp_label2}:')
                #             tmp_lab.append(temp_label1)
                #     else:
                #         #this is the last operation
                #         if cur_opp.name == "&&":
                #                 lines.append(f'if ({build_case(case)}) goto success; else goto false')  
                #         elif cur_opp.name == "||":
                #                 lines.append(f'if ({build_case(case)}) goto success; else goto fail')                                                          

                #     if next_opp == None or next_opp.name != cur_opp.name:
                #         save = []
                #         if next_opp == None and tmp_lab != []: 

                            
                #             for i in lines:
                #                 for j in tmp_lab:
                #                     if j in i:
                #                         if cur_opp.name == "||":
                #                             lines[lines.index(i)] = i.replace(j, "success")
                #                         else:
                #                             lines[lines.index(i)] = i.replace(j, "false") 

                #         else:
                #             if tmp_lab != []: 
                #                 save.append(tmp_lab.pop())
                #             for i in tmp_lab:
                #                 lines.append(f'{i}:')

                #             tmp_lab = save

                    # end_if.append(f'<D.{returnDigit}>')
                    # returnDigit += 1                    
                    # #create if gimple statement with gotos
                    # lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                    # #label 1:
                    # lines.append(f'{temp_label1}:')

                    #work on body later
                    #Body
                    # lines.append(returnLines(case.children[1],returnDigit))
                    # #add goto here to skip over other statements
                    # lines.append(f'goto {end_if[-1]};')
                    # #label 2:
                    # lines.append(f'{temp_label2}:')
            for i in end_if:
                lines.append(f'{i}:')

                

        elif ind == 4: 
            #Return

            # If returns some type of arithmetic expression, breaks it down.
            if len(element.children) > 0:
                lines += breakdownArithmetic(element.children[0], f"D.{returnDigit}")
                lines.append(f"return D.{returnDigit};") 
            
            # Returns nothing
            else:
                lines.append(f"return;") 

        elif ind == 5:
            #Function Call
            func_call = element.children[0].name

            # function call has parameters
            if func_call.children != []:
                lines += breakdownArithmetic(func_call.children[0], f"D.{returnDigit}")
                lines.append(f"{func_call.name}(D.{returnDigit});")
                returnDigit += 1
            
            # no parameters
            else:
                lines.append(f"{func_call.name}();")

        elif ind == 6:
            print("While and do while")
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

        # except Exception as err:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     print(exc_type, exc_tb.tb_lineno)
        #     pass
    
    return lines

def build_case(node):
    #does not handle complex booleans.

    #first node is the opperator
    opp = node.name

    #next find first arguement
    if node.children[0].name == "var" or node.children[0].name == "call":
        first_arg = node.children[0].children[0].name
    else:
        first_arg = node.children[0].name

    #next find second arguement
    if node.children[1].name == "var" or node.children[1].name == "call":
        second_arg = node.children[1].name
    else:
        second_arg = node.children[1].name

    return f'{first_arg} {opp} {second_arg}'


def breakdownBoolean(root, returnDigit, success_label, failure_label):

    #NOTE root needs to be the parent of the first "&&" or "||"

    cases = []
    syms = []
    lines = []
    while(root.children[0].name == "&&" or root.children[0].name == "||"):
        syms.append(root.children[0])
        cases.append(root.children[1])
        root = root.children[0]
    for k in root.children:
        cases.append(k)

    tmp_lab = []
    for ind, case in enumerate(cases[::-1]):

        if case.name == "body":
            continue

        if ind == 0:
            cur_opp = syms.pop()
            next_opp = cur_opp
        else:
            cur_opp = next_opp
            if syms != []:
                next_opp = syms.pop()
            else:
                next_opp = None


        temp_label1 = f'<D.{returnDigit}>'
        returnDigit += 1
        temp_label2 = f'<D.{returnDigit}>'
        returnDigit += 1

        # print('asdfasd')
        # print(case.children[1].name)

        # asdf, returnDigit = breakdownExpression(case.children[1], returnDigit, "foo", "bar")

        # print("STAR")
        # for i in asdf:
        #     print(i)
        # print("SDF")


        if cur_opp.name == "&&" and not next_opp == None:
            if next_opp.name == "||":
                lines.append(f'if ({build_case(case)}) goto {temp_label2}; else goto {temp_label1}')
                lines.append(f'{temp_label1}:')
                tmp_lab.append(temp_label2)
            else:
                lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                lines.append(f'{temp_label1}:')
                tmp_lab.append(temp_label2)
        elif cur_opp.name == "||" and not next_opp == None:
            if next_opp.name == "&&":
                lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                lines.append(f'{temp_label1}:')
                tmp_lab.append(temp_label2)                           
            else:
                lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                lines.append(f'{temp_label2}:')
                tmp_lab.append(temp_label1)
        else:
            #this is the last operation
            if cur_opp.name == "&&":
                    lines.append(f'if ({build_case(case)}) goto {success_label}; else goto {failure_label}')  
            elif cur_opp.name == "||":
                    lines.append(f'if ({build_case(case)}) goto {success_label}; else goto {failure_label}')                                                          

        if next_opp == None or next_opp.name != cur_opp.name:
            save = []
            if next_opp == None and tmp_lab != []: 

                
                for i in lines:
                    for j in tmp_lab:
                        if j in i:
                            if cur_opp.name == "||":
                                lines[lines.index(i)] = i.replace(j, f'{success_label}:')
                            else:
                                lines[lines.index(i)] = i.replace(j, f'{failure_label}:') 

            else:
                if tmp_lab != []: 
                    save.append(tmp_lab.pop())
                for i in tmp_lab:
                    lines.append(f'{i}:')

                tmp_lab = save

    return lines, returnDigit
def breakdownArithmetic(root, varName):
    ntv = [root]

    isOp = r'^(\+|\-|\/|\*|\%)$'
    opCheck = re.compile(isOp)
    Stack = []

    lines = []
    lastVarName = 0
    
    # fill up stack with all operands / operations 
    while ntv != []:
        cur = ntv[0]
        Stack.append(cur.name)

        # Beginning of function call parameters
        if cur.parent.name == 'call':
            
            # params exist
            if cur.children != []:
                lines += breakdownArithmetic(cur.children[0], varName)

                #remove params so they dont get added to Stack
                ntv[0].children = []

                Stack.append(varName) #tmp variable (should be some 'D.xxxx' variable eventually?)
            
            # params don't exist
            else:
                Stack.append('')

        ntv = [x for x in cur.children] + ntv[1:]

    last = len(Stack)
    for i in Stack[::-1]:
        ind = last- 1
        
        if(opCheck.match(i)):

            # two operands
            v1 = Stack[ind+1]
            v2 = Stack[ind+2]

            # append the operation
            #lines.append(f"_{lastVarName} = {v1} {i} {v2};")
            lines.append(f"{varName} = {v1} {i} {v2};")

            # modify the stack to get rid of operands but keep new tmp variable
            #Stack = Stack[:ind] + [f"_{lastVarName}"] + Stack[ind+3:]
            Stack = Stack[:ind] + [f"{varName}"] + Stack[ind+3:]

            # increment tmp variable for IR
            lastVarName += 1

        elif(i == "var"):

            # modify stack to get rid of 'var'
            Stack = Stack[:ind] + Stack[ind+1:]

        elif(i == "call"):

            # modify function name to include parameter tmp variable
            Stack[ind+1] = Stack[ind+1] + f" ({Stack[ind+2]})"

            # modify stack to get rid of 'call'
            Stack = Stack[:ind] + Stack[ind+1:]

            # modify stack to get rid of parameter tmp variable
            Stack = Stack[:ind+1] + Stack[ind+2:]

        else:
            pass

        last -= 1

    # final assignment to the passed in variable
    lines.append(f"{varName} = {Stack[0]};")

    return lines



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
