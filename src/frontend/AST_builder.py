

def buildAST(parseHead):
    head = parseHead
    ASTHead = None
    ASTcurrent = None
    ntv = [(head, ASTcurrent)]
    


    while ntv != []:
        c = ntv[0]
        typ = c[0].token
        tmpTyp = None
        sliceIndex = 0
        ASTcurrent = c[1]
        if typ == "program":
            #program : look for initializations and function definitions
            ASTHead = ASTNode("Program")
            ASTcurrent = ASTHead

        elif typ == "initialization":
            #inittialization : Look for TYPE SELF_DEFINED or TYPE designation
            tmp = ASTNode("=", ASTcurrent,[])

            ASTcurrent.children.append(tmp)
            if len([x for x in c[0].content if 'content' in x.__dict__]) == 0:
                tmp.children.append(ASTNode(f"{c[0].content[0].value} {c[0].content[1].value}",tmp,[]))
                tmp.children.append(ASTNode("NULL",tmp,[]))
            else:
                tmp.children.append(ASTNode(f"{c[0].content[0].value} ",tmp,[]))

            ASTcurrent = tmp
        elif typ == "designation":
            if(ASTcurrent.name == "="):
                ASTcurrent.children[0].name += c[0].content[0].value
                sliceIndex += 1
                ASTcurrent.children.append(ASTNode("",tmp,[]))

                ASTcurrent = ASTcurrent.children[1]


            #designation : Look for SELF_DEFINED SET and value
            
        elif typ == "value":
            #value : Look for INTEGER CHAR PRECISION
            ASTcurrent.children[-1].name += c[0].content[0].value
            pass
        elif typ == "function definition":
            #function definition : Look for TYPE SELF_DEFINED ARGS block or TYPE SELF_DEFINED block
            newNode = ASTNode(f"{c[0].content[0].value} {c[0].content[1].value}",ASTcurrent,[])
            ASTcurrent.children.append(newNode)
            ASTcurrent = newNode
            ASTcurrent.children.append(ASTNode("param",ASTcurrent,[]))
            ASTcurrent.children.append(ASTNode("body",ASTcurrent,[]))
            if (not(len([x for x in c[0].content if "content" in x.__dict__ and x.token == "args"]))):
                ASTcurrent = ASTcurrent.children[1]
            pass
        elif typ == "args":
            
            ASTcurrent = ASTcurrent.children[0]

            li = [x for x in c[0].content if 'content' in x.__dict__]
            for node in li:
                li += [x for x in node.content if 'content' in x.__dict__]
            
            for term in [x for x in li if x.token == 'arg_terminal']:
                param_name = ""
                for token in term.content:
                    param_name += token.value + " "
                ASTcurrent.children.append(ASTNode(param_name, ASTcurrent, []))

            sliceIndex += 3

            ntv[1] = (ntv[1][0], ASTcurrent.parent.children[1]) # TODO: USE DEDICATED COMMAND
            pass
        elif typ == "if":
            ASTcurrent.children.append(ASTNode("if",ASTcurrent,[]))
            ASTcurrent = ASTcurrent.children[-1]
            ASTcurrent.children.append(ASTNode("",ASTcurrent,[]))
            ASTcurrent.children.append(ASTNode("body",ASTcurrent,[]))
            ASTcurrent = ASTcurrent.children[0]
            #if : Look for collation block or collation content_terminal
            pass
        elif typ == "collation":
            # if(ASTcurrent.name == "if"):
            #     ASTcurrent = ASTcurrent.children[0]
            #     ASTcurrent.name = c[0].content[1].content[0].value
            #     #ASTcurrent.children.append(ASTNode("",ASTcurrent,[]))
            # else:
            #     #ASTcurrent = ASTcurrent.children[0]
            #     ASTcurrent.children.append()
                # pass
            #collation : Look for collation comparison collation or arithmetic
            pass
        elif typ == "comparison":
            #comparison : Look for EQ or LEQ or GEQ or NEQ or LT or GT
            ASTcurrent.name = c[0].content[0].value
            pass
        elif typ == "arithmetic":
            #arithmetic : Look for SELF_DEFINED or value or arithmetic operator arithmetic or operator arithmetic or arithmetic operator
            #print(c[0].content[0])
            tmpLen = len([x for x in c[0].content if "content" in x.__dict__])
            #for two non-terminals (i.e ARITHMETIC op ARITHMETIC)
            if(tmpLen == 2): 
                pass
            #for one non-terminals (i.e value)
            elif(tmpLen == 1):
                ASTcurrent = ASTcurrent.parent
                pass
            #for no non-terminals (i.e SELF_DEFINED)
            else:
                
                ASTcurrent.children.append(ASTNode(c[0].content[0].value,ASTcurrent,[]))

                pass
            pass
        #LKDLKEKLFELKFKLDKLFKLDF
        elif typ == "operator":
            #operator : Look for OR AND BOR XOR BAND LSH RSH ADD SUB MUL DIV MOD 
            pass
        elif typ == "return":
            #return : value or SELF_DEFINED or function call or nothing
            tmp = ASTNode("return",ASTcurrent,[])
            ASTcurrent.children.append(tmp)
            ASTcurrent = tmp
            ASTcurrent.children.append(ASTNode("",ASTcurrent,[]))
            ASTcurrent = ASTcurrent.children[0]
            pass

        else:
            pass
        ntv = [(x, ASTcurrent) for x in c[0].content[sliceIndex:] if 'content' in x.__dict__] + ntv[1:]

    pprint_tree(ASTHead)

def pprint_tree(node, file=None, _prefix="", _last=True):
    print(_prefix, "`-- " if _last else "|-- ", node.name, sep="", file=file)
    _prefix += "    " if _last else "|   "
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        _last = i == (child_count - 1)
        pprint_tree(child, file, _prefix, _last)


class ASTNode():
    def __init__(self, name = None, parent = None, children = []):
        self.children = children
        self.parent = parent
        self.name = name