

def buildAST(parseHead):
    head = parseHead
    ASTHead = None
    ASTcurrent = None
    ntv = [(head, ASTcurrent)]
    
    while ntv != []:
        c = ntv[0]
        typ = c[0].token
        ASTcurrent = c[1]

        expansion = None

        if typ == "program":
            ASTHead = ASTNode("Program")
            ASTcurrent = ASTHead
        elif typ == "initialization":
            ASTcurrent.children.append(ASTNode("", ASTcurrent,[]))
            ASTcurrent = ASTcurrent.children[-1]
            if len([x for x in c[0].content if 'content' in x.__dict__]) == 0:
                ASTcurrent.name = "="
                ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value} {c[0].content[1].value}", ASTcurrent, []))
                ASTcurrent.children.append(ASTNode("NULL", ASTcurrent, []))
            else:
                ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value} ", ASTcurrent, []))
        elif typ == "designation":
            # if last node was an initialization
            if ASTcurrent.name == "":
                ASTcurrent.name = c[0].content[1].content[0].value
                ASTcurrent.children[0].name += c[0].content[0].value
            else:
                ASTcurrent.children.append(ASTNode(c[0].content[1].content[0].value, ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
                ASTcurrent.children.append(ASTNode(c[0].content[0].value, ASTcurrent, []))

            # Skip the assignment node
            expansion = [(x, ASTcurrent) for x in c[0].content[1:] if 'content' in x.__dict__]            
        elif typ == "value":
            ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value}", ASTcurrent, []))

            print_AST(ASTcurrent)
        elif typ == "function definition":
            ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value} {c[0].content[1].value}", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("param", ASTcurrent, []))
            ASTcurrent.children.append(ASTNode("body", ASTcurrent, []))

            # split the content of the function definition up
            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'args'] + [(x, ASTcurrent.children[1]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'block']

        elif typ == "arg_terminal":
            ASTcurrent.children.append(ASTNode(" ".join([x.value for x in c[0].content]), ASTcurrent, []))
        elif typ == "if":
            # Check if the node is already within a branch
            if ASTcurrent.name != "branch":
                ASTcurrent.children.append(ASTNode("branch", ASTcurrent, []))
                ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("case", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent, []))
            ASTcurrent.children.append(ASTNode("body", ASTcurrent, []))

            # split the condition from the body
            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'collation'] + [(x, ASTcurrent.children[1]) for x in c[0].content if 'content' in x.__dict__ and x.token == 'if_body'] + [(x, ASTcurrent.parent) for x in c[0].content if 'content' in x.__dict__ and x.token == "if_expansion"]
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
                ASTcurrent.children.append(ASTNode(c[0].content[0].value,ASTcurrent,[]))
                pass
            pass
        elif typ == "return":
            ASTcurrent.children.append(ASTNode("return", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            # Returning a variable
            if len(c[0].content) > 0 and 'value' in c[0].content[1].__dict__:
                ASTcurrent.children.append(ASTNode(c[0].content[1].value, ASTcurrent, []))
            pass
        elif typ == "function call":
            ASTcurrent.children.append(ASTNode(f"{c[0].content[0].value} ()", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__ and x.token == "parameter"]
        elif typ == "while loop":
            ASTcurrent.children.append(ASTNode("while", ASTcurrent, []))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("", ASTcurrent, []))
            ASTcurrent.children.append(ASTNode("body", ASTcurrent, []))

            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "collation"] + [(x, ASTcurrent.children[1]) for x in c[0].content if 'content' in x.__dict__ and (x.token == "block" or x.token == "content_terminal")]
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
            ASTcurrent.children.append(ASTNode("body", ASTcurrent, []))

            expansion = [(x, ASTcurrent.children[0]) for x in c[0].content if 'content' in x.__dict__ and x.token == "collation"] + [(x, ASTcurrent.children[1]) for x in c[0].content if 'content' in x.__dict__ and (x.token == "block" or x.token == "content_terminal")]
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
        else:
            pass

        if expansion == None:
            expansion = [(x, ASTcurrent) for x in c[0].content if 'content' in x.__dict__]

        ntv = expansion + ntv[1:]

    # goto: lable colon
    # unary operators: Operator and index of child corresponds to pre or post.

    # to ensure that all nodes dont have an empty parent
    ntv = [ASTHead]

    while ntv != []:
        c = ntv[0]
        if c.parent and c.parent.name == "":
            c.parent.name = c.name
            c.parent.children = c.children + c.parent.children[1:]
            del c.parent.children[0]
        ntv = [x for x in c.children] + ntv[1:]

    return ASTHead

def print_AST(node, file=None, _prefix="", _last=True):
    print(_prefix, "`-- " if _last else "|-- ", node.name, sep="", file=file)
    _prefix += "    " if _last else "|   "
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        _last = i == (child_count - 1)
        print_AST(child, file, _prefix, _last)


class ASTNode():
    def __init__(self, name = None, parent = None, children = []):
        self.children = children
        self.parent = parent
        self.name = name