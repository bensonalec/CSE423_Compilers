import importlib
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

        self.symbols = set()
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
                        self.undefined.append(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope))
                    else:
                        self.symbols.add(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) 
                        cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")
                    """ if cur.Node.children[1].name == "main":
                        self.symbols.add(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) 
                        cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")

                    #if function name is in table already or main has not been declared
                    elif ([x for x in self.symbols if x.name == cur.Node.children[0].name]  == []):
                        cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/") 

                     #if main hasn't already been declared you don't need a function prototype              
                    elif ([x for x in self.symbols if x.name == "main"]  == []): 
                        self.symbols.add(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) 
                        cur = cur._replace(Scope = cur.Scope + cur.Node.children[1].name + "/")
                    #if it fails all checks
                    else:
                        self.undefined.append(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope))  """


                #Function Prototype Declaration
                elif index == 1:
                    self.symbols.add(Entry(True, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) 
                    #no need to change scope since it is a prototype 
                    pass
                
                
                # Function Call
                elif index == 2:
                    if ([x for x in self.symbols if x.name == cur.Node.children[0].name and cur.Scope in x.scope] == []):
                        print("Function Undefined")
                        self.undefined.append(Entry(True, cur.Node.children[0].name, None, cur.Scope)) #FIX ME
                    pass
                # Initialization and Usage
                elif index == 3:
                    
                    #declaration of variable
                    if len(cur.Node.children) > 1:
                        #add to symbol table this should also handle function param being that they are still within the same scope as there parent function
                        self.symbols.add(Entry(False, cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope)) #FIX ME
                        pass
                    #usage of varible
                    else:
                        if ([x for x in self.symbols if x.name == cur.Node.children[0].name and cur.Scope in x.scope] == []):
                            print("Variable Undeclared")
                            self.undefined.append(Entry(False,  cur.Node.children[1].name, cur.Node.children[0].name, cur.Scope,)) #FIX ME
                            
                        pass

         
            except ValueError:
                # This means that the token is not in that list
                pass

            # fetches the relevant children of the current node and appends the already known children to the list of residual nodes
            ntv = [Node(x, cur.Scope) for x in cur.Node.children if 'children' in x.__dict__] + ntv[1:]
        
        
        #prints symbol table and undefined
        print ("Known symbols:")
        [print (f"{x.name} {x.type} {x.scope}") for x in self.symbols]
        print ("Unknown symbols:")
        [print (f"{x.name} {x.type} {x.scope}") for x in self.undefined]
