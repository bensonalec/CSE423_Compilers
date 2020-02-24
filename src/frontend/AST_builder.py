"""
This module takes in the parse tree, and produces an Abstract Syntax Tree. 
This is done using a Depth First Traversal. By taking the Concrete Syntax Tree (Parse Tree) 
and converting it to an Abstract Syntax Tree we can begin to move towards an intermediate form.
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
            ASTHead = ASTNode("program")
            ASTcurrent = ASTHead
        elif typ == "initialization":
            ASTcurrent.children.append(ASTNode("", ASTcurrent,[]))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("var", ASTcurrent, []))
            if len([x for x in c[0].content if 'content' in x.__dict__]) == 0:
                ASTcurrent.name = "="
                ASTcurrent.children[-1].children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))
                ASTcurrent.children[-1].children.append(ASTNode(c[0].content[1].value, ASTcurrent, []))
                ASTcurrent.children.append(ASTNode("NULL", ASTcurrent, []))
            else:
                ASTcurrent.children[-1].children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))
        elif typ == "designation":
            # if last node was an initialization
            if ASTcurrent.name == "":
                ASTcurrent.name = c[0].content[1].content[0].value
                ASTcurrent.children[0].children.append(ASTNode(c[0].content[0].value, ASTcurrent.children[0], [])) 
            else:
                ASTcurrent.children.append(ASTNode(c[0].content[1].content[0].value, ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
                ASTcurrent.children.append(ASTNode("var", ASTcurrent, []))
                ASTcurrent.children[-1].children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))

            # Skip the assignment node
            expansion = [(x, ASTcurrent) for x in c[0].content[1:] if 'content' in x.__dict__]            
        elif typ == "value":
            ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value}", ASTcurrent, []))
        elif typ == "function definition":
            ASTcurrent.children.append(ASTNode("func", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent, []))
            ASTcurrent.children.append(ASTNode("param", ASTcurrent, []))

            # split the content of the function definition up
            expansion = [(x, ASTcurrent.children[2]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'args'] + [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == 'block']
        elif typ == "functionDeclaration":
            ASTcurrent.children.append(ASTNode("decl", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent, []))
            ASTcurrent.children.append(ASTNode("param", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
        elif typ == "arg_terminal":
            ASTcurrent.children.append(ASTNode("var", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent, []))
            # ASTcurrent.children.append(ASTNode(" ".join([x.value for x in c[0].content]), ASTcurrent, []))
        elif typ == "if":
            # Check if the node is already within a branch
            if ASTcurrent.name != "branch":
                ASTcurrent.children.append(ASTNode("branch", ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("case", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent, []))

            # split the condition from the body
            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'collation'] + [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == 'if_body'] + [(x, ASTcurrent.parent) for x in c[0].content if 'content' in x.__dict__ and x.token == "if_expansion"]
        elif typ == "if_expansion":
            # Check if it's the last else in the if statement
            if not (c[0].content[1].content[0].token == 'content_terminal' and c[0].content[1].content[0].content[0].token == "if"):
                ASTcurrent.children.append(ASTNode("default", ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
        elif typ == "comparison":
            ASTcurrent.name = c[0].content[0].value
            pass
        elif typ == "arithmetic":
            tmpLen = len([x for x in c[0].content if "content" in x.__dict__])

            #for two non-terminals (i.e ARITHMETIC op ARITHMETIC)
            if(tmpLen == 2): 
                ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
            
            #for one non-terminals (i.e value)
            elif(tmpLen == 1):
                pass
            #for no non-terminals (i.e SELF_DEFINED)
            else:
                ASTcurrent.children.append(ASTNode("var", ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
                ASTcurrent.children.append(ASTNode(c[0].content[0].value,ASTcurrent,[]))
                pass
            pass
        elif typ == "return":
            ASTcurrent.children.append(ASTNode("return", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            pass
        elif typ == "function call":
            ASTcurrent.children.append(ASTNode("call", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == "parameter"]
        elif typ == "while loop":
            ASTcurrent.children.append(ASTNode("while", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent, []))

            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "collation"] + [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and (x.token == "block" or x.token == "content_terminal")]
            pass
        elif typ == "break":
            ASTcurrent.children.append(ASTNode("break", ASTcurrent, []))
        elif typ == "jump":
            ASTcurrent.children.append(ASTNode("goto", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent, []))
        elif typ == "goto":
            ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value}:", ASTcurrent, []))
        elif typ == "do loop":
            ASTcurrent.children.append(ASTNode("do_while", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent, []))

            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "collation"] + [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and (x.token == "block" or x.token == "content_terminal")]
        elif typ == "unary":
            if len([x for x in c[0].content if 'content' in x.__dict__]):
                index = [x for x in range(2) if x != [y.token if 'content' in y.__dict__ else y.name for y in c[0].content].index("arithmetic")][0]
                ASTcurrent.children.append(ASTNode(c[0].content[index].value, ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
            else:
                op_index = [x for x in range(2) if x != [y.name for y in c[0].content].index("SELF_DEFINED")][0]
                ASTcurrent.children.append(ASTNode(c[0].content[op_index].value, ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
                ASTcurrent.children.append(ASTNode("NULL", ASTcurrent ,[]))
                ASTcurrent.children.insert(op_index ^ 1, ASTNode(c[0].content[op_index ^ 1].value, ASTcurrent, []))
            pass
        elif typ == "block":
            ASTcurrent.children.append(ASTNode("body", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
        elif typ == "content_terminal":
            if ASTcurrent.name != "body" and 'content' in c[0].content[0].__dict__ and c[0].content[0].token != "block":
                ASTcurrent.children.append(ASTNode("body", ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
        else:
            pass

        if expansion == None:
            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__]

        ntv = expansion + ntv[1:]

    # goto: lable colon
    # unary operators: Operator and index of child corresponds to pre or post.

    # to ensure that all nodes dont have an empty parent
    ntv = [ASTHead]

    #Removes the blank parents from some nodes that end up blank as a result of our AST building process
    while ntv != []:
        c = ntv[0]
        if c.parent and c.parent.name == "":
            c.parent.name = c.name
            c.parent.children = c.children + c.parent.children[1:]
        ntv = [x for x in c.children] + ntv[1:]



    return ASTHead

def print_AST(node, file=None, _prefix="", _last=True):
    """
    Prints the AST given the head

    Args: 
        node: The head node of the tree.
        file: The file to be written to (Defaults to Stdout).
        _prefix: A string indicating the spacing from the left side of the screen.
        _last: A boolean that indicates if a node is the last in it's immediate surroundings.
    """
    print(_prefix, "`-- " if _last else "|-- ", node.name, sep="", file=file)
    _prefix += "    " if _last else "|   "
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        _last = i == (child_count - 1)
        print_AST(child, file, _prefix, _last)


class ASTNode():
    """
    A class that builds an object representing the node in an AST. 
    It has it's children, parent, and name.
    """
    def __init__(self, name = None, parent = None, children = []):
        """
        Constructs an ASTNode

        Args: 
            name: The name of the Node (Its contents).
            parent: A node that is the parent of this current node.
            children: The children of this node (In a list).
        """
        self.children = children
        self.parent = parent
        self.name = name