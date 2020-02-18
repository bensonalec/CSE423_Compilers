import importlib,re
from collections import namedtuple

lex = importlib.import_module("lexer", ".")
ast = importlib.import_module("AST_builder", ".")

class Entry():
    def __init__(self, is_func, nam, typ, scop):
        self.is_function = is_func
        self.name = nam
        self.type = typ
        self.scope = scop
        self.references = []
        self.modifiers = []


Node = namedtuple("Node", ["Node", "Scope"])

class symbol_table():
    def __init__(self,AST):
        self.AST = AST

        self.symbols = []
        self.undefined = []
    
    def analyze(self):

        ntv = [Node(self.AST, "/")]

        typ = None
        b = False

        # Simple implementation of a DFS
        while ntv != []:
            # Grabs the first element which will be the residual left most child
            cur = ntv[0]

            # checks whether the current node is an operation that will need to access the symbol table 
            try:                
                index = ["func", "decl", "call", "var"].index(cur.Node.name)
                
                # Function Declaration
                if index == 0:
                    if [x for x in self.symbols if x.name == "main"] != [] and [x for x in self.symbols if cur.Node.children[1].name == x.name] == []:
                        print(f'Function Not Properly Declared {cur.Node.children[0].name}')
                        self.undefined.append(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope))
                    else:
                        self.symbols.append(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) 
                        cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")

                #Function Prototype Declaration
                elif index == 1:
                    self.symbols.append(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) 
                    cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")
                    pass
                
                
                # Function Call
                elif index == 2:
                    if [x for x in self.symbols if x.is_function == True and x.name == cur.Node.children[0].name] == []:
                        print(f'Function Undefined {cur.Node.children[0].name}')
                        self.undefined.append(Entry(True, cur.Node.children[0].name, "None", cur.Scope))
                    pass
                # Initialization and Usage
                elif index == 3:
                    
                    #declaration of variable
                    if len(cur.Node.children) > 1:
                        #add to symbol table this should also handle function param being that they are still within the same scope as there parent function
                        if([x for x in self.symbols if x.name == cur.Node.children[1].name and cur.Scope in x.scope] == []):
                            self.symbols.append(Entry(False, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) 
                        else:
                            print(f'Variable Already Declared {cur.Node.children[1].name} {cur.Node.children[0].name}')
                            self.undefined.append(Entry(False, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope))                             
                        pass
                    #usage of varible
                    else:
                        if ([x for x in self.symbols if x.name == cur.Node.children[0].name and cur.Scope in x.scope] == []):
                            print(f'Variable Undeclared {cur.Node.children[0].name}')
                            self.undefined.append(Entry(False,  cur.Node.children[0].name, "None", cur.Scope)) 
                            
                        pass

         
            except ValueError:
                # This means that the token is not in that list
                pass

            # fetches the relevant children of the current node and appends the already known children to the list of residual nodes
            ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]

        #Pass 2
        ntv = [Node(self.AST, "/")]

        typ = None
        b = False

        # Simple implementation of a DFS
        while ntv != []:
            # Grabs the first element which will be the residual left most child
            cur = ntv[0]

            # checks whether the current node is an operation that will need to access the symbol table 
            try:                
                index = ["="].index(cur.Node.name)
                
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
                            tblEntry = [x for x in self.symbols if x.name == var.name and cur.Scope in x.scope]
                            if(expectedType == ""):
                                if(len(tblEntry) == 1):
                                    #it is in the table already (good)
                                    topVar = tblEntry[0].name
                                    expectedType = tblEntry[0].type
                            else:
                                if(expectedType != tblEntry[0].type):
                                    print("Type mismatch")
                        #check function calls
                        elif(x.name == "call"):
                            chil = [z for z in x.children]
                            func = chil[-1]
                            tblEntry = [x for x in self.symbols if x.name == func.name and cur.Scope in x.scope and x.is_function]
                            if(len(tblEntry) == 1):
                                funcType = tblEntry[0].type
                                if(funcType != expectedType):
                                    print("Type mismatch")
                        #one of the children is a precision
                        elif(precCheck.match(x.name)):
                            if(expectedType != "float" and expectedType != "double"):
                                print("Type mismatch for",topVar,", unexpected precision")
                        #one of the chidlren is an integer
                        elif(digCheck.match(x.name)):
                            if(expectedType != "int"):
                                print("Type mismatch for",topVar,", unexpected integer")
                        elif(charCheck.match(x.name)):
                            if(expectedType != "char"):
                                print("Type mismatch for",topVar,", unexpected character")
                        elif(stringCheck.match(x.name)):
                            if(expectedType != "string"):
                                print("Type mismatch for",topVar,", unexpected string")
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
                                            print("Type mismatch")
                                    elif((precCheck.match(curTemp.Node.name))):
                                        print("Type mismatch")
                                    elif(not (digCheck.match(curTemp.Node.name) or opCheck.match(curTemp.Node.name))):
                                        print("Type mismatch")
                                ntvTemp = [Node(z, curTemp.Scope) for z in curTemp.Node.children if 'children' in z.__dict__] + ntvTemp[1:]

                            pass
                    # print("Variable in use!",cur.Node.name,[x.name for x in cur.Node.children])

         
            except ValueError:
                # This means that the token is not in that list
                pass

            # fetches the relevant children of the current node and appends the already known children to the list of residual nodes
            ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]


    def print_symbol_table(self):
        if len(self.symbols) == 0:
            print ("No defined symbols available")
            return

        col_lengths = [
            max(max([len(x.name) for x in self.symbols]), len("Name")),
            max(max([len(str(x.is_function)) for x in self.symbols]), len("Function?")),
            max(max([len(x.type) for x in self.symbols]), len("Type")),
            max(max([len(x.scope) for x in self.symbols]), len("Scope")),
            max(max([len(x.references) for x in self.symbols]), len("References")),
            max(max([len(x.modifiers) for x in self.symbols]), len("Modifiers")),
        ]

        self.symbols.sort(key=lambda x: x.scope)

        print (f"{'Name':^{col_lengths[0]}} | {'Function?':^{col_lengths[1]}} | {'Type':^{col_lengths[2]}} | {'Scope':^{col_lengths[3]}}")
        print (f"{'-'*col_lengths[0]}-+-{'-'*col_lengths[1]}-+-{'-'*col_lengths[2]}-+-{'-'*col_lengths[3]}-")
        for x in self.symbols: print(f"{x.name:>{col_lengths[0]}} | {str(x.is_function) :>{col_lengths[1]}} | {x.type :>{col_lengths[2]}} | {x.scope :<{col_lengths[3]}}")

    def print_unknown_symbols(self):
        if len(self.undefined) == 0:
            print ("No undefined symbols available")
            return

        col_lengths = [
            max(max([len(x.name) for x in self.undefined]), len("Name")),
            max(max([len(str(x.is_function)) for x in self.undefined]), len("Function?")),
            max(max([len(x.scope) for x in self.undefined]), len("Scope")),
        ]

        self.undefined.sort(key=lambda x: x.scope)

        print (f"{'Name':^{col_lengths[0]}} | {'Function?':^{col_lengths[1]}} | {'Type':^{col_lengths[2]}}")
        print (f"{'-'*col_lengths[0]}-+-{'-'*col_lengths[1]}-+-{'-'*col_lengths[2]}-")
        for x in self.undefined: print(f"{x.name:>{col_lengths[0]}} | {str(x.is_function) :>{col_lengths[1]}} | {x.type :>{col_lengths[2]}}")