"""
This module reads in a BNF and produces a parser for use with rply.The BNF expects the form X : Y Y #name, where the name determines what the node will end up being called in the Parse tree.
"""

import re
import os

    
funcTemp = """
        @self.pg.production('BNFSPOT')
        def FUNCNAMESPOT(p):
            newNode = ParseTree("NAMESPOT",p)
            self.Head = newNode
            return newNode
"""
headTemp = """
        @self.pg.production('BNFSPOT')
        def program(p):
            \"\"\"
            Tells the parser which BNF will be the head of the tree
            
            Args:
                p: The matching set of tokens.

            Returns:
                The node of the ParseTree.
            \"\"\"
            newNode = ParseTree("NAMESPOT",p)
            self.Head = newNode
            return newNode
"""

initTemp = """
    def __init__(self):
        \"\"\"
        Initializes the parser and tells it the allowed tokens

        \"\"\"

        self.pg = ParserGenerator(
            TOKENSPOT , 
            precedence=[
                ('right', ['SET', 'AEQ', 'SEQ', 'MEQ', 'DEQ', 'MODEQ', 'LSEQ', 'RSEQ', 'BAEQ', 'XEQ', 'BOEQ']),
                ('left',  ['OR']),
                ('left',  ['AND']),
                ('left',  ['BOR']),
                ('left',  ['XOR']),
                ('left',  ['BAND']),
                ('left',  ['EQ', 'NEQ']),
                ('left',  ['GE', 'GEQ']),
                ('left',  ['LE', 'LEQ']),
                ('left',  ['LSH', 'RSH']),
                ('left',  ['ADD', 'SUB']),
                ('left',  ['MUL', 'DIV', 'MOD']),
                ('right', ['INC', 'DEC', 'NOT', 'COMP']),
            ]
        )
        #initialzie head and current node
        self.Head = None
"""

def main(path):
    """
    Creates a parser.py file from input. While the default is more or less BNF_definition (as it is passed in inside this files __main__ block) the function assumes no default

    Args:
        path: the path to the input file
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

    fi = open(path,"r")
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
\"\"\"
This module contains definitions for the ParseTree and Parser classes, as well as some ansillary functions to assist.
\"\"\"
from rply import ParserGenerator
from rply.errors import ParserGeneratorWarning
from warnings import simplefilter
from rply.token import Token

#we get werid 'non-descriptive' warnings from ParserGenerator, this ignores those
simplefilter('ignore', ParserGeneratorWarning)

class ParseTree():
    \"\"\"
    ParseTree is a class that acts as each node in an ParseTree
    \"\"\"
    def __init__(self, token, content):
        \"\"\"
        Construct a new ParseTree object

        Args:
            token: The token type of the node.
            content: The content of that is tokenized.
        \"\"\"
        self.token = token
        self.content = content


#setup parser class
class Parser():
    \"\"\"
    Definition for the Parser object, works off of rply. Contains rules for parsing.
    \"\"\"
    INITSPOT

    def parse(self):
        \"\"\"
        The list of BNF functions and their behavior
        \"\"\"
        FUNCLISTSPOT
    
        @self.pg.error
        def error_handle(token):
            \"\"\"
            Boilerplate error handling function
            
            Args:
                token: The token that caused an error.
            \"\"\"
            return ValueError(token)

    #boilerplate function
    def get_parser(self):
        \"\"\"
        Retrieves the built version of the parser.

        Returns:
            The built parser.
        \"\"\"
        return self.pg.build()

    #retrieve the trees head
    def getTree(self):
        \"\"\"
        Getter for the head of the tree.

        Returns:
            The head of the tree.
        \"\"\"

        return self.Head

    def print_error(self):
        \"\"\"
        Prints parser error message. This function ultimately iterates through the ParseTree that was returned after the parser found an error. ParseTree's consist of tokens as well as other ParseTree's so we need to iterate to find the first token and then print its source position.
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
                # last element is an ParseTree.
                head = head.content[len(head.content)-1]

        if token:
            print(f"ParsingError: Last token  \\\'{token.value}\\\' parsed successfully at, {token.source_pos}\\n")
        else:
            # Never found a token to report, need to exit
            print("ParsingError: No ParseTree obtained\\n")
            exit()



    """

    totalOutput = totalOutput.replace("INITSPOT",initFunc)
    totalOutput = totalOutput.replace("FUNCLISTSPOT",functionList)

    print("Overwriting ")
    with open(os.path.dirname(__file__) + "/parser.py", 'w') as f:
        f.write(totalOutput)

if __name__ == "__main__":
    #default is assumed to be BNF definition if not otherwise specified
    main("BNF_definition")
