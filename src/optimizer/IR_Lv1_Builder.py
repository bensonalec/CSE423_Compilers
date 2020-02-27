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
            returnLines(i[1])

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

def returnLines(node):
    for element in node.children:
        try:
            splits = [["=","+="],["for"],["body"],["branch"],["return"],["call"],["while","do_while"],["break"],["continue"],["goto"],["label"]]
            ind = [splits.index(x) for x in splits if element.name in x]
            ind = ind[0]
            if ind == 0:
                print("Assignment")
            elif ind == 1:
                print("For loop")
            elif ind == 2:
                print("Body")
                returnLines(element)
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
