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
        returnVarName = f"D.{returnDigit}"
        for i in bodyList:
            for x in returnLines(i[1],0, returnVarName)[0]:
                print(x)
            returnDigit += 1
            returnVarName = f"D.{returnDigit}"

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

def returnLines(node,lastVarName, returnVarName):
    lines = []
    for element in node.children:
        try:
            splits = [["=","+="],["for"],["body"],["branch"],["return"],["call"],["while","do_while"],["break"],["continue"],["goto"],["label"]]
            ind = [splits.index(x) for x in splits if element.name in x]
            ind = ind[0]
            if ind == 0:
                #Assignment

                varName = element.children[0].children[0].name
                
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
                ret,lastVarName = returnLines(element,lastVarName)
            elif ind == 3:
                print("If")
            elif ind == 4: 
                #Return

                # It returns some type of arithmetic, break it down.
                # TODO: it currently breaks down single values like "return 1;"
                #       should I keep this? or test if it is "complicated" arithmetic?
                if len(element.children) > 0:
                    lines += breakdownArithmetic(element.children[0], f"_{lastVarName}")
                    lines.append(f"{returnVarName} = _{lastVarName}")
                    lastVarName += 1
                    lines.append(f"return {returnVarName};") 
                
                # Returns nothing
                else:
                    lines.append(f"return;") 

            elif ind == 5:
                print("Call")
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
    
    return lines,lastVarName

def breakdownArithmetic(root, varName):
    ntv = [root]
    
    isOp = r'\+|\-|\/|\*'
    opCheck = re.compile(isOp)
    opStack = []

    lines = []
    
    while ntv != []:
        cur = ntv[0]
        opStack.append(cur.name)
        ntv = [x for x in cur.children] + ntv[1:]

    last = len(opStack)
    for i in opStack[::-1]:
        ind = last- 1
        
        if(opCheck.match(i)):
            v1 = opStack[ind+1]
            v2 = opStack[ind+2]

            lines.append(f"{varName} = {v1}{i}{v2}")
            opStack = opStack[:ind] + [f"{varName}"] + opStack[ind+3:]
            pass

        elif(i == "var"):
            pass
        elif(i == "call"):
            #TODO: NEED TO CAPTURE PARAMETERS
            varName += 1
            expansion = []
            pass

        #There is only one value.
        #I think this will only happen when numbers are passed in and not operators? 
        #maybe it will happen when function calls are passed in?
        elif(len(opStack) == 1):
            lines.append(f"{varName} = {i}")

        last -= 1

    return lines
