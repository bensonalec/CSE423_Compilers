import re

class LevelOneIR():
    def __init__(self,astHead,symTable):
        self.astHead = astHead
        self.symTable = symTable

    def construct(self):
        sym = self.symTable
        print(buildBoilerPlate(sym))
        # print([(x.type, x.name, [(y.type, y.name) for y in self.symTable.symbols if y.is_param and y.scope.split('/')[1] == x.name]) for x in self.symTable.symbols if x.is_function])
        ntv = self.astHead
        varIndex = 0
        lastVarName = "_" + str(varIndex)
        bodyList = []
        for x in self.astHead.children:
            if x.name == "func":
                bodyList.append((x.children[1].name,x.children[3]))
        #now bodylist contains the bodies of each function

        for i in bodyList:
            print(returnLines(i[1],0))

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

def returnLines(node,lastVarName):
    lines = []
    for element in node.children:
        try:
            splits = [["=","+="],["for"],["body"],["branch"],["return"],["call"],["while","do_while"],["break"],["continue"],["goto"],["label"]]
            ind = [splits.index(x) for x in splits if element.name in x]
            ind = ind[0]
            if ind == 0:
                
                print("Assignment")
                #preform a DFS from the element node
                #upon each 
                tempDive = element.children[1]
                ntv = [tempDive]
                
                isOp = r'\+|\-|\/|\*'
                opCheck = re.compile(isOp)
                opStack = []
                
                while ntv != []:
                
                    # Grabs the first element which will be the residual left most child
                    cur = ntv[0]
                    
                    opStack.append(cur.name)
                    
                    ntv = [x for x in cur.children] + ntv[1:]
                print(opStack)
                last = len(opStack)
                for i in opStack[::-1]:
                    ind = last- 1
                    
                    if(opCheck.match(i)):
                        v1 = opStack[ind+1]
                        v2 = opStack[ind+2]
                        print(v1,i,v2)
                        lines.append(f"_{lastVarName} = {v1}{i}{v2}")
                        print(lines)
                        
                        # del opStack[ind+1]
                        # del opStack[ind+2]
                        # opStack[ind] = f"_{lastVarName}"
                        opStack = opStack[:ind] + [f"_{lastVarName}"] + opStack[ind+3:]
                        
                        print(opStack)
                        pass
    
                    elif(i == "var"):
                        pass
                    elif(i == "call"):
                        #NEED TO CAPTURE PARAMETERS

                        lastVarName += 1
                        # lines.append(f"_{lastVarName} = {cur.children[0].name}()")
                        
                        expansion = []
                        pass
                    else:
                        pass
                        # lines.append(f"_{lastVarName} = _{lastVarName}{cur.name}")
                    last -= 1
                element.print_AST()
            elif ind == 1:
                print("For loop")
            elif ind == 2:
                print("Body")
                ret,lastVarName = returnLines(element,lastVarName)
            elif ind == 3:
                print("If")
            elif ind == 4:
                print("Return")
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
        except Exception:
            pass
    
    return lines,lastVarName