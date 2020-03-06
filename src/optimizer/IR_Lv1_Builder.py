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
        labelDigit = returnDigit + 1
        for i in bodyList:
            lines , labelDigit = returnLines(i[1], returnDigit, labelDigit)
            for x in lines:
                print(x)
            returnDigit = labelDigit + 1

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

def returnLines(node,returnDigit,labelDigit):
    lines = []
    for element in node.children:
        try:
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
                # If/Else statement(s)

                # list of goto labels to be appended at end of if blocks
                end_if = []

                #for each case in a branch
                for case in element.children:
                    
                    #default is an 'else'. Only has one child, body
                    if case.name == "default":
                        #Get lines for the body and assign new labeldigit
                        tmp, labelDigit = returnLines(case.children[0],returnDigit, labelDigit)
                        lines.extend(tmp)
                        continue

                    #create label for body if true and label to skip to correct place if false.
                    success_label = f'<D.{labelDigit}>'
                    labelDigit += 1
                    failure_label = f'<D.{labelDigit}>'
                    labelDigit += 1

                    #break down argument for if statement into smaller if statements
                    temp_lines, labelDigit = breakdownBoolean(case, labelDigit, success_label, failure_label)
                    
                    #adds broken down if statement
                    lines.extend(temp_lines)
                    
                    #Add goto for body statement
                    lines.append(success_label)

                    #Get lines for the if body and assign new labeldigit
                    tmp, labelDigit = returnLines(case.children[1],returnDigit, labelDigit)
                    lines.extend(tmp)

                    #append goto for end of if body
                    lines.append(f'goto <D.{labelDigit}>;')
                    end_if.append(f'<D.{labelDigit}>')
                    labelDigit += 1

                    lines.append(f"{failure_label}:")

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
                    lines += breakdownArithmetic(func_call.children[0], f"D.{labelDigit}")
                    lines.append(f"{func_call.name}(D.{labelDigit});")
                    returnDigit += labelDigit
                
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

        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass
    
    return lines, labelDigit

def build_case(node):
    #builds argement to go in gimple string

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


def breakdownBoolean(root, labelDigit, success_label, failure_label):

    #NOTE root needs to be the parent of the first "&&" or "||"

    #list of individual conditionals
    conds = []

    #an array of symbols
    syms = []
    lines = []
    while(root.children[0].name == "&&" or root.children[0].name == "||"):
        syms.append(root.children[0])
        conds.append(root.children[1])
        root = root.children[0]
    for k in root.children:
        conds.append(k)

    #conds = conds[1:]
    tmp_lab = []

    for ind, case in enumerate(conds[::-1]):
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

        temp_label1 = f'<D.{labelDigit}>'
        labelDigit += 1
        temp_label2 = f'<D.{labelDigit}>'
        labelDigit += 1

        if len(case.children) != 1:

            declare, labelDigit = breakdownExpression(case.children[1], labelDigit, "foo", "bar")
            #declare is a list of returned arithmetic lines.

            if declare != []:

                #add declarations before
                lines.extend(declare)

                #replace operator with created variable name
                arg = build_case(case)
                arg = arg.replace(case.children[1].name, declare[-1].split(" ")[0])

            else:
                #None complex arithmatic
                arg = build_case(case) 
        
        else:
            #if only variable name
            arg = case.children[0].name

        #appends if statement and labels based on current and next opperator. This also does short circuiting
        if cur_opp.name == "&&" and not next_opp == None:
            if next_opp.name == "||":
                lines.append(f'if ({arg}) goto {temp_label2}; else goto {temp_label1}')
                lines.append(f'{temp_label1}:')
                tmp_lab.append(temp_label2)
            else:
                lines.append(f'if ({arg}) goto {temp_label1}; else goto {temp_label2}')
                lines.append(f'{temp_label1}:')
                tmp_lab.append(temp_label2)
        elif cur_opp.name == "||" and not next_opp == None:
            if next_opp.name == "&&":
                lines.append(f'if ({arg}) goto {temp_label1}; else goto {temp_label2}')
                lines.append(f'{temp_label1}:')
                tmp_lab.append(temp_label2)                           
            else:
                lines.append(f'if ({arg}) goto {temp_label1}; else goto {temp_label2}')
                lines.append(f'{temp_label2}:')
                tmp_lab.append(temp_label1)
        else:
            #this is the last operation
            if cur_opp.name == "&&":
                    lines.append(f'if ({arg}) goto {success_label}; else goto {failure_label}')  
            elif cur_opp.name == "||":
                    lines.append(f'if ({arg}) goto {success_label}; else goto {failure_label}')                                                          

        #if next conditional statement is different
        if next_opp == None or next_opp.name != cur_opp.name:
            save = []
            if next_opp == None and tmp_lab != []: 

                #replace with success label in lines
                for i in lines:
                    for j in tmp_lab:
                        if j in i:
                            if cur_opp.name == "||":
                                lines[lines.index(i)] = i.replace(j, f'{success_label}:')
                            else:
                                lines[lines.index(i)] = i.replace(j, f'{failure_label}:') 

            else:
                if tmp_lab != []: 
                    #append goto for to be used in next statement
                    save.append(tmp_lab.pop())
                for i in tmp_lab:
                    #add label
                    lines.append(f'{i}:')

                tmp_lab = save

    return lines, labelDigit



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



def breakdownExpression(root, labelDigit, successLabel, failureLabel):
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


    for node in ns:
        if node.name in comp_ops:
            ops = [tvs.pop() for x in node.children if len(x.children) != 0]
        elif node.name in arth_ops:
            ops = [tvs.pop() for x in node.children if len(x.children) != 0]

            # Case 1: ops is empty
            if ops == [] and len(node.children) > 1:
                lines.append(f"D.{labelDigit} = {node.children[0].name} {node.name} {node.children[1].name}")
            # Case 2: two elem in ops
            elif len(ops) == 2:
                lines.append(f"D.{labelDigit} = {ops[0]} {node.name} {ops[1]}")
            else:
                pos = [node.children.index(x) for x in node.children if len(x.children) != 0 and len(node.children) > 1]

                # Case 3: one elem in ops but its the left element in the operation
                if pos == [0]:
                    lines.append(f"D.{labelDigit} = {ops[0]} {node.name} {node.children[1].name}")
                # Case 4: one elem in ops but its the right element in the operation
                elif pos == [1]:
                    lines.append(f"D.{labelDigit} = {node.children[0].name} {node.name} {ops[0]}")
                # Case 5: Its a unary operator
                elif pos == []:
                    lines.append(f"D.{labelDigit} = {node.name}{ops[0] if ops != [] else node.children[0].name}")
            
            tvs.append(f"D.{labelDigit}")
    return lines, labelDigit
