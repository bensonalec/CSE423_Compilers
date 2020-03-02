import re

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
                print("If")

                #move this eventually
                def build_case(node):
                    #does not handle complex booleans.

                    #first node is the opperator
                    opp = node.children[0].name

                    #next find first arguement
                    if node.children[0].children[0].name == "var" or node.children[0].children[0].name == "call":
                        first_arg = node.children[0].children[0].children[0].name
                    else:
                        first_arg = node.children[0].children[0].name

                    #next find second arguement
                    if node.children[0].children[1].name == "var" or node.children[0].children[1].name == "call":
                        second_arg = node.children[0].children[1].children[0].name
                    else:
                        second_arg = node.children[0].children[1].name

                    return f'{first_arg} {opp} {second_arg}'


                end_if = []

                for case in element.children:

                    if case.name == "default":
                       lines.append(returnLines(case.children[0],returnDigit))
                       continue

                    temp_label1 = f'<D.{returnDigit}>'
                    returnDigit += 1
                    temp_label2 = f'<D.{returnDigit}>'
                    returnDigit += 1
                    end_if.append(f'<D.{returnDigit}>')
                    returnDigit += 1                    
                    #create if gimple statement with gotos
                    lines.append(f'if ({build_case(case)}) goto {temp_label1}; else goto {temp_label2}')
                    #label 1:
                    lines.append(f'{temp_label1}:')
                    #Body
                    lines.append(returnLines(case.children[1],returnDigit))
                    #add goto here to skip over other statements
                    lines.append(f'goto {end_if[-1]};')
                    #label 2:
                    lines.append(f'{temp_label2}:')
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
                func_call = element.children[0]

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

        except Exception as err:
            print("Exception: ", err)
            pass
    
    return lines

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
