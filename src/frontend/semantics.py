import importlib,re
from collections import namedtuple

lex = importlib.import_module("lexer", __name__)
ast = importlib.import_module("AST_builder", __name__)

en_map = {
    0 : "Variable",
    1 : "Function",
    2 : "Parameter",
    3 : "Label",
}

class Entry():
    def __init__(self, en_typ, nam, typ, scop, modif):
        self.entry_type = en_typ
        self.name = nam
        self.type = typ
        self.scope = scop
        self.references = []
        self.modifiers = list(sorted(set(modif)))


Node = namedtuple("Node", ["Node", "Scope"])
Node.__docstring__ = """
A simple namedtuple to allow for better readability when performing the depth first search required for the semantic analysis.
"""
class symbol_table():
    def __init__(self,AST):
        self.AST = AST

        self.symbols = []
        self.undefined = []
        self.errors = []

    def analyze(self):

        ntv = [Node(self.AST, "/")]
        scopenum = 0
        typ = None
        b = False
        # Simple implementation of a DFS
        while ntv != []:
            # Grabs the first element which will be the residual left most child
            cur = ntv[0]

            # checks whether the current node is an operation that will need to access the symbol table
            try:
                index = ["func", "decl", "call", "var", "body"].index(cur.Node.name)

                #Catches edge case where var or func is used an self_defined name
                if cur.Node.children == []:
                    ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]
                    continue


                # Function Declaration
                if index == 0:
                    # If a function is declared after main without a prototype
                    if [x for x in self.symbols if x.name == "main" and x.entry_type == {value: key for key, value in en_map.items()}["Function"]] != [] and [x for x in self.symbols if cur.Node.children[1].name == x.name] == []:
                        # print(f'Function Not Properly Declared {cur.Node.children[0].name}')
                        self.undefined.append(Entry({value: key for key, value in en_map.items()}["Function"], cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))
                    # If a function is declared befor main is declared without a prototype
                    elif [x for x in self.symbols if x.name == "main" and x.entry_type == {value: key for key, value in en_map.items()}["Function"]] == []:
                        self.symbols.append(Entry({value: key for key, value in en_map.items()}["Function"], cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))
                        cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")
                    else:
                        cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")
                #Function Prototype Declaration
                elif index == 1:
                    self.symbols.append(Entry({value: key for key, value in en_map.items()}["Function"], cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))
                    cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")
                    pass


                # Function Call
                elif index == 2:
                    if [x for x in self.symbols if x.entry_type == {value: key for key, value in en_map.items()}["Function"] and x.name == cur.Node.children[0].name] == []:
                        # print(f'Function Undefined {cur.Node.children[0].name}')
                        self.undefined.append(Entry({value: key for key, value in en_map.items()}["Function"],cur.Node.children[0].name, "None", cur.Scope, [x.name for x in cur.Node.children[0].children]))
                    pass
                # Initialization and Usage
                elif index == 3:

                    #declaration of variable
                    if len(cur.Node.children) > 1:
                        #add to symbol table this should also handle function param being that they are still within the same scope as there parent function
                        if([x for x in self.symbols if x.name == cur.Node.children[1].name and x.scope in cur.Scope] == []):
                            if cur.Node.parent.parent.name == "func" or cur.Node.parent.parent.name == "decl":
                                if cur.Node.parent.name == "param":
                                    self.symbols.append(Entry({value: key for key, value in en_map.items()}["Parameter"],cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))
                                else:
                                    self.symbols.append(Entry({value: key for key, value in en_map.items()}["Variable"],cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))
                            else:
                                    self.symbols.append(Entry({value: key for key, value in en_map.items()}["Variable"],cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))
                        elif(cur.Node.parent.name != "param"):
                            print(f'Variable Already Declared {cur.Node.children[1].name} {cur.Node.children[0].name}')
                            self.undefined.append(Entry({value: key for key, value in en_map.items()}["Variable"], cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))
                        elif(cur.Node.parent.name == "param" and [x for x in self.symbols if cur.Node.children[1].name == x.name] == []):
                            print(f'Undeclared parameter{cur.Node.children[1].name} {cur.Node.children[0].name}')
                            self.undefined.append(Entry({value: key for key, value in en_map.items()}["Variable"], cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope, [x.name for x in cur.Node.children[0].children]))

                        pass
                    #usage of varible
                    else:
                        if ([x for x in self.symbols if x.name == cur.Node.children[0].name and x.scope in cur.Scope] == []):
                            print(f'Variable Undeclared {cur.Node.children[0].name}')
                            self.undefined.append(Entry({value: key for key, value in en_map.items()}["Variable"],  cur.Node.children[0].name, "None", cur.Scope, [x.name for x in cur.Node.children[0].children]))

                        pass
                elif index == 4:
                    cur = cur._replace(Scope = f"{cur.Scope}{scopenum}/")
                    scopenum += 1

                    #gets all labels declared in body of a function
                    labels = [x.children[0] for x in cur.Node.children if x.name == "label"]
                    if labels != []:

                        #for each label in the body
                        for i in labels:
                            #checks if label is already in the symbol table.
                            if [x for x in self.symbols if x.name == i.name] == []:
                                self.symbols.append(Entry({value: key for key, value in en_map.items()}["Label"],  i.name, "None", cur.Scope, [x.name for x in cur.Node.children[0].children]))
                            else:
                                self.undefined.append(Entry({value: key for key, value in en_map.items()}["Label"],  i.name, "None", cur.Scope, [x.name for x in cur.Node.children[0].children]))

                    pass

            except ValueError:
                # This means that the token is not in that list
                pass

            # fetches the relevant children of the current node and appends the already known children to the list of residual nodes
            ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]

        #Pass 2, in this pass check types and function parameters
        ntv = [Node(self.AST, "/")]

        typ = None
        b = False

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
                    #regexes to do type checks on the fly
                    isDigit = r"\-?([1-9]\d*|\d)"
                    isOp = r'\+|\-|\/|\*'
                    isPrec = r"\-?(\d\.\d+|[1-9]\d*\.\d+)"
                    isChar = r"(\'[\w\;\\ \%\"\']\')"
                    isString = r"(\"[\w+\;\\ \%\"\']*\")"
                    precCheck = re.compile(isPrec)
                    digCheck = re.compile(isDigit)
                    opCheck = re.compile(isOp)
                    charCheck = re.compile(isChar)
                    stringCheck = re.compile(isString)

                    for x in children:
                        #get the expected type, or variable in assignment
                        if(x.name == "var"):

                            chil = ([z for z in x.children])
                            #this is the variable that is being assigned to
                            var = chil[-1]
                            #get the expected type from symbol table

                            tblEntry = [x for x in self.symbols if x.name == var.name and funcname in x.scope]

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
                            tblEntry = [x for x in self.symbols if x.name == func.name and cur.Scope in x.scope and x.entry_type == {value: key for key, value in en_map.items()}["Function"]]
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
                                    elif([x for x in self.symbols if x.name == curTemp.Node.name and curTemp.Scope in x.scope] != []):
                                        var = [x for x in self.symbols if x.name == curTemp.Node.name and curTemp.Scope in x.scope][0]
                                        if(var.type != "int"):
                                            self.errors.append("Type mismatch for " + topVar)
                                    elif((precCheck.match(curTemp.Node.name))):
                                        self.errors.append("Type mismatch for " + topVar)
                                    elif(not (digCheck.match(curTemp.Node.name) or opCheck.match(curTemp.Node.name))):
                                        self.errors.append("Type mismatch for " + topVar)
                                ntvTemp = [Node(z, curTemp.Scope) for z in curTemp.Node.children if 'children' in z.__dict__] + ntvTemp[1:]

                            pass

                elif index == 1:
                    #iterate through the children, get the name of the function, look up how many parameters it expects
                    func = cur.Node.children[0]
                    functionName = func.name
                    functionChildren = [x.name for x in func.children]
                    #get the number of params and types from the symbol table
                    params = [x for x in self.symbols if functionName in x.scope and x.entry_type == {value: key for key, value in en_map.items()}["Parameter"]]
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
                elif index == 2:
                    funcname = cur.Node.children[1].name

                    #get params of the node currently being visited
                    params = [x for x in cur.Node.children[2].children]
                    params = [(x.children[0].name) for x in params]
                    # print(params)
                    #get the expected params

                    expected = ([(x.type) for x in self.symbols if x.entry_type == {value: key for key, value in en_map.items()}["Parameter"] and f"/{funcname}/" == x.scope])
                    if expected != params:
                        self.errors.append("Parameters in function prototype do not match function definition in " + funcname)
                elif index == 3:
                    label = cur.Node.children[0]
                    labelName = label.name

                    #look for labelName: in the symbol table
                    toLook = labelName
                    found = ([x.name for x in self.symbols if x.entry_type == {value: key for key, value in en_map.items()}["Label"] and x.name == toLook])
                    if(found == []):
                        self.errors.append("Label " +  labelName + " not found")
                    elif(len(found) > 1):
                        self.errors.append("Multiple labels with name " +   labelName + " found")

            except ValueError:
                # This means that the token is not in that list
                pass

            # fetches the relevant children of the current node and appends the already known children to the list of residual nodes
            ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]

    def __str__(self):
        li = []

        known_len = [
            max([len(x.name) for x in self.symbols] + [len("Name")]),
            max([len(en_map[x.entry_type]) for x in self.symbols] + [len("Entry Type")]),
            max([len(x.type) for x in self.symbols] + [len("Type")]),
            max([len(x.scope) for x in self.symbols] + [len("Scope")]),
            max([len(", ".join(x.modifiers)) for x in self.symbols] + [len("Modifiers")]),
        ]
        unknown_len = [
            max([len(x.name) for x in self.undefined] + [len("Name")]),
            max([len(en_map[x.entry_type]) for x in self.undefined] + [len("Entry Type")]),
            max([len(x.scope) for x in self.undefined] + [len("Scope")]),
        ]

        li.append("Known Symbols")
        li.append(f" {'Name':^{known_len[0]}} | {'Entry Type':^{known_len[1]}} | {'Type':^{known_len[2]}} | {'Scope':^{known_len[3]}} | {'Modifiers':^{known_len[4]}} ")
        li.append(f"-{'-'*known_len[0]}-+-{'-'*known_len[1]}-+-{'-'*known_len[2]}-+-{'-'*known_len[3]}-+-{'-'*known_len[4]}-")
        for x in self.symbols:
            li.append(f" {x.name:>{known_len[0]}} | {en_map[x.entry_type]:>{known_len[1]}} | {x.type :>{known_len[2]}} | {x.scope :<{known_len[3]}} | {', '.join(x.modifiers) :>{known_len[4]}}")
        li.append("")
        li.append("Unknown Symbols")
        li.append(f" {'Name':^{unknown_len[0]}} | {'Entry Type':^{unknown_len[1]}} | {'Type':^{unknown_len[2]}}")
        li.append(f"-{'-'*unknown_len[0]}-+-{'-'*unknown_len[1]}-+-{'-'*unknown_len[2]}-")
        for x in self.undefined:
            li.append(f" {x.name:>{unknown_len[0]}} | {en_map[x.entry_type]:>{unknown_len[1]}} | {x.type :>{unknown_len[2]}}")

        return "\n".join(li) + "\n"

    def print_symbol_table(self):
        # if len(self.symbols) == 0:
        #     print ("No defined symbols available")
        #     return

        col_lengths = [
            max([len(x.name) for x in self.symbols] + [len("Name")]),
            max([len(en_map[x.entry_type]) for x in self.symbols] + [len("Entry Type")]),
            max([len(x.type) for x in self.symbols] + [len("Type")]),
            max([len(x.scope) for x in self.symbols] + [len("Scope")]),
            max([len(", ".join(x.modifiers)) for x in self.symbols] + [len("Modifiers")]),

        ]

        print ("Known Symbols")
        print (f" {'Name':^{col_lengths[0]}} | {'Entry Type':^{col_lengths[1]}} | {'Type':^{col_lengths[2]}} | {'Scope':^{col_lengths[3]}} | {'Modifiers':^{col_lengths[4]}} ")
        print (f"-{'-'*col_lengths[0]}-+-{'-'*col_lengths[1]}-+-{'-'*col_lengths[2]}-+-{'-'*col_lengths[3]}-+-{'-'*col_lengths[4]}-")
        for x in self.symbols:
            print(f" {x.name:>{col_lengths[0]}} | {en_map[x.entry_type]:>{col_lengths[1]}} | {x.type :>{col_lengths[2]}} | {x.scope :<{col_lengths[3]}} | {', '.join(x.modifiers) :>{col_lengths[4]}}")
        # print("")

    def print_unknown_symbols(self):
        # if len(self.undefined) == 0:
        #     print ("No undefined symbols available")
        #     return

        col_lengths = [
            max([len(x.name) for x in self.undefined] + [len("Name")]),
            max([len(en_map[x.entry_type]) for x in self.undefined] + [len("Entry Type")]),
            max([len(x.scope) for x in self.undefined] + [len("Scope")]),
        ]

        print ("Unknown Symbols")
        print (f" {'Name':^{col_lengths[0]}} | {'Entry Type':^{col_lengths[1]}} | {'Type':^{col_lengths[2]}}")
        print (f"-{'-'*col_lengths[0]}-+-{'-'*col_lengths[1]}-+-{'-'*col_lengths[2]}-")
        for x in self.undefined:
            print(f" {x.name:>{col_lengths[0]}} | {en_map[x.entry_type]:>{col_lengths[1]}} | {x.type :>{col_lengths[2]}}")
        # print("")

    def printSemanticErrors(self):
        for i in self.errors:
            print(i)

    def lineSemanticErrors(self):
        output = ""
        for i in self.errors:
            output += (i+"\n")

        return output
