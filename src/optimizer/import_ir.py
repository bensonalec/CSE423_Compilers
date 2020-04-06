"""
This module handle ir input from a file
"""
from rply import LexerGenerator
from rply.errors import LexingError
from copy import deepcopy
import IRLine
import re
#TODO: ADD TOKEN FOR KEYWORDS, MAKE THE PARSING ACTUALLY PARSE INTO IRNODES


class import_ir():

        

        
    def __init__(self, filename):
        with open(filename,"r") as fd:
            self.data = fd.read()
            self.tokens = None
    def tokenize(self):
        
        text_input = self.data.strip()
        #final = ""

        #text_input = final
        lexer = IR_Lexer().get_lexer()
        tokens = lexer.lex(text_input)
        self.tokens = tokens
        # print(tokensToString(deepcopy(tokens)))

    def parse(self):
        pg = Parser()
        pg.parse()
        parser = pg.get_parser()
        parser.parse(self.tokens)

        # Retrieve the head of the parse tree
        head = pg.getTree()
        for i in pg.ls:
            print(str(i))
        #print(str(pg.ls))
        # print(head.__repr__)

def tokensToString(tokens):
    """
    Iterates through the tokens and generates a string of all of them

    Args:
        tokens: The token object that is returned from the lexer.
    """
    return "\n".join([str(x) for x in tokens])


class IR_Lexer():
    """
    The lexer class definition
    """
    def __init__(self):
        """
        Constructs the Lexer object.
        """
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        """
        Adds tokens to the rply lexer object
        """
        self.lexer.add("D_NUM", r"D\.[0-9]*")
        self.lexer.add("INT",r"([1-9]\d*|\d)")
        self.lexer.add("FLOAT",r"(\d|[1-9]\d+)\.\d*")
        self.lexer.add("CHAR",r"\'\\?[\w\;\\ \%\"\']\'")
        self.lexer.add("STRING",r"(\"[^\n]*?(?<!\\)\")|(\'[^\n]*?(?<!\\)\')")
        self.lexer.add("PLUS",r"\+")
        self.lexer.add("MINUS",r"-")
        self.lexer.add("DIVIDE",r"/")
        self.lexer.add("TIMES",r"\*")
        self.lexer.add("MODULUS",r"%")
        self.lexer.add("LEFT_SHIFT",r"<<")
        self.lexer.add("RIGHT_SHIFT",r">>")
        self.lexer.add("NOT_EQUAL_TO",r"!=")
        self.lexer.add("NOT",r"!")
        self.lexer.add("XOR",r"\^")
        self.lexer.add("NEGATE",r"~")
        self.lexer.add("SEMICOLON",r";")
        self.lexer.add("RETURN",r"\breturn\b")
        self.lexer.add("GOTO",r"\bgoto\b")
        self.lexer.add("IF",r"\bif\b")
        self.lexer.add("ELSE",r"\belse\b")
        self.lexer.add("GEQ",r">=")
        self.lexer.add("LEQ",r"<=")
        self.lexer.add("GREATER_THAN",r">")
        self.lexer.add("LESS_THAN",r"<")
        self.lexer.add("EQUAL_TO",r"={2}")
        self.lexer.add("EQUALS",r"=")
        self.lexer.add("NULL",r"\bNULL\b")
        self.lexer.add("KEYWORD","\b(const|signed|static|unsigned|extern)\b")
        self.lexer.add("COMMA",r",")
        self.lexer.add("COLON",r":")
        self.lexer.add("AND",r"&{2}")
        self.lexer.add("OR",r"\|{2}")
        self.lexer.add("BW_AND",r"&")
        self.lexer.add("BW_OR",r"\|")
        self.lexer.add("TYPE",r"\b(auto|long double|double|float|long long( int)?|long|int|short|char|void)\b")
        self.lexer.add("VAR_NAME",r"[a-zA-Z_]\w*")
        self.lexer.add("OPEN_PAREN",r"\(")
        self.lexer.add("CLOSE_PAREN",r"\)")
        self.lexer.add("OPEN_BRACK",r"\{")
        self.lexer.add("CLOSE_BRACK",r"\}")
        self.lexer.ignore(r'\s+')
        self.lexer.ignore(r'\n')
        self.lexer.ignore(r'\t')


    def get_lexer(self):
        """
        Retrieves the lexer, with the tokens added to the inner lexer object.

        Returns:
            The lexer, now built with the tokens added
        """
        self._add_tokens()
        return self.lexer.build()

def print_error(token):
    """
    Prints lexer error message. Currently we only experience invalid token
    errors. The input `token` is a `Token` object, imported from `rply`.

    Args:
        token: The token object that is returned from the lexer.
    """
    print(f"LexingError: Invalid Token \'{token.value}\' at, {token.source_pos}\n")





"""
This module contains definitions for the ParseTree and Parser classes, as well as some ansillary functions to assist.
"""
from rply import ParserGenerator
from rply.errors import ParserGeneratorWarning
from warnings import simplefilter
from rply.token import Token

#we get werid 'non-descriptive' warnings from ParserGenerator, this ignores those
simplefilter('ignore', ParserGeneratorWarning)

class ParseTree():
    """
    ParseTree is a class that acts as each node in an ParseTree
    """
    def __init__(self, token, content):
        """
        Construct a new ParseTree object

        Args:
            token: The token type of the node.
            content: The content of that is tokenized.
        """
        self.token = token
        self.content = content

    def print_ParseTree(self, file=None, _prefix="", _last=True):
        """
        Prints the ParseTree in depth first order

        Args:
            file: The file to be written to (Defaults to Stdout).
            _prefix: A string indicating the spacing from the left side of the screen.
            _last: A boolean that indicates if a self is the last in it's immediate surroundings.
        """
        print(f"{_prefix}{'`-- ' if _last else '|-- '}{self.token}", file=file)
        _prefix += "    " if _last else "|   "
        for i, child in enumerate(self.content):
            _last = i == len(self.content)-1
            if 'content' in child.__dict__:
                child.print_ParseTree(file, _prefix, _last)
            else:
                print(f"{_prefix}{'`-- ' if _last else '|-- '}{child}", file=file)

    def __str__(self):
        """
        Produces a string representation of the Parse Tree
        """
        li = []

        ntv = [("", self, True)]

        while ntv:
            li.append(ntv[0])

            ntv = [(f"{ntv[0][0]}{'    ' if ntv[0][2] else '|   '}", x, i == len(ntv[0][1].content)-1 ) for i, x in enumerate(ntv[0][1].content)] + ntv[1:] if 'content' in ntv[0][1].__dict__ else ntv[1:]

        return "".join([f"{x[0]}{'`-- ' if x[2] else '|-- '}{x[1].token if 'token' in x[1].__dict__ else x[1]}" for x in li]) + ""

    def __repr__(self):
        """
        Constructs a list based string representation of the parse tree
        """

        li = []

        ntv = [(1, self)]

        while ntv:
            li.append((ntv[0][0], ntv[0][1].content))

            ntv = [(ntv[0][0]+1, x) for x in ntv[0][1].content if 'content' in x.__dict__] + ntv[1:]

        return "".join([f"{x[0]} : {[y.token if 'content' in y.__dict__ else y for y in x[1]]}" for x in li])

    def getListView(self, level):
        """
        Prints a simple list version of the tree for output. Calls itself recursively

        Args:
            level: The current level of the tree.
        """

        li = []
        li.append(f"{level+1} : {[x if 'content' not in x.__dict__ else x.token for x in self.content]}")

        for x in self.content:
            if "content" in x.__dict__:
                li.extend(x.getListView(level+1))

        if level == 0:
            return "".join(li)
        return li

#setup parser class
class Parser():
    """
    Definition for the Parser object, works off of rply. Contains rules for parsing.
    """
    
    def __init__(self):
        """
        Initializes the parser and tells it the allowed tokens

        """

        self.pg = ParserGenerator(
            ['PROGRAM','VAR_NAME','OPEN_PAREN','CLOSE_PAREN','OPEN_BRACK','CLOSE_BRACK','FUNCTION_DEF','TYPE','COMMA','PARAMATERS','PARAMETERS','CONTENT','D_NUM','SEMICOLON','LINE','EQUALS','STRING','CHAR','MINUS','PLUS','NEGATE','NOT','NULL','RETURN','IF','GOTO','LESS_THAN','GREATER_THAN','ELSE','COLON','KEWORD','CONDITION','FUNC_CALL','FUNC_INPUT','COMP','EQUAL_TO','LEQ','GEQ','NOT_EQUAL_TO','OP','DIVIDE','TIMES','MODULUS','BW_AND','BW_OR','LEFT_SHIFT','RIGHT_SHIFT','XOR','INT','DIG','FLOAT'] ,
        )
        #initialzie head and current node
        self.Head = None
        self.ls = []


    def parse(self):
        """
        The list of BNF functions and their behavior
        """
        
        @self.pg.production('program : function_def ')
        def program___function_def_(p):
            newNode = ParseTree("PROGRAM",p)
            self.Head = newNode
            return newNode

        @self.pg.production('program : function_def program ')
        def program___function_def_program_(p):
            newNode = ParseTree("PROGRAM",p)
            self.Head = newNode
            return newNode

        @self.pg.production('program :  ')
        def program____(p):
            newNode = ParseTree("PROGRAM",p)
            self.Head = newNode
            return newNode

        @self.pg.production('function_def : VAR_NAME OPEN_PAREN parameters CLOSE_PAREN OPEN_BRACK content CLOSE_BRACK ')
        def function_def___VAR_NAME_OPEN_PAREN_parameters_CLOSE_PAREN_OPEN_BRACK_content_CLOSE_BRACK_(p):

            newNode = ParseTree("FUNCTION_DEF",p)
            self.Head = newNode
            #first, convert parameters to a string form
            #also, get the string representation of VAR_NAME
            
            tokens = []
            tokens += [x.value for x in p[2].content if isinstance(x,Token)]
            tokenSets = [x for x in p[2].content if isinstance(x,ParseTree)]
            while tokenSets != []:
                for i in tokenSets:
                    tokens += [x.value for x in i.content if isinstance(x,Token)]
                    tokenSets = [x for x in i.content if isinstance(x,ParseTree)]
            
            
            functioName = p[0].value
            params = " ".join(tokens)
            IRNodeToReturn = IRLine.IRFunctionDecl(functioName,params)
            self.ls.append(IRNodeToReturn)
            return newNode

        @self.pg.production('parameters : TYPE VAR_NAME COMMA parameters ')
        def parameters___TYPE_VAR_NAME_COMMA_parameters_(p):
            newNode = ParseTree("PARAMATERS",p)
            self.Head = newNode
            return newNode

        @self.pg.production('parameters : TYPE VAR_NAME ')
        def parameters___TYPE_VAR_NAME_(p):
            newNode = ParseTree("PARAMETERS",p)
            self.Head = newNode
            return newNode

        @self.pg.production('parameters : ')
        def parameters___(p):
            newNode = ParseTree("PARAMETERS",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : line ')
        def content___line_(p):
            newNode = ParseTree("CONTENT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : content content ')
        def content___content_content_(p):
            newNode = ParseTree("CONTENT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : ')
        def content___(p):
            newNode = ParseTree("CONTENT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : OPEN_BRACK content CLOSE_BRACK ')
        def content___OPEN_BRACK_content_CLOSE_BRACK_(p):
            newNode = ParseTree("CONTENT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : TYPE D_NUM SEMICOLON ')
        def line___TYPE_D_NUM_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : TYPE VAR_NAME SEMICOLON ')
        def line___TYPE_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            #needs modifiers, type, and varname
            #modifiers is none
            typ = p[0]
            name = p[1]
            IRNodeToReturn = IRLine.IRVariableInit("",typ.value, name.value)
            self.ls.append(IRNodeToReturn)
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS dig op dig SEMICOLON ')
        def line___VAR_NAME_EQUALS_dig_op_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS VAR_NAME SEMICOLON ')
        def line___VAR_NAME_EQUALS_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS dig SEMICOLON ')
        def line___VAR_NAME_EQUALS_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS STRING SEMICOLON ')
        def line___VAR_NAME_EQUALS_STRING_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS CHAR SEMICOLON ')
        def line___VAR_NAME_EQUALS_CHAR_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS VAR_NAME op dig SEMICOLON ')
        def line___VAR_NAME_EQUALS_VAR_NAME_op_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS dig op VAR_NAME SEMICOLON ')
        def line___VAR_NAME_EQUALS_dig_op_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS VAR_NAME op VAR_NAME SEMICOLON ')
        def line___VAR_NAME_EQUALS_VAR_NAME_op_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS MINUS dig SEMICOLON ')
        def line___VAR_NAME_EQUALS_MINUS_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS MINUS VAR_NAME SEMICOLON ')
        def line___VAR_NAME_EQUALS_MINUS_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS PLUS dig SEMICOLON ')
        def line___VAR_NAME_EQUALS_PLUS_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS PLUS VAR_NAME SEMICOLON ')
        def line___VAR_NAME_EQUALS_PLUS_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS NEGATE dig SEMICOLON ')
        def line___VAR_NAME_EQUALS_NEGATE_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS NOT dig SEMICOLON ')
        def line___VAR_NAME_EQUALS_NOT_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS NOT VAR_NAME SEMICOLON ')
        def line___VAR_NAME_EQUALS_NOT_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS NEGATE VAR_NAME SEMICOLON ')
        def line___VAR_NAME_EQUALS_NEGATE_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS NULL SEMICOLON ')
        def line___VAR_NAME_EQUALS_NULL_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : D_NUM EQUALS VAR_NAME SEMICOLON ')
        def line___D_NUM_EQUALS_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : D_NUM EQUALS dig SEMICOLON ')
        def line___D_NUM_EQUALS_dig_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : D_NUM EQUALS STRING SEMICOLON ')
        def line___D_NUM_EQUALS_STRING_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : D_NUM EQUALS CHAR SEMICOLON ')
        def line___D_NUM_EQUALS_CHAR_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : RETURN D_NUM SEMICOLON ')
        def line___RETURN_D_NUM_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : func_call SEMICOLON ')
        def line___func_call_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME EQUALS func_call SEMICOLON ')
        def line___VAR_NAME_EQUALS_func_call_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : IF OPEN_PAREN condition CLOSE_PAREN GOTO LESS_THAN D_NUM GREATER_THAN SEMICOLON ELSE GOTO LESS_THAN D_NUM GREATER_THAN SEMICOLON ')
        def line___IF_OPEN_PAREN_condition_CLOSE_PAREN_GOTO_LESS_THAN_D_NUM_GREATER_THAN_SEMICOLON_ELSE_GOTO_LESS_THAN_D_NUM_GREATER_THAN_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : LESS_THAN D_NUM GREATER_THAN COLON ')
        def line___LESS_THAN_D_NUM_GREATER_THAN_COLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : GOTO LESS_THAN D_NUM GREATER_THAN SEMICOLON ')
        def line___GOTO_LESS_THAN_D_NUM_GREATER_THAN_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : GOTO VAR_NAME SEMICOLON ')
        def line___GOTO_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : VAR_NAME COLON ')
        def line___VAR_NAME_COLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : KEWORD TYPE VAR_NAME SEMICOLON ')
        def line___KEWORD_TYPE_VAR_NAME_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('line : RETURN SEMICOLON ')
        def line___RETURN_SEMICOLON_(p):
            newNode = ParseTree("LINE",p)
            self.Head = newNode
            return newNode

        @self.pg.production('condition : VAR_NAME comp VAR_NAME ')
        def condition___VAR_NAME_comp_VAR_NAME_(p):
            newNode = ParseTree("CONDITION",p)
            self.Head = newNode
            return newNode

        @self.pg.production('condition : VAR_NAME comp dig ')
        def condition___VAR_NAME_comp_dig_(p):
            newNode = ParseTree("CONDITION",p)
            self.Head = newNode
            return newNode

        @self.pg.production('condition : dig comp dig ')
        def condition___dig_comp_dig_(p):
            newNode = ParseTree("CONDITION",p)
            self.Head = newNode
            return newNode

        @self.pg.production('condition : dig comp VAR_NAME ')
        def condition___dig_comp_VAR_NAME_(p):
            newNode = ParseTree("CONDITION",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_call : VAR_NAME OPEN_PAREN func_input CLOSE_PAREN ')
        def func_call___VAR_NAME_OPEN_PAREN_func_input_CLOSE_PAREN_(p):
            newNode = ParseTree("FUNC_CALL",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : ')
        def func_input___(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : STRING COMMA func_input ')
        def func_input___STRING_COMMA_func_input_(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : CHAR COMMA func_input ')
        def func_input___CHAR_COMMA_func_input_(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : dig COMMA func_input ')
        def func_input___dig_COMMA_func_input_(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : VAR_NAME COMMA func_input ')
        def func_input___VAR_NAME_COMMA_func_input_(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : STRING  ')
        def func_input___STRING__(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : CHAR  ')
        def func_input___CHAR__(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : dig  ')
        def func_input___dig__(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_input : VAR_NAME ')
        def func_input___VAR_NAME_(p):
            newNode = ParseTree("FUNC_INPUT",p)
            self.Head = newNode
            return newNode

        @self.pg.production('comp : LESS_THAN ')
        def comp___LESS_THAN_(p):
            newNode = ParseTree("COMP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('comp : GREATER_THAN ')
        def comp___GREATER_THAN_(p):
            newNode = ParseTree("COMP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('comp : EQUAL_TO ')
        def comp___EQUAL_TO_(p):
            newNode = ParseTree("COMP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('comp : LEQ ')
        def comp___LEQ_(p):
            newNode = ParseTree("COMP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('comp : GEQ ')
        def comp___GEQ_(p):
            newNode = ParseTree("COMP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('comp : NOT_EQUAL_TO ')
        def comp___NOT_EQUAL_TO_(p):
            newNode = ParseTree("COMP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : PLUS ')
        def op___PLUS_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : MINUS ')
        def op___MINUS_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : DIVIDE ')
        def op___DIVIDE_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : TIMES ')
        def op___TIMES_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : MODULUS ')
        def op___MODULUS_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : BW_AND ')
        def op___BW_AND_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : BW_OR ')
        def op___BW_OR_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : NEGATE ')
        def op___NEGATE_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : LEFT_SHIFT ')
        def op___LEFT_SHIFT_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : RIGHT_SHIFT ')
        def op___RIGHT_SHIFT_(p):
            newNode = ParseTree("OP",p)
            self.Head = newNode
            return newNode

        @self.pg.production('op : XOR ')
        def op___XOR_(p):
            newNode = ParseTree("",p)
            self.Head = newNode
            return newNode

        @self.pg.production('dig : INT ')
        def dig___INT_(p):
            newNode = ParseTree("DIG",p)
            self.Head = newNode
            return newNode

        @self.pg.production('dig : FLOAT ')
        def dig___FLOAT_(p):
            newNode = ParseTree("DIG",p)
            self.Head = newNode
            return newNode


        @self.pg.error
        def error_handle(token):
            """
            Boilerplate error handling function

            Args:
                token: The token that caused an error.
            """
            return ValueError(token)

    #boilerplate function
    def get_parser(self):
        """
        Retrieves the built version of the parser.

        Returns:
            The built parser.
        """
        return self.pg.build()

    #retrieve the trees head
    def getTree(self):
        """
        Getter for the head of the tree.

        Returns:
            The head of the tree.
        """

        return self.Head

    def print_error(self):
        """
        Prints parser error message. This function ultimately iterates through the ParseTree that was returned after the parser found an error. ParseTree's consist of tokens as well as other ParseTree's so we need to iterate to find the first token and then print its source position.
        """
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
            print(f"ParsingError: Last token  \'{token.value}\' parsed successfully at, {token.source_pos}\n")
        else:
            # Never found a token to report, need to exit
            print("ParsingError: No ParseTree obtained\n")
            exit()



    
