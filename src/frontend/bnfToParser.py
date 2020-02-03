import re

    
funcTemp = """
        @self.pg.production('BNFSPOT')
        def FUNCNAMESPOT(p):
            \"\"\"
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            \"\"\"
            newNode = AbstractSyntaxTree("NAMESPOT",p)
            self.Head = newNode
            return newNode
"""
headTemp = """
        @self.pg.production('BNFSPOT')
        def program(p):
            \"\"\"
            Tells the parser which BNF will be the head of the tree
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            \"\"\"
            newNode = AbstractSyntaxTree("NAMESPOT",p)
            self.Head = newNode
            return newNode
"""

initTemp = """
    def __init__(self):
        \"\"\"
        Initializes the parser and tells it the allowed tokens
        :return: This does not return anything
        \"\"\"

        self.pg = ParserGenerator(
            TOKENSPOT
        )
        #initialzie head and current node
        self.Head = None
"""

def main(path):
    """
    Creates a parser.py file from input (assumed to be BNF_definition)
    param: path: the path to the input file
    :return: This returns nothing
    """
    fi = open(path,"r")
    cont = fi.read()
    fi.close()
    reg = r'([A-Z][A-Z|_]*[A-Z])'
    reg = re.compile(reg)

    tokens = []
    for group in reg.findall(cont):
        tokens.append("'" + group + "'")
    tokens = list(dict.fromkeys(tokens))
    tokenList = "["
    jon = ","
    join = jon.join(tokens)
    tokenList += join + "]"

    initFunc = initTemp.replace("TOKENSPOT",tokenList)

    fi = open("BNF_definition","r")
    cont = fi.readlines()
    fi.close()
    functionList = ""

    for line in cont:
        if(line != "\n"):
            
            spl = line.split("#")
            bnf = spl[0]
            funcname = bnf.replace(" ","_")
            funcname = funcname.replace(":","_")
            
            name = spl[1].strip()
            if(name == "program"):
                newFunc = headTemp
            else:
                newFunc = funcTemp
            newFunc = newFunc.replace("BNFSPOT",bnf)
            newFunc = newFunc.replace("FUNCNAMESPOT",funcname)
            newFunc = newFunc.replace("NAMESPOT",name)
            
            functionList += newFunc

    totalOutput = """
from rply import ParserGenerator
from rply.errors import ParserGeneratorWarning
from warnings import simplefilter
from rply.token import Token

#we get werid 'non-descriptive' warnings from ParserGenerator, this ignores those
simplefilter('ignore', ParserGeneratorWarning)

class AbstractSyntaxTree():
    \"\"\"
    AbstractSyntaxTree is a class that acts as each node in an Abstract Syntax Tree
    \"\"\"
    def __init__(self, token, content):
        \"\"\"
        Construct a new AbstractSyntaxTree object
        :param token: the token type of the node
        :param content: the content of that is tokenized
        :return: this returns nothing
        \"\"\"
        self.token = token
        self.content = content


#setup parser class
class Parser():
    \"\"\"
    Parser is an object that contains the rules for the aprser
    \"\"\"
    INITSPOT

    def parse(self):
        \"\"\"
        The list of BNF functions and their behavior
        :return: This does not return anything
        \"\"\"
        FUNCLISTSPOT
    
        @self.pg.error
        def error_handle(token):
            \"\"\"
            Boilerplate error handling function
            param: token: the token that caused an error
            :return: There is nothing returned
            \"\"\"
            return ValueError(token)

    #boilerplate function
    def get_parser(self):
        \"\"\"
        Returns the built version of the parser
        :return: Returns the built parser
        \"\"\"
        return self.pg.build()

    #retrieve the trees head
    def getTree(self):
        \"\"\"
        Getter for the head of the tree
        :return: This returns the head of the tree
        \"\"\"

        return self.Head

    def print_error(self):
        \"\"\"
        Prints parser error message. This function ultimately iterates through the AST that was 
        returned after the parser found an error. AST's consist of tokens as well as other AST's so 
        we need to iterate to find the first token and then print its source position.
        :return: This does not return anything
        \"\"\"
        # TODO: add some more in-depth error processing to print
        # out a more detailed description of what went wrong, and possibly some suggestions 
        # at to why there was a parse/syntax error. (i.e. suggest a missing semicolon)

        head = self.getTree()
        token = 0 # token hasn't been found yet, so we set value to 0

        while True and head:
            # Iterate through list of elements
            for i in head.content:

                # Could be a Token
                if(type(i) == type(Token("sample", "sample"))):

                    # Found a Token
                    token = i
                    break

            # Check again (to break out of while loop and not iterate again)		
            if (type(token) == type(Token("sample", "sample"))):
                break
            else:
                # Set head to last element.
                # If this code executes then I can assume that the 
                # last element is an AST.
                head = head.content[len(head.content)-1]

        if token:
            print(f"ParsingError: Last token  \\\'{token.value}\\\' parsed successfully at, {token.source_pos}\\n")
        else:
            # Never found a token to report, need to exit
            print("ParsingError: No AST obtained\\n")
            exit()



    """

    totalOutput = totalOutput.replace("INITSPOT",initFunc)
    totalOutput = totalOutput.replace("FUNCLISTSPOT",functionList)

    # print (totalOutput)

    with open("parser.py", 'w') as f:
        f.write(totalOutput)

if __name__ == "__main__":
    main("BNF_definition")
