"""
This module takes in the parse tree, and produces an Abstract Syntax Tree.This is done using a Depth First Traversal. By taking the Concrete Syntax Tree (Parse Tree)and converting it to an Abstract Syntax Tree we can begin to move towards an intermediate form.
"""
def buildAST(parseHead):
    """
    Produces an AST given the head of the Parse Tree

    Args:
        parseHead: The head node of the parse tree.

    Returns:
        The head of the Abstract Syntax Tree.
    """
    head = parseHead
    ASTHead = None
    ASTcurrent = None
    ntv = [(head, ASTcurrent)]
   
    #DFS by iterating through a stack of nodes to visit
    while ntv != []:
        c = ntv[0]
        typ = c[0].token
        ASTcurrent = c[1]

        expansion = None

        #This block checks the type of the ASTNode that is  being visited, and acts as a monstrous switch statement, for each visited node a proper AST segment or node is built
        if typ == "program":
            ASTHead = ASTNode("program", ASTcurrent)
            ASTcurrent = ASTHead
        
        elif typ == "initialization":
            ASTcurrent.children.append(ASTNode("=", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("var", ASTcurrent))
            ASTcurrent.children[-1].children.append(ASTNode(c[0].content[1].value, ASTcurrent))

            # Check if there is a value to initialize the variable to
            if not [x for x in c[0].content if 'value' in x.__dict__ and x.value == "="]:
                ASTcurrent.children.append(ASTNode("NULL", ASTcurrent.parent))
            
            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "var_type"]
            expansion += [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token != "var_type"]
        
        elif typ == "designation":
            ASTcurrent.children.append(ASTNode(c[0].content[1].content[0].value, ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("var", ASTcurrent))
            ASTcurrent.children[-1].children.append(ASTNode(c[0].content[0].content[0].value, ASTcurrent))

            # Skip the assignment node
            expansion = [(x, ASTcurrent) for x in c[0].content[1:] if 'content' in x.__dict__]           
        
        elif typ == "value":
            ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value}", ASTcurrent))
        
        elif typ == "function definition":
            ASTcurrent.children.append(ASTNode("func", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent))
            ASTcurrent.children.append(ASTNode("param", ASTcurrent))
           
            # split the content of the function definition up
            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == 'func_type']
            expansion += [(x, ASTcurrent.children[1]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'args']
            expansion += [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == 'block']
        
        elif typ == "functionDeclaration":
            ASTcurrent.children.append(ASTNode("decl", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent))
            ASTcurrent.children.append(ASTNode("param", ASTcurrent))
            
            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == 'func_type']
            expansion += [(x, ASTcurrent.children[1]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'args']
        
        elif typ == "arg_terminal":
            ASTcurrent.children.append(ASTNode("var", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent))
        
        elif typ == "if":
            # Check if the node is already within a branch
            if ASTcurrent.name != "branch":
                ASTcurrent.children.append(ASTNode("branch", ASTcurrent))
                ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("case", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent))

            # split the condition from the body and further if statements
            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'collation']
            expansion += [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == 'if_body']
            expansion += [(x, ASTcurrent.parent) for x in c[0].content if 'content' in x.__dict__ and x.token == "if_expansion"]
        
        elif typ == "if_expansion":
            # Check if it's the last else in the if statement
            if c[0].content[1].content[0].token == 'content_terminal' and c[0].content[1].content[0].content[0].token == "if":
                expansion = [(x, ASTcurrent) for x in c[0].content[1].content[0].content if 'content' in x.__dict__ and x.token == "if"]
            else:
                ASTcurrent.children.append(ASTNode("default", ASTcurrent))
                ASTcurrent = ASTcurrent.children[-1]
        
        elif typ.startswith('arithmetic'):

            if len(c[0].content) == 2:
                # To catch unary operations
                if typ.endswith('unary'):
                    # All operations with two children are pre ops.
                    if 'value' in c[0].content[0].__dict__:
                        # If the first child is a terminal it can either be a pre increment or a sizeof call
                        ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent))
                        ASTcurrent = ASTcurrent.children[-1]
                        if ASTcurrent.name == "sizeof":
                            pass
                        else:
                            ASTcurrent.children.append(ASTNode("NULL", ASTcurrent))
                            ASTcurrent.children.append(ASTNode("", ASTcurrent))
                            ASTcurrent = ASTcurrent.children[-1]
                    else:
                        # if the first value is a terminal its an operation that is either dereferencing, referencing, positive, negative, complement, and logical negation
                        ASTcurrent.children.append(ASTNode(c[0].content[0].content[0].value, ASTcurrent))
                        ASTcurrent = ASTcurrent.children[-1]

                elif typ.endswith('post'):
                    # The only post operations with two children are increment and decrement 
                    ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent))
                    ASTcurrent = ASTcurrent.children[-1]
                    ASTcurrent.children.append(ASTNode("", ASTcurrent))
                    ASTcurrent.children.append(ASTNode("NULL", ASTcurrent))
                    ASTcurrent = ASTcurrent.children[0]
                    pass
                else:
                    ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent))
                    ASTcurrent = ASTcurrent.children[-1]

                    expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__]
            elif len(c[0].content) == 3:
                # If there are binary operations
                if 'value' in c[0].content[1].__dict__:
                    ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent))
                    ASTcurrent = ASTcurrent.children[-1]
                
                    expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__]
                else:
                    pass
                pass
        
        elif typ.startswith('collation'):
            if len(c[0].content) == 3:
                # To ensure that there are no false positives since arithmetic is directly linked to collation
                if 'value' in c[0].content[1].__dict__:
                    ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent))
                    ASTcurrent = ASTcurrent.children[-1]
                
                    expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__]

        elif typ == "return":
            ASTcurrent.children.append(ASTNode("return", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]

        elif typ == "string literal":
            ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent))

        elif typ == "function call":
            ASTcurrent.children.append(ASTNode("call", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]

            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == "parameter"]
        
        elif typ == "while loop":
            ASTcurrent.children.append(ASTNode("while", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent))

            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "collation"]
            expansion += [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and (x.token == "block" or x.token == "content_terminal")]
        
        elif typ == "break":
            ASTcurrent.children.append(ASTNode("break", ASTcurrent))
        
        elif typ == "continue":
            ASTcurrent.children.append(ASTNode("continue", ASTcurrent))
        
        elif typ == "jump":
            ASTcurrent.children.append(ASTNode("goto", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent))
        
        elif typ == "goto":
            ASTcurrent.children.append(ASTNode("label", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value}:", ASTcurrent))
        
        elif typ == "do loop":
            ASTcurrent.children.append(ASTNode("do_while", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent))

            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "collation"]
            expansion += [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and (x.token == "block" or x.token == "content_terminal")]
        
        elif typ == "func_type":
            idx = [c[0].content.index(x) for x in c[0].content if 'value' in x.__dict__][0]
            ASTcurrent.children.insert(0, ASTNode(c[0].content[idx].value, ASTcurrent))
            ASTcurrent = ASTcurrent.children[0]
        
        elif typ == "func_modif_terminal":
            ASTcurrent.children.insert(0, ASTNode(c[0].content[0].value, ASTcurrent))
        
        elif typ == "var_type":
            idx = [c[0].content.index(x) for x in c[0].content if 'value' in x.__dict__][0]
            ASTcurrent.children.insert(0, ASTNode(c[0].content[idx].value, ASTcurrent))
            ASTcurrent = ASTcurrent.children[0]
        
        elif typ == "var_modif_terminal":
            ASTcurrent.children.insert(0, ASTNode(c[0].content[0].value, ASTcurrent))
        
        elif typ == "param_terminal":
            if [x for x in c[0].content if 'content' in x.__dict__] == []:
                ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent))
        
        elif typ == "for loop":
            ASTcurrent.children.append(ASTNode("for", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]

            # Prepare the nodes for the different parts of the for loop
            ASTcurrent.children.append(ASTNode("", ASTcurrent))
            ASTcurrent.children.append(ASTNode("", ASTcurrent))
            ASTcurrent.children.append(ASTNode("", ASTcurrent))
            ASTcurrent.children.append(ASTNode("", ASTcurrent))
           
            expansion =  [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "for param 1"]
            expansion += [(x, ASTcurrent.children[1]) for x in c[0].content if 'content' in x.__dict__ and x.token == "for param 2"]
            expansion += [(x, ASTcurrent.children[2]) for x in c[0].content if 'content' in x.__dict__ and x.token == "for param 3"]
            expansion += [(x, ASTcurrent.children[3]) for x in c[0].content if 'content' in x.__dict__ and (x.token == "content_terminal" or x.token == "block")]
        
        elif typ == "switch":
            ASTcurrent.children.append(ASTNode("branch", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
           
            cases = []
            expansion = []

            # Unravel the tree in a DFS manner to retrieve all the cases 
            v = [x for x in c[0].content if 'content' in x.__dict__ and x.token == "switch_body"]
            while v != []:
                n = v[0]
                extra = []
                if n.token == "case" or n.token == "default":
                    cases.append(n)
                else:
                    extra = [x for x in n.content if 'content' in x.__dict__]

                v = extra + v[1:]

            # Store the last case body for use when there is fallthrough.
            last_cases = []
            for case in reversed(cases):
                ASTcurrent.children.insert(0, ASTNode(case.token, ASTcurrent))
                if case.token != "default":
                    ASTcurrent.children[0].children.append(ASTNode("==", ASTcurrent.children[-1]))
                    ASTcurrent.children[0].children[-1].children.append(ASTNode("var", ASTcurrent.children[-1].children[-1]))
                    ASTcurrent.children[0].children[-1].children[-1].children.append(ASTNode(c[0].content[2].content[0].content[0].content[0].value, ASTcurrent.children[0].children[-1].children[-1]))
                    ASTcurrent.children[0].children[-1].children.append(ASTNode(case.content[1].content[0].value, ASTcurrent.children[-1].children[-1]))
               
                ASTcurrent.children[0].children.append(ASTNode("body", ASTcurrent.children[-1]))

                if [x for x in case.content if 'content' in x.__dict__ and x.token == 'case_body'] == []:
                    # Add all the previous case bodies until there is a statement that break the fallthrough
                    expansion += [(x, ASTcurrent.children[0].children[-1]) for x in last_cases]
                else:
                    j = [x.token if 'content' in x.__dict__ else x.value for x in case.content].index('case_body')

                    # Check if the case will fall through or not
                    v = [x for x in case.content if 'content' in x.__dict__]
                    b = False
                    while v != []:
                        n = v[0]
                        extra = []
                        if n.token in ["break", "return", "goto"]:
                            b = True
                            break;
                        else:
                            extra = [x for x in n.content if 'content' in x.__dict__]
                        
                        v = extra + v[1:]
                    
                    if b:
                        # If there is breaking statement in the case body reset last_cases
                        last_cases = [case.content[j]]
                    else:
                        # else prepend the current case body to it because of reverse traversal of the cases
                        last_cases = [case.content[j]] + last_cases
                    
                    expansion += [(x, ASTcurrent.children[0].children[-1]) for x in last_cases]
                    
        elif typ == "block":
            ASTcurrent.children.append(ASTNode("body", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
        
        elif typ == "content_terminal":
            if ASTcurrent.name != "body" and 'content' in c[0].content[0].__dict__ and c[0].content[0].token != "block":
                ASTcurrent.children.append(ASTNode("body", ASTcurrent))
                ASTcurrent = ASTcurrent.children[-1]
        elif typ == "var_access":
            # Abstracted the access of a single value
            ASTcurrent.children.append(ASTNode("var", ASTcurrent))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent))
        else:
            pass

        if expansion == None:
            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__]

        ntv = expansion + ntv[1:]

    #Removes the blank parents from some nodes that end up blank as a result of our AST building process
    ntv = [ASTHead]
    while ntv != []:
        c = ntv[0]
        if c.parent and c.parent.name == "":
            c.parent.name = c.name
            c.parent.children = c.children + c.parent.children[1:]
        ntv = [x for x in c.children] + ntv[1:]

    return ASTHead


class ASTNode():
    """
    A class that builds an object representing the node in an AST.
    It has it's children, parent, and name.
    """
    def __init__(self, name, parent):
        """
        Constructs an ASTNode

        Args:
            name: The name of the Node (Its contents).
            parent: A node that is the parent of this current node.
        """
        self.name = name
        self.parent = parent
        self.children = []

    def print_AST(self, file=None, _prefix="", _last=True):
        """
        Prints the AST given the head

        Args:
            file: The file to be written to (Defaults to Stdout).
            _prefix: A string indicating the spacing from the left side of the screen.
            _last: A boolean that indicates if a node is the last in it's immediate surroundings.
        """
        print(f"{_prefix}{'`-- ' if _last else '|-- '}{self.name}", file=file)
        _prefix += "    " if _last else "|   "
        for i, child in enumerate(self.children):
            _last = i == len(self.children)-1
            child.print_AST(file, _prefix, _last)
        