
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

        return "\n".join([f"{x[0]}{'`-- ' if x[2] else '|-- '}{x[1].token if 'token' in x[1].__dict__ else x[1]}" for x in li]) + "\n"

    def __repr__(self):
        """
        Constructs a list based string representation of the parse tree
        """

        li = []

        ntv = [(1, self)]

        while ntv:
            li.append((ntv[0][0], ntv[0][1].content))

            ntv = [(ntv[0][0]+1, x) for x in ntv[0][1].content if 'content' in x.__dict__] + ntv[1:]

        return "\n".join([f"{x[0]} : {[y.token if 'content' in y.__dict__ else y for y in x[1]]}" for x in li])

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
            return "\n".join(li)
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
            ['COMMENT','SELF_DEFINED','OPEN_PAREN','CLOSE_PAREN','SEMICOLON','TYPE','FUNC_MODIF','BOTH_MODIF','VAR_MODIF','COMMA','OPEN_BRACK','CLOSE_BRACK','OPEN_BRACE','CLOSE_BRACE','STRING','WHILE_LOOP','FOR_LOOP','DO_LOOP','IF_BRANCH','ELSE_BRANCH','SWITCH_BRANCH','CASE','COLON','DEFAULT','RETURN','GOTO','BREAK','CONTINUE','SET','INTEGER','MUL','AEQ','SEQ','MEQ','DEQ','MODEQ','LSEQ','RSEQ','BOEQ','BAEQ','XEQ','OR','AND','BOR','XOR','BAND','EQ','NEQ','LT','GT','LEQ','GEQ','LSH','RSH','ADD','SUB','DIV','MOD','INC','DEC','SIZEOF','COMP','NOT','PRECISION','CHAR','HEX','OCT','BIN','NULL'] ,
        )
        #initialzie head and current node
        self.Head = None


    def parse(self):
        """
        The list of BNF functions and their behavior
        """

        @self.pg.production('program : definitionList ')
        def program(p):
            """
            Tells the parser which BNF will be the head of the tree

            Args:
                p: The matching set of tokens.

            Returns:
                The node of the ParseTree.
            """
            newNode = ParseTree("program",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definitionList : definition_terminal definitionList ')
        def definitionList___definition_terminal_definitionList_(p):
            newNode = ParseTree("definitionList",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definitionList : definition_terminal ')
        def definitionList___definition_terminal_(p):
            newNode = ParseTree("definitionList",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definition_terminal : functionDefinition ')
        def definition_terminal___functionDefinition_(p):
            newNode = ParseTree("definition_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definition_terminal : functionDeclaration ')
        def definition_terminal___functionDeclaration_(p):
            newNode = ParseTree("definition_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definition_terminal : initialization ')
        def definition_terminal___initialization_(p):
            newNode = ParseTree("definition_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definition_terminal : COMMENT ')
        def definition_terminal___COMMENT_(p):
            newNode = ParseTree("definition_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDefinition : func_type SELF_DEFINED OPEN_PAREN args CLOSE_PAREN block ')
        def functionDefinition___func_type_SELF_DEFINED_OPEN_PAREN_args_CLOSE_PAREN_block_(p):
            newNode = ParseTree("function definition",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDefinition : func_type SELF_DEFINED OPEN_PAREN CLOSE_PAREN block ')
        def functionDefinition___func_type_SELF_DEFINED_OPEN_PAREN_CLOSE_PAREN_block_(p):
            newNode = ParseTree("function definition",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDeclaration : func_type SELF_DEFINED OPEN_PAREN args CLOSE_PAREN SEMICOLON ')
        def functionDeclaration___func_type_SELF_DEFINED_OPEN_PAREN_args_CLOSE_PAREN_SEMICOLON_(p):
            newNode = ParseTree("functionDeclaration",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDeclaration : func_type SELF_DEFINED OPEN_PAREN CLOSE_PAREN SEMICOLON ')
        def functionDeclaration___func_type_SELF_DEFINED_OPEN_PAREN_CLOSE_PAREN_SEMICOLON_(p):
            newNode = ParseTree("functionDeclaration",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_type : TYPE ')
        def func_type___TYPE_(p):
            newNode = ParseTree("func_type",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_type : func_modif TYPE ')
        def func_type___func_modif_TYPE_(p):
            newNode = ParseTree("func_type",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_modif : func_modif_terminal ')
        def func_modif___func_modif_terminal_(p):
            newNode = ParseTree("func_modif",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_modif : func_modif_terminal func_modif ')
        def func_modif___func_modif_terminal_func_modif_(p):
            newNode = ParseTree("func_modif",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_modif_terminal : FUNC_MODIF ')
        def func_modif_terminal___FUNC_MODIF_(p):
            newNode = ParseTree("func_modif_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('func_modif_terminal : BOTH_MODIF ')
        def func_modif_terminal___BOTH_MODIF_(p):
            newNode = ParseTree("func_modif_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_modif : var_modif_terminal ')
        def var_modif___var_modif_terminal_(p):
            newNode = ParseTree("var_modif",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_modif : var_modif_terminal var_modif ')
        def var_modif___var_modif_terminal_var_modif_(p):
            newNode = ParseTree("var_modif",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_modif_terminal : VAR_MODIF ')
        def var_modif_terminal___VAR_MODIF_(p):
            newNode = ParseTree("var_modif_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_modif_terminal : BOTH_MODIF ')
        def var_modif_terminal___BOTH_MODIF_(p):
            newNode = ParseTree("var_modif_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : arg_terminal COMMA args ')
        def args___arg_terminal_COMMA_args_(p):
            newNode = ParseTree("args",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : arg_terminal ')
        def args___arg_terminal_(p):
            newNode = ParseTree("args",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arg_terminal : var_type SELF_DEFINED ')
        def arg_terminal___var_type_SELF_DEFINED_(p):
            newNode = ParseTree("arg_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arg_terminal : var_type SELF_DEFINED OPEN_BRACK CLOSE_BRACK ')
        def arg_terminal___var_type_SELF_DEFINED_OPEN_BRACK_CLOSE_BRACK_(p):
            newNode = ParseTree("arg_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arg_terminal : var_type ')
        def arg_terminal___var_type_(p):
            newNode = ParseTree("arg_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('block : OPEN_BRACE content CLOSE_BRACE ')
        def block___OPEN_BRACE_content_CLOSE_BRACE_(p):
            newNode = ParseTree("block",p)
            self.Head = newNode
            return newNode

        @self.pg.production('block : OPEN_BRACE CLOSE_BRACE ')
        def block___OPEN_BRACE_CLOSE_BRACE_(p):
            newNode = ParseTree("block",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : content_terminal content ')
        def content___content_terminal_content_(p):
            newNode = ParseTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : content_terminal ')
        def content___content_terminal_(p):
            newNode = ParseTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content_terminal : single_line ')
        def content_terminal___single_line_(p):
            newNode = ParseTree("content_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content_terminal : loop ')
        def content_terminal___loop_(p):
            newNode = ParseTree("content_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content_terminal : branch ')
        def content_terminal___branch_(p):
            newNode = ParseTree("content_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content_terminal : goto ')
        def content_terminal___goto_(p):
            newNode = ParseTree("content_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content_terminal : COMMENT ')
        def content_terminal___COMMENT_(p):
            newNode = ParseTree("content_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content_terminal : block ')
        def content_terminal___block_(p):
            newNode = ParseTree("content_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : initialization SEMICOLON ')
        def single_line___initialization_SEMICOLON_(p):
            newNode = ParseTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : function_call SEMICOLON ')
        def single_line___function_call_SEMICOLON_(p):
            newNode = ParseTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : designation SEMICOLON ')
        def single_line___designation_SEMICOLON_(p):
            newNode = ParseTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : response SEMICOLON ')
        def single_line___response_SEMICOLON_(p):
            newNode = ParseTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : collation SEMICOLON ')
        def single_line___collation_SEMICOLON_(p):
            newNode = ParseTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : SEMICOLON ')
        def single_line___SEMICOLON_(p):
            newNode = ParseTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('function_call : SELF_DEFINED OPEN_PAREN param CLOSE_PAREN ')
        def function_call___SELF_DEFINED_OPEN_PAREN_param_CLOSE_PAREN_(p):
            newNode = ParseTree("function call",p)
            self.Head = newNode
            return newNode

        @self.pg.production('function_call : SELF_DEFINED OPEN_PAREN CLOSE_PAREN ')
        def function_call___SELF_DEFINED_OPEN_PAREN_CLOSE_PAREN_(p):
            newNode = ParseTree("function call",p)
            self.Head = newNode
            return newNode

        @self.pg.production('string_literal : STRING ')
        def string_literal___STRING_(p):
            newNode = ParseTree("string literal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param : param_terminal ')
        def param___param_terminal_(p):
            newNode = ParseTree("parameter",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param : param_terminal COMMA param ')
        def param___param_terminal_COMMA_param_(p):
            newNode = ParseTree("parameter",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param_terminal : arithmetic ')
        def param_terminal___arithmetic_(p):
            newNode = ParseTree("param_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param_terminal : STRING ')
        def param_terminal___STRING_(p):
            newNode = ParseTree("param_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : WHILE_LOOP OPEN_PAREN collation CLOSE_PAREN content_terminal ')
        def loop___WHILE_LOOP_OPEN_PAREN_collation_CLOSE_PAREN_content_terminal_(p):
            newNode = ParseTree("while loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : FOR_LOOP OPEN_PAREN for_part_1 SEMICOLON for_part_2 SEMICOLON for_part_3 CLOSE_PAREN content_terminal ')
        def loop___FOR_LOOP_OPEN_PAREN_for_part_1_SEMICOLON_for_part_2_SEMICOLON_for_part_3_CLOSE_PAREN_content_terminal_(p):
            newNode = ParseTree("for loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : DO_LOOP content_terminal WHILE_LOOP OPEN_PAREN collation CLOSE_PAREN SEMICOLON ')
        def loop___DO_LOOP_content_terminal_WHILE_LOOP_OPEN_PAREN_collation_CLOSE_PAREN_SEMICOLON_(p):
            newNode = ParseTree("do loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : IF_BRANCH OPEN_PAREN collation CLOSE_PAREN if_body')
        def branch___IF_BRANCH_OPEN_PAREN_collation_CLOSE_PAREN_if_body(p):
            newNode = ParseTree("if",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : IF_BRANCH OPEN_PAREN collation CLOSE_PAREN if_body if_expansion ')
        def branch___IF_BRANCH_OPEN_PAREN_collation_CLOSE_PAREN_if_body_if_expansion_(p):
            newNode = ParseTree("if",p)
            self.Head = newNode
            return newNode

        @self.pg.production('if_body : content_terminal ')
        def if_body___content_terminal_(p):
            newNode = ParseTree("if_body",p)
            self.Head = newNode
            return newNode

        @self.pg.production('if_expansion : ELSE_BRANCH if_body ')
        def if_expansion___ELSE_BRANCH_if_body_(p):
            newNode = ParseTree("if_expansion",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : SWITCH_BRANCH OPEN_PAREN arithmetic CLOSE_PAREN switch_body ')
        def branch___SWITCH_BRANCH_OPEN_PAREN_arithmetic_CLOSE_PAREN_switch_body_(p):
            newNode = ParseTree("switch",p)
            self.Head = newNode
            return newNode

        @self.pg.production('switch_body : OPEN_BRACE case CLOSE_BRACE ')
        def switch_body___OPEN_BRACE_case_CLOSE_BRACE_(p):
            newNode = ParseTree("switch_body",p)
            self.Head = newNode
            return newNode

        @self.pg.production('switch_body : OPEN_BRACE cases CLOSE_BRACE ')
        def switch_body___OPEN_BRACE_cases_CLOSE_BRACE_(p):
            newNode = ParseTree("switch_body",p)
            self.Head = newNode
            return newNode

        @self.pg.production('cases : case cases ')
        def cases___case_cases_(p):
            newNode = ParseTree("cases",p)
            self.Head = newNode
            return newNode

        @self.pg.production('cases : case ')
        def cases___case_(p):
            newNode = ParseTree("cases",p)
            self.Head = newNode
            return newNode

        @self.pg.production('cases : default ')
        def cases___default_(p):
            newNode = ParseTree("cases",p)
            self.Head = newNode
            return newNode

        @self.pg.production('case : CASE value COLON ')
        def case___CASE_value_COLON_(p):
            newNode = ParseTree("case",p)
            self.Head = newNode
            return newNode

        @self.pg.production('case : CASE value COLON case_body ')
        def case___CASE_value_COLON_case_body_(p):
            newNode = ParseTree("case",p)
            self.Head = newNode
            return newNode

        @self.pg.production('default : DEFAULT COLON ')
        def default___DEFAULT_COLON_(p):
            newNode = ParseTree("default",p)
            self.Head = newNode
            return newNode

        @self.pg.production('default : DEFAULT COLON case_body ')
        def default___DEFAULT_COLON_case_body_(p):
            newNode = ParseTree("default",p)
            self.Head = newNode
            return newNode

        @self.pg.production('case_body : content ')
        def case_body___content_(p):
            newNode = ParseTree("case_body",p)
            self.Head = newNode
            return newNode

        @self.pg.production('goto : SELF_DEFINED COLON content_terminal ')
        def goto___SELF_DEFINED_COLON_content_terminal_(p):
            newNode = ParseTree("goto",p)
            self.Head = newNode
            return newNode

        @self.pg.production('goto : SELF_DEFINED COLON ')
        def goto___SELF_DEFINED_COLON_(p):
            newNode = ParseTree("goto",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : RETURN collation ')
        def response___RETURN_collation_(p):
            newNode = ParseTree("return",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : RETURN ')
        def response___RETURN_(p):
            newNode = ParseTree("return",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : GOTO SELF_DEFINED ')
        def response___GOTO_SELF_DEFINED_(p):
            newNode = ParseTree("jump",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : BREAK ')
        def response___BREAK_(p):
            newNode = ParseTree("break",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : CONTINUE ')
        def response___CONTINUE_(p):
            newNode = ParseTree("continue",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : var_type SELF_DEFINED SET initialization_terminal ')
        def initialization___var_type_SELF_DEFINED_SET_initialization_terminal_(p):
            newNode = ParseTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : var_type SELF_DEFINED ')
        def initialization___var_type_SELF_DEFINED_(p):
            newNode = ParseTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : var_type SELF_DEFINED OPEN_BRACK INTEGER CLOSE_BRACK ')
        def initialization___var_type_SELF_DEFINED_OPEN_BRACK_INTEGER_CLOSE_BRACK_(p):
            newNode = ParseTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : var_type MUL designation ')
        def initialization___var_type_MUL_designation_(p):
            newNode = ParseTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : var_type SELF_DEFINED array_init SET initialization_terminal ')
        def initialization___var_type_SELF_DEFINED_array_init_SET_initialization_terminal_(p):
            newNode = ParseTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : var_type SELF_DEFINED array_init assignment OPEN_BRACE arr_list CLOSE_BRACE ')
        def initialization___var_type_SELF_DEFINED_array_init_assignment_OPEN_BRACE_arr_list_CLOSE_BRACE_(p):
            newNode = ParseTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('array_init : OPEN_BRACK INTEGER CLOSE_BRACK ')
        def array_init___OPEN_BRACK_INTEGER_CLOSE_BRACK_(p):
            newNode = ParseTree("array_init",p)
            self.Head = newNode
            return newNode

        @self.pg.production('array_init : OPEN_BRACK CLOSE_BRACK ')
        def array_init___OPEN_BRACK_CLOSE_BRACK_(p):
            newNode = ParseTree("array_init",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization_terminal : collation ')
        def initialization_terminal___collation_(p):
            newNode = ParseTree("initialization_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization_terminal : string_literal ')
        def initialization_terminal___string_literal_(p):
            newNode = ParseTree("initialization_terminal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_type : var_modif TYPE ')
        def var_type___var_modif_TYPE_(p):
            newNode = ParseTree("var_type",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_type : TYPE ')
        def var_type___TYPE_(p):
            newNode = ParseTree("var_type",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_1 : initialization ')
        def for_part_1___initialization_(p):
            newNode = ParseTree("for param 1",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_1 : ')
        def for_part_1___(p):
            newNode = ParseTree("for param 1",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_1 : designation ')
        def for_part_1___designation_(p):
            newNode = ParseTree("for param 1",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_2 : collation ')
        def for_part_2___collation_(p):
            newNode = ParseTree("for param 2",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_2 : ')
        def for_part_2___(p):
            newNode = ParseTree("for param 2",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_3 : designation ')
        def for_part_3___designation_(p):
            newNode = ParseTree("for param 3",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_3 : arithmetic ')
        def for_part_3___arithmetic_(p):
            newNode = ParseTree("for param 3",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_3 : ')
        def for_part_3___(p):
            newNode = ParseTree("for param 3",p)
            self.Head = newNode
            return newNode

        @self.pg.production('designation : var_access assignment collation ')
        def designation___var_access_assignment_collation_(p):
            newNode = ParseTree("designation",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arr_list : collation ')
        def arr_list___collation_(p):
            newNode = ParseTree("arr_list",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arr_list : collation COMMA arr_list ')
        def arr_list___collation_COMMA_arr_list_(p):
            newNode = ParseTree("arr_list",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : AEQ ')
        def assignment___AEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : SEQ ')
        def assignment___SEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : MEQ ')
        def assignment___MEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : DEQ ')
        def assignment___DEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : MODEQ ')
        def assignment___MODEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : LSEQ ')
        def assignment___LSEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : RSEQ ')
        def assignment___RSEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : BOEQ ')
        def assignment___BOEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : BAEQ ')
        def assignment___BAEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : XEQ ')
        def assignment___XEQ_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : SET ')
        def assignment___SET_(p):
            newNode = ParseTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation : collation_or ')
        def collation___collation_or_(p):
            newNode = ParseTree("collation",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_or : collation_and ')
        def collation_or___collation_and_(p):
            newNode = ParseTree("collation_or",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_or : collation_or OR collation_and ')
        def collation_or___collation_or_OR_collation_and_(p):
            newNode = ParseTree("collation_or",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_and : collation_bor ')
        def collation_and___collation_bor_(p):
            newNode = ParseTree("collation_and",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_and : collation_and AND collation_bor ')
        def collation_and___collation_and_AND_collation_bor_(p):
            newNode = ParseTree("collation_and",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_bor : collation_xor ')
        def collation_bor___collation_xor_(p):
            newNode = ParseTree("collation_bor",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_bor : collation_bor BOR collation_xor ')
        def collation_bor___collation_bor_BOR_collation_xor_(p):
            newNode = ParseTree("collation_bor",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_xor : collation_band ')
        def collation_xor___collation_band_(p):
            newNode = ParseTree("collation_xor",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_xor : collation_xor XOR collation_band ')
        def collation_xor___collation_xor_XOR_collation_band_(p):
            newNode = ParseTree("collation_xor",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_band : collation_eq ')
        def collation_band___collation_eq_(p):
            newNode = ParseTree("collation_band",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_band : collation_band BAND collation_eq ')
        def collation_band___collation_band_BAND_collation_eq_(p):
            newNode = ParseTree("collation_band",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_eq : collation_rel ')
        def collation_eq___collation_rel_(p):
            newNode = ParseTree("collation_eq",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_eq : collation_eq EQ collation_rel ')
        def collation_eq___collation_eq_EQ_collation_rel_(p):
            newNode = ParseTree("collation_eq",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_eq : collation_eq NEQ collation_rel ')
        def collation_eq___collation_eq_NEQ_collation_rel_(p):
            newNode = ParseTree("collation_eq",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_rel : arithmetic ')
        def collation_rel___arithmetic_(p):
            newNode = ParseTree("collation_rel",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_rel : collation_rel LT arithmetic ')
        def collation_rel___collation_rel_LT_arithmetic_(p):
            newNode = ParseTree("collation_rel",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_rel : collation_rel GT arithmetic ')
        def collation_rel___collation_rel_GT_arithmetic_(p):
            newNode = ParseTree("collation_rel",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_rel : collation_rel LEQ arithmetic ')
        def collation_rel___collation_rel_LEQ_arithmetic_(p):
            newNode = ParseTree("collation_rel",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation_rel : collation_rel GEQ arithmetic ')
        def collation_rel___collation_rel_GEQ_arithmetic_(p):
            newNode = ParseTree("collation_rel",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic_sh ')
        def arithmetic___arithmetic_sh_(p):
            newNode = ParseTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_sh : arithmetic_pm ')
        def arithmetic_sh___arithmetic_pm_(p):
            newNode = ParseTree("arithmetic_sh",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_sh : arithmetic_sh LSH arithmetic_pm ')
        def arithmetic_sh___arithmetic_sh_LSH_arithmetic_pm_(p):
            newNode = ParseTree("arithmetic_sh",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_sh : arithmetic_sh RSH arithmetic_pm ')
        def arithmetic_sh___arithmetic_sh_RSH_arithmetic_pm_(p):
            newNode = ParseTree("arithmetic_sh",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_pm : arithmetic_mul ')
        def arithmetic_pm___arithmetic_mul_(p):
            newNode = ParseTree("arithmetic_pm",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_pm : arithmetic_pm ADD arithmetic_mul ')
        def arithmetic_pm___arithmetic_pm_ADD_arithmetic_mul_(p):
            newNode = ParseTree("arithmetic_pm",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_pm : arithmetic_pm SUB arithmetic_mul ')
        def arithmetic_pm___arithmetic_pm_SUB_arithmetic_mul_(p):
            newNode = ParseTree("arithmetic_pm",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_mul : arithmetic_cast ')
        def arithmetic_mul___arithmetic_cast_(p):
            newNode = ParseTree("arithmetic_mul",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_mul : arithmetic_mul MUL arithmetic_cast ')
        def arithmetic_mul___arithmetic_mul_MUL_arithmetic_cast_(p):
            newNode = ParseTree("arithmetic_mul",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_mul : arithmetic_mul DIV arithmetic_cast ')
        def arithmetic_mul___arithmetic_mul_DIV_arithmetic_cast_(p):
            newNode = ParseTree("arithmetic_mul",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_mul : arithmetic_mul MOD arithmetic_cast ')
        def arithmetic_mul___arithmetic_mul_MOD_arithmetic_cast_(p):
            newNode = ParseTree("arithmetic_mul",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_cast : arithmetic_unary ')
        def arithmetic_cast___arithmetic_unary_(p):
            newNode = ParseTree("arithmetic_cast",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_cast : OPEN_PAREN var_type CLOSE_PAREN arithmetic_unary ')
        def arithmetic_cast___OPEN_PAREN_var_type_CLOSE_PAREN_arithmetic_unary_(p):
            newNode = ParseTree("arithmetic_cast",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_unary : arithmetic_post ')
        def arithmetic_unary___arithmetic_post_(p):
            newNode = ParseTree("arithmetic_unary",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_unary : INC var_access ')
        def arithmetic_unary___INC_var_access_(p):
            newNode = ParseTree("arithmetic_unary",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_unary : DEC var_access ')
        def arithmetic_unary___DEC_var_access_(p):
            newNode = ParseTree("arithmetic_unary",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_unary : unary_op arithmetic_cast ')
        def arithmetic_unary___unary_op_arithmetic_cast_(p):
            newNode = ParseTree("arithmetic_unary",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_unary : SIZEOF arithmetic_unary ')
        def arithmetic_unary___SIZEOF_arithmetic_unary_(p):
            newNode = ParseTree("arithmetic_unary",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_unary : SIZEOF var_type ')
        def arithmetic_unary___SIZEOF_var_type_(p):
            newNode = ParseTree("arithmetic_unary",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_post : value ')
        def arithmetic_post___value_(p):
            newNode = ParseTree("arithmetic_post",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_post : function_call ')
        def arithmetic_post___function_call_(p):
            newNode = ParseTree("arithmetic_post",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_post : var_access ')
        def arithmetic_post___var_access_(p):
            newNode = ParseTree("arithmetic_post",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_post : var_access INC ')
        def arithmetic_post___var_access_INC_(p):
            newNode = ParseTree("arithmetic_post",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_post : var_access DEC ')
        def arithmetic_post___var_access_DEC_(p):
            newNode = ParseTree("arithmetic_post",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic_post : OPEN_PAREN collation CLOSE_PAREN ')
        def arithmetic_post___OPEN_PAREN_collation_CLOSE_PAREN_(p):
            newNode = ParseTree("arithmetic_post",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary_op : BAND ')
        def unary_op___BAND_(p):
            newNode = ParseTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary_op : MUL ')
        def unary_op___MUL_(p):
            newNode = ParseTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary_op : ADD ')
        def unary_op___ADD_(p):
            newNode = ParseTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary_op : SUB ')
        def unary_op___SUB_(p):
            newNode = ParseTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary_op : COMP ')
        def unary_op___COMP_(p):
            newNode = ParseTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary_op : NOT ')
        def unary_op___NOT_(p):
            newNode = ParseTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_access : SELF_DEFINED ')
        def var_access___SELF_DEFINED_(p):
            newNode = ParseTree("var_access",p)
            self.Head = newNode
            return newNode

        @self.pg.production('var_access : SELF_DEFINED OPEN_BRACK collation CLOSE_BRACK ')
        def var_access___SELF_DEFINED_OPEN_BRACK_collation_CLOSE_BRACK_(p):
            newNode = ParseTree("var_access",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : INTEGER ')
        def value___INTEGER_(p):
            newNode = ParseTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : PRECISION ')
        def value___PRECISION_(p):
            newNode = ParseTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : CHAR ')
        def value___CHAR_(p):
            newNode = ParseTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : HEX ')
        def value___HEX_(p):
            newNode = ParseTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : OCT ')
        def value___OCT_(p):
            newNode = ParseTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : BIN ')
        def value___BIN_(p):
            newNode = ParseTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : NULL ')
        def value___NULL_(p):
            newNode = ParseTree("value",p)
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



