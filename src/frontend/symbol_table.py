"""
The module serves to create the symbol table
"""
import os
import re
from importlib.machinery import SourceFileLoader
from collections import namedtuple
from inspect import getsourcefile

lex = SourceFileLoader("lexer", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/lexer.py").load_module()
ast = SourceFileLoader("AST_builder", f"{os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))}/AST_builder.py").load_module()

en_map = {
    0 : "Variable",
    1 : "Function",
    2 : "Parameter",
    3 : "Label",
}

class Entry():
    """
    A class that represents a singular entry in the symbol table
    """
    def __init__(self, en_typ, nam, typ, scop, modif):
        """
        Args:
            en_typ: Whether the entry is a variable, function, parameter, or label.
            nam: Name of the entry.
            typ: The associated type of the entry such as `int`, `float` ect. For functions this represents the return type.
            scop: The scope where the entry exists.
            modif: The modifiers associated with the entry such as `unsigned`, `const`, `static` ect.
        """
        self.entry_type = en_typ
        self.name = nam
        self.type = typ
        self.scope = scop
        self.references = []
        self.modifiers = list(sorted(set(modif)))


Node = namedtuple("Node", ["Node", "Scope"])
Node.__doc__ = """
A simple namedtuple to allow for better readability when performing the depth first search required for the generation of the symbol table.
"""
class symbol_table():
    """
    A class that stores all the known and unknown symbols.
    """
    def __init__(self,AST):
        """
        Args:
            AST: The head node of the abstract syntax tree.
        """
        self.AST = AST

        self.symbols = []
        self.undefined = []
        self.errors = []

    def analyze(self):
        """
        Analyses the abstract syntax tree to determine whether there are any undeclared references.
        """
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
                        self.undefined.append(Entry({value: key for key, value in en_map.items()}["Function"],cur.Node.children[0].name, "None", cur.Scope, [x.name for x in cur.Node.children[0].children]))
                    else:
                        ref = [x for x in self.symbols if en_map[x.entry_type] == "Function" and x.name == cur.Node.children[0].name]
                        for i in ref:
                            i.references.append(i)

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
                        else:
                            ref = [x for x in self.symbols if x.name == cur.Node.children[0].name and x.scope in cur.Scope]
                            for i in ref:
                                i.references.append(i)

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

    def __repr__(self):
        return "\n".join(self.errors)

    def print_symbol_table(self):
        """
        Prints the known symbols in the symbol table to stdout
        """

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

    def print_unknown_symbols(self):
        """
        Prints the unknown symbols in the symbol table to stdout
        """

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
