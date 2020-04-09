"""
The module serves to perform semantic analysis on the AST to ensure the typing is correct
"""

from collections import namedtuple
import re


Node = namedtuple("Node", ["Node", "Scope"])
Node.__doc__ = """
A simple namedtuple to allow for better readability when performing the depth first search required for the semantic analysis.
"""

Node = namedtuple("Node", ["Node", "Scope"])
en_map = {
    0 : "Variable",
    1 : "Function",
    2 : "Parameter",
    3 : "Label",
}


class semantic():
    """
    A class that stores any semantic errors that occur.
    """

    def __init__(self,AST,symbols):
        """
        Args:
            AST: The head node of the abstract syntax tree.
            symbols: The symbol table
        """

        self.errors = []
        self.AST = AST
        self.symbols = symbols

    def semanticAnalysis(self):
        """
        Runs semantic analysis
        """

        AST = self.AST
        symbols = self.symbols
        ntv = [Node(AST, "/")]

        typ = None
        b = False

        #regexes to do type checks on the fly
        isDigit = r"\-?([1-9]\d*|\d)"
        isOp = r'\+|\-|\/|\*|\||\&|\^|\~'
        isPrec = r"\-?(\d\.\d+|[1-9]\d*\.\d+)"
        isChar = r"(\'[\w\;\\ \%\"\']\')"
        isString = r"(\"[\w+\;\\ \%\"\']*\")"
        precCheck = re.compile(isPrec)
        digCheck = re.compile(isDigit)
        opCheck = re.compile(isOp)
        charCheck = re.compile(isChar)
        stringCheck = re.compile(isString)

        # Simple implementation of a DFS
        funcname = ""
        while ntv != []:
            # Grabs the first element which will be the residual left most child
            cur = ntv[0]

            # checks whether the current node is an operation that will need to access the symbol table
            try:
                index = ["=","call","func","goto"].index(cur.Node.name)

                #Catches edge case where var or func is used an self_defined name
                if cur.Node.children == []:
                    ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]
                    continue

                # Function Declaration
                if index == 0:
                    children = cur.Node.children
                    expectedType = ""
                    topVar = ""

                    for x in children:
                        #get the expected type, or variable in assignment
                        if(x.name == "var"):

                            chil = ([z for z in x.children])
                            #this is the variable that is being assigned to
                            var = chil[-1]
                            #get the expected type from symbol table

                            tblEntry = [x for x in symbols if x.name == var.name and funcname in x.scope]

                            if(expectedType == ""):
                                if(len(tblEntry) == 1):
                                    #it is in the table already (good)
                                    topVar = tblEntry[0].name
                                    expectedType = tblEntry[0].type
                            else:
                                if(expectedType != tblEntry[0].type):
                                    self.errors.append("Type mismatch for variable" + " " + var.name)
                        #check function calls
                        elif(x.name == "call"):
                            chil = [z for z in x.children]
                            func = chil[-1]
                            tblEntry = [x for x in symbols if x.name == func.name and cur.Scope in x.scope and x.entry_type == {value: key for key, value in en_map.items()}["Function"]]
                            if(len(tblEntry) == 1):
                                funcType = tblEntry[0].type
                                if(funcType != expectedType):
                                    self.errors.append("Type mismatch for " + topVar)
                        #one of the children is a precision
                        elif(precCheck.match(x.name)):
                            if(expectedType != "float" and expectedType != "double"):
                                self.errors.append("Type mismatch for " + topVar + ", unexpected precision " + x.name)
                        #one of the chidlren is an integer
                        elif(digCheck.match(x.name)):
                            if(expectedType != "int"):
                                self.errors.append("Type mismatch for " + topVar + ", unexpected integer " + x.name)
                        elif(charCheck.match(x.name)):
                            if(expectedType != "char"):
                                self.errors.append("Type mismatch for " + topVar + ", unexpected character " + x.name)
                        elif(stringCheck.match(x.name)):
                            if(expectedType != "string"):
                                self.errors.append("Type mismatch for " + topVar + ", unexpected string " + x.name)
                        #case that operators are in use
                        elif(opCheck.match(x.name)):
                            #need to desced through all possible branches of this, and ensure everything is use is an integer
                            #expect variables, function calls, and integers in operatiosn
                            #need to traverse all nodes inside of this branch
                            ntvTemp = [Node(x, "/")]
                            while ntvTemp != []:
                                # Grabs the first element which will be the residual left most child
                                curTemp = ntvTemp[0]
                                if(expectedType == "int"):
                                    if(curTemp.Node.name == "var" or curTemp.Node.name == "call"):
                                        pass
                                    elif([x for x in symbols if x.name == curTemp.Node.name and curTemp.Scope in x.scope] != []):
                                        var = [x for x in symbols if x.name == curTemp.Node.name and curTemp.Scope in x.scope][0]
                                        if(var.type != "int"):
                                            self.errors.append("Type mismatch for " + topVar)
                                    elif((precCheck.match(curTemp.Node.name))):
                                        self.errors.append("Type mismatch for " + topVar)
                                    elif(not (digCheck.match(curTemp.Node.name) or opCheck.match(curTemp.Node.name))):
                                        self.errors.append("Type mismatch for " + topVar)
                                ntvTemp = [Node(z, curTemp.Scope) for z in curTemp.Node.children if 'children' in z.__dict__] + ntvTemp[1:]

                            pass
                #function call
                elif index == 1:
                    #iterate through the children, get the name of the function, look up how many parameters it expects
                    func = cur.Node.children[0]
                    functionName = func.name
                    functionChildren = [x.name for x in func.children]
                    #get the number of params and types from the symbol table
                    params = [x for x in symbols if functionName in x.scope and x.entry_type == {value: key for key, value in en_map.items()}["Parameter"]]
                    types = [x.type for x in params]
                    if(len(params) != len(functionChildren)):
                        self.errors.append("Improper amount of arguments in call to function " + functionName)
                    else:
                        for it,par in enumerate(functionChildren):
                            #get type of par
                            expec = types[it]
                            #one of the children is a precision
                            if(precCheck.match(par)):
                                if(expec != "float" and expec != "double"):
                                    self.errors.append("Type mismatch for " + functionName + ", unexpected precision " + par)
                            #one of the chidlren is an integer
                            elif(digCheck.match(par)):
                                if(expec != "int"):
                                    self.errors.append("Type mismatch for " + functionName + ", unexpected integer " + par)
                            elif(charCheck.match(par)):
                                if(expec != "char"):
                                    self.errors.append("Type mismatch for " + functionName + ", unexpected character " + par)
                            elif(stringCheck.match(par)):
                                if(expec != "string"):
                                    self.errors.append("Type mismatch for " + functionName + ", unexpected string " + par)

                            #check if type of par and types[it] are the same

                            pass
                    #then iterate through the children of this and check the types of the parameters
                    pass
                #function definition
                elif index == 2:
                    funcname = cur.Node.children[1].name

                    #get params of the node currently being visited
                    params = [x for x in cur.Node.children[2].children]
                    params = [(x.children[0].name) for x in params]
                    # print(params)
                    #get the expected params

                    expected = ([(x.type) for x in symbols if x.entry_type == {value: key for key, value in en_map.items()}["Parameter"] and f"/{funcname}/" == x.scope])
                    if expected != params:
                        self.errors.append("Parameters in function prototype do not match function definition in " + funcname)
                #goto labels
                elif index == 3:
                    label = cur.Node.children[0]
                    labelName = label.name

                    #look for labelName: in the symbol table
                    toLook = labelName
                    found = ([x.name for x in symbols if x.entry_type == {value: key for key, value in en_map.items()}["Label"] and x.name == toLook])
                    if(found == []):
                        self.errors.append("Label " +  labelName + " not found")
                    elif(len(found) > 1):
                        self.errors.append("Multiple labels with name " +   labelName + " found")

            except ValueError:
                # This means that the token is not in that list
                pass

            # fetches the relevant children of the current node and appends the already known children to the list of residual nodes
            ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]

    def printSemanticErrors(self):
        """
        Prints the semantic errors to stdout
        """
        for i in self.errors:
            print(i)

    def lineSemanticErrors(self):
        """
        Retrieves the semantic errors

        Returns:
            output: All the semantic errors as a string separated by new lines
        """
        output = ""
        for i in self.errors:
            output += (i+"\n")

        return output