
from rply import ParserGenerator
from rply.errors import ParserGeneratorWarning
from warnings import simplefilter
from rply.token import Token

#we get werid 'non-descriptive' warnings from ParserGenerator, this ignores those
simplefilter('ignore', ParserGeneratorWarning)

class AbstractSyntaxTree():
    """
    AbstractSyntaxTree is a class that acts as each node in an Abstract Syntax Tree
    """
    def __init__(self, token, content):
        """
        Construct a new AbstractSyntaxTree object
        :param token: the token type of the node
        :param content: the content of that is tokenized
        :return: this returns nothing
        """
        self.token = token
        self.content = content


#setup parser class
class Parser():
    """
    Parser is an object that contains the rules for the aprser
    """
    
    def __init__(self):
        """
        Initializes the parser and tells it the allowed tokens
        :return: This does not return anything
        """

        self.pg = ParserGenerator(
            ['SEMICOLON','TYPE','SELF_DEFINED','OPEN_PAREN','CLOSE_PAREN','COMMA','OPEN_BRACE','CLOSE_BRACE','COMMENT','WHILE_LOOP','FOR_LOOP','DO_LOOP','IF_BRANCH','ELSE_BRANCH','SWITCH_BRANCH','CASE','COLON','DEFAULT','RETURN','GOTO','BREAK','CONTINUE','AEQ','SEQ','MEQ','DEQ','LSEQ','RSEQ','BOEQ','BAEQ','XEQ','CEQ','SET','OR','AND','BOR','XOR','BAND','LSH','RSH','ADD','SUB','MUL','DIV','MOD','NOT','COMP','INC','DEC','INTEGER','PRECISION','CHAR','HEX','OCT','BIN','NULL'] , 
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


    def parse(self):
        """
        The list of BNF functions and their behavior
        :return: This does not return anything
        """
        
        @self.pg.production('program : definitionList ')
        def program(p):
            """
            Tells the parser which BNF will be the head of the tree
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("program",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definitionList : functionDefinition definitionList ')
        def definitionList___functionDefinition_definitionList_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("definitionList",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definitionList : functionDeclaration definitionList ')
        def definitionList___functionDeclaration_definitionList_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("definitionList",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definitionList : initialization SEMICOLON definitionList ')
        def definitionList___initialization_SEMICOLON_definitionList_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("definitionList",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definitionList : ')
        def definitionList___(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("definitionList",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDefinition : TYPE SELF_DEFINED OPEN_PAREN args CLOSE_PAREN block ')
        def functionDefinition___TYPE_SELF_DEFINED_OPEN_PAREN_args_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("function definition",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDefinition : TYPE SELF_DEFINED OPEN_PAREN CLOSE_PAREN block ')
        def functionDefinition___TYPE_SELF_DEFINED_OPEN_PAREN_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("function definition",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDeclaration : TYPE SELF_DEFINED OPEN_PAREN args CLOSE_PAREN SEMICOLON ')
        def functionDeclaration___TYPE_SELF_DEFINED_OPEN_PAREN_args_CLOSE_PAREN_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("functionDeclaration",p)
            self.Head = newNode
            return newNode

        @self.pg.production('functionDeclaration : TYPE SELF_DEFINED OPEN_PAREN CLOSE_PAREN SEMICOLON ')
        def functionDeclaration___TYPE_SELF_DEFINED_OPEN_PAREN_CLOSE_PAREN_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("functionDeclaration",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : TYPE SELF_DEFINED COMMA args ')
        def args___TYPE_SELF_DEFINED_COMMA_args_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("args",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : TYPE SELF_DEFINED ')
        def args___TYPE_SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("args",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : TYPE ')
        def args___TYPE_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("args",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : TYPE COMMA args ')
        def args___TYPE_COMMA_args_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("args",p)
            self.Head = newNode
            return newNode

        @self.pg.production('block : OPEN_BRACE block content CLOSE_BRACE ')
        def block___OPEN_BRACE_block_content_CLOSE_BRACE_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("block",p)
            self.Head = newNode
            return newNode

        @self.pg.production('block : OPEN_BRACE content block CLOSE_BRACE ')
        def block___OPEN_BRACE_content_block_CLOSE_BRACE_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("block",p)
            self.Head = newNode
            return newNode

        @self.pg.production('block : OPEN_BRACE content CLOSE_BRACE ')
        def block___OPEN_BRACE_content_CLOSE_BRACE_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("block",p)
            self.Head = newNode
            return newNode

        @self.pg.production('block : OPEN_BRACE CLOSE_BRACE ')
        def block___OPEN_BRACE_CLOSE_BRACE_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("block",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : single_line content ')
        def content___single_line_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : loop content ')
        def content___loop_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : branch content ')
        def content___branch_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : goto content ')
        def content___goto_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : goto ')
        def content___goto_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : branch ')
        def content___branch_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : loop ')
        def content___loop_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : single_line ')
        def content___single_line_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : COMMENT content ')
        def content___COMMENT_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('content : COMMENT ')
        def content___COMMENT_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("content",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : initialization SEMICOLON ')
        def single_line___initialization_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : function_call SEMICOLON ')
        def single_line___function_call_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : designation SEMICOLON ')
        def single_line___designation_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : response SEMICOLON ')
        def single_line___response_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : SEMICOLON ')
        def single_line___SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("single_line",p)
            self.Head = newNode
            return newNode

        @self.pg.production('function_call : SELF_DEFINED OPEN_PAREN param CLOSE_PAREN ')
        def function_call___SELF_DEFINED_OPEN_PAREN_param_CLOSE_PAREN_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("function call",p)
            self.Head = newNode
            return newNode

        @self.pg.production('function_call : SELF_DEFINED OPEN_PAREN CLOSE_PAREN ')
        def function_call___SELF_DEFINED_OPEN_PAREN_CLOSE_PAREN_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("function call",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param : arithmetic ')
        def param___arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("parameter",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param : SELF_DEFINED ')
        def param___SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("paramater",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param : arithmetic COMMA param ')
        def param___arithmetic_COMMA_param_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("parameter",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param : SELF_DEFINED COMMA param ')
        def param___SELF_DEFINED_COMMA_param_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("parameter",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : WHILE_LOOP OPEN_PAREN arithmetic CLOSE_PAREN block ')
        def loop___WHILE_LOOP_OPEN_PAREN_arithmetic_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("while loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : WHILE_LOOP OPEN_PAREN arithmetic CLOSE_PAREN content ')
        def loop___WHILE_LOOP_OPEN_PAREN_arithmetic_CLOSE_PAREN_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("while loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : FOR_LOOP OPEN_PAREN for_part_1 SEMICOLON for_part_2 SEMICOLON for_part_3 CLOSE_PAREN block ')
        def loop___FOR_LOOP_OPEN_PAREN_for_part_1_SEMICOLON_for_part_2_SEMICOLON_for_part_3_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : FOR_LOOP OPEN_PAREN for_part_1 SEMICOLON for_part_2 SEMICOLON for_part_3 CLOSE_PAREN content ')
        def loop___FOR_LOOP_OPEN_PAREN_for_part_1_SEMICOLON_for_part_2_SEMICOLON_for_part_3_CLOSE_PAREN_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : DO_LOOP block WHILE_LOOP OPEN_PAREN arithmetic CLOSE_PAREN SEMICOLON ')
        def loop___DO_LOOP_block_WHILE_LOOP_OPEN_PAREN_arithmetic_CLOSE_PAREN_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('loop : DO_LOOP content WHILE_LOOP OPEN_PAREN arithmetic CLOSE_PAREN SEMICOLON ')
        def loop___DO_LOOP_content_WHILE_LOOP_OPEN_PAREN_arithmetic_CLOSE_PAREN_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : IF_BRANCH OPEN_PAREN arithmetic CLOSE_PAREN block ')
        def branch___IF_BRANCH_OPEN_PAREN_arithmetic_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("if",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : IF_BRANCH OPEN_PAREN arithmetic CLOSE_PAREN content ')
        def branch___IF_BRANCH_OPEN_PAREN_arithmetic_CLOSE_PAREN_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("if",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : ELSE_BRANCH IF_BRANCH OPEN_PAREN arithmetic CLOSE_PAREN block ')
        def branch___ELSE_BRANCH_IF_BRANCH_OPEN_PAREN_arithmetic_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("elif",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : ELSE_BRANCH IF_BRANCH OPEN_PAREN arithmetic CLOSE_PAREN content ')
        def branch___ELSE_BRANCH_IF_BRANCH_OPEN_PAREN_arithmetic_CLOSE_PAREN_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("elif",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : ELSE_BRANCH block ')
        def branch___ELSE_BRANCH_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("else",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : ELSE_BRANCH content ')
        def branch___ELSE_BRANCH_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("else",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : SWITCH_BRANCH OPEN_PAREN value CLOSE_PAREN block ')
        def branch___SWITCH_BRANCH_OPEN_PAREN_value_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("switch",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : CASE value COLON block ')
        def branch___CASE_value_COLON_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("case",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : CASE value COLON content ')
        def branch___CASE_value_COLON_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("case",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : DEFAULT COLON block ')
        def branch___DEFAULT_COLON_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("default",p)
            self.Head = newNode
            return newNode

        @self.pg.production('branch : DEFAULT COLON content ')
        def branch___DEFAULT_COLON_content_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("default",p)
            self.Head = newNode
            return newNode

        @self.pg.production('goto : SELF_DEFINED COLON single_line ')
        def goto___SELF_DEFINED_COLON_single_line_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("goto",p)
            self.Head = newNode
            return newNode

        @self.pg.production('goto : SELF_DEFINED COLON loop ')
        def goto___SELF_DEFINED_COLON_loop_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("goto",p)
            self.Head = newNode
            return newNode

        @self.pg.production('goto : SELF_DEFINED COLON branch ')
        def goto___SELF_DEFINED_COLON_branch_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("goto",p)
            self.Head = newNode
            return newNode

        @self.pg.production('goto : SELF_DEFINED COLON block ')
        def goto___SELF_DEFINED_COLON_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("goto",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : RETURN arithmetic ')
        def response___RETURN_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("return",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : RETURN function_call ')
        def response___RETURN_function_call_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("return",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : RETURN SELF_DEFINED ')
        def response___RETURN_SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("return",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : RETURN ')
        def response___RETURN_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("return",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : GOTO SELF_DEFINED ')
        def response___GOTO_SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("jump",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : BREAK ')
        def response___BREAK_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("break",p)
            self.Head = newNode
            return newNode

        @self.pg.production('response : CONTINUE ')
        def response___CONTINUE_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("continue",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : TYPE designation ')
        def initialization___TYPE_designation_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('initialization : TYPE SELF_DEFINED ')
        def initialization___TYPE_SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_1 : initialization ')
        def for_part_1___initialization_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for param 1",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_1 : ')
        def for_part_1___(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for param 1",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_1 : designation ')
        def for_part_1___designation_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for param 1",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_2 : collation ')
        def for_part_2___collation_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for param 2",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_2 : ')
        def for_part_2___(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for param 2",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_3 : designation ')
        def for_part_3___designation_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for param 3",p)
            self.Head = newNode
            return newNode

        @self.pg.production('for_part_3 : ')
        def for_part_3___(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("for param 3",p)
            self.Head = newNode
            return newNode

        @self.pg.production('designation : SELF_DEFINED assignment arithmetic ')
        def designation___SELF_DEFINED_assignment_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("designation",p)
            self.Head = newNode
            return newNode

        @self.pg.production('designation : SELF_DEFINED assignment ')
        def designation___SELF_DEFINED_assignment_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("designation",p)
            self.Head = newNode
            return newNode

        @self.pg.production('designation : SELF_DEFINED assignment function_call ')
        def designation___SELF_DEFINED_assignment_function_call_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("designation",p)
            self.Head = newNode
            return newNode

        @self.pg.production('designation : SELF_DEFINED assignment arithmetic ')
        def designation___SELF_DEFINED_assignment_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("designation",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : AEQ ')
        def assignment___AEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : SEQ ')
        def assignment___SEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : MEQ ')
        def assignment___MEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : DEQ ')
        def assignment___DEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : LSEQ ')
        def assignment___LSEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : RSEQ ')
        def assignment___RSEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : BOEQ ')
        def assignment___BOEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : BAEQ ')
        def assignment___BAEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : XEQ ')
        def assignment___XEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : CEQ ')
        def assignment___CEQ_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('assignment : SET ')
        def assignment___SET_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('collation : arithmetic ')
        def collation___arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("collation",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic OR arithmetic ')
        def arithmetic___arithmetic_OR_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic AND arithmetic ')
        def arithmetic___arithmetic_AND_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic BOR arithmetic ')
        def arithmetic___arithmetic_BOR_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic XOR arithmetic ')
        def arithmetic___arithmetic_XOR_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic BAND arithmetic ')
        def arithmetic___arithmetic_BAND_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic LSH arithmetic ')
        def arithmetic___arithmetic_LSH_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic RSH arithmetic ')
        def arithmetic___arithmetic_RSH_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic ADD arithmetic ')
        def arithmetic___arithmetic_ADD_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic SUB arithmetic ')
        def arithmetic___arithmetic_SUB_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic MUL arithmetic ')
        def arithmetic___arithmetic_MUL_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic DIV arithmetic ')
        def arithmetic___arithmetic_DIV_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic MOD arithmetic ')
        def arithmetic___arithmetic_MOD_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : ADD arithmetic ')
        def arithmetic___ADD_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : SUB arithmetic ')
        def arithmetic___SUB_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : NOT arithmetic ')
        def arithmetic___NOT_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : COMP arithmetic ')
        def arithmetic___COMP_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : OPEN_PAREN TYPE CLOSE_PAREN arithmetic ')
        def arithmetic___OPEN_PAREN_TYPE_CLOSE_PAREN_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : INC SELF_DEFINED ')
        def arithmetic___INC_SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : DEC SELF_DEFINED ')
        def arithmetic___DEC_SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : SELF_DEFINED INC ')
        def arithmetic___SELF_DEFINED_INC_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : SELF_DEFINED DEC ')
        def arithmetic___SELF_DEFINED_DEC_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : value ')
        def arithmetic___value_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : SELF_DEFINED ')
        def arithmetic___SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : function_call ')
        def arithmetic___function_call_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : INTEGER ')
        def value___INTEGER_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : PRECISION ')
        def value___PRECISION_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : CHAR ')
        def value___CHAR_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : HEX ')
        def value___HEX_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : OCT ')
        def value___OCT_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : BIN ')
        def value___BIN_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("value",p)
            self.Head = newNode
            return newNode

        @self.pg.production('value : NULL ')
        def value___NULL_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("value",p)
            self.Head = newNode
            return newNode

    
        @self.pg.error
        def error_handle(token):
            """
            Boilerplate error handling function
            param: token: the token that caused an error
            :return: There is nothing returned
            """
            return ValueError(token)

    #boilerplate function
    def get_parser(self):
        """
        Returns the built version of the parser
        :return: Returns the built parser
        """
        return self.pg.build()

    #retrieve the trees head
    def getTree(self):
        """
        Getter for the head of the tree
        :return: This returns the head of the tree
        """

        return self.Head

    def print_error(self):
        """
        Prints parser error message. This function ultimately iterates through the AST that was 
        returned after the parser found an error. AST's consist of tokens as well as other AST's so 
        we need to iterate to find the first token and then print its source position.
        :return: This does not return anything
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
                # last element is an AST.
                head = head.content[len(head.content)-1]

        if token:
            print(f"ParsingError: Last token  \'{token.value}\' parsed successfully at, {token.source_pos}\n")
        else:
            # Never found a token to report, need to exit
            print("ParsingError: No AST obtained\n")
            exit()



    