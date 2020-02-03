
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
            ['TYPE','SELF_DEFINED','OPEN_PAREN','CLOSE_PAREN','OPEN_BRACE','CLOSE_BRACE','ASSIGNMENT','SEMICOLON','LOOPING','BRANCHING','BEHAVIOR','COLON','CLOSE_PARENT','COMMA','INTEGER','STRING','PRECISION','COMPARISON','LOGICAL','ARITHMETIC']
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

        @self.pg.production('definitionList : definitionList functionDefinition ')
        def definitionList___definitionList_functionDefinition_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("definitionList",p)
            self.Head = newNode
            return newNode

        @self.pg.production('definitionList : functionDefinition ')
        def definitionList___functionDefinition_(p):
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

        @self.pg.production('single_line : TYPE SELF_DEFINED ASSIGNMENT literal SEMICOLON ')
        def single_line___TYPE_SELF_DEFINED_ASSIGNMENT_literal_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("variable assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : TYPE SELF_DEFINED SEMICOLON ')
        def single_line___TYPE_SELF_DEFINED_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("initialization",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : function_call SEMICOLON ')
        def single_line___function_call_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("function call",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : LOOPING OPEN_PAREN boolean CLOSE_PAREN block ')
        def single_line___LOOPING_OPEN_PAREN_boolean_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("loop",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : LOOPING block LOOPING OPEN_PAREN boolean CLOSE_PAREN SEMICOLON ')
        def single_line___LOOPING_block_LOOPING_OPEN_PAREN_boolean_CLOSE_PAREN_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("do while",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : BRANCHING OPEN_PAREN boolean CLOSE_PAREN block ')
        def single_line___BRANCHING_OPEN_PAREN_boolean_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("if and else",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : BRANCHING OPEN_PAREN non_contiguous CLOSE_PAREN block ')
        def single_line___BRANCHING_OPEN_PAREN_non_contiguous_CLOSE_PAREN_block_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("switch",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : arithmetic SEMICOLON ')
        def single_line___arithmetic_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : BEHAVIOR literal SEMICOLON ')
        def single_line___BEHAVIOR_literal_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("return statement",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : BEHAVIOR non_contiguous SEMICOLON ')
        def single_line___BEHAVIOR_non_contiguous_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("statement",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : BEHAVIOR SEMICOLON ')
        def single_line___BEHAVIOR_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("return statement",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : SELF_DEFINED ASSIGNMENT literal SEMICOLON ')
        def single_line___SELF_DEFINED_ASSIGNMENT_literal_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : SELF_DEFINED ASSIGNMENT boolean SEMICOLON ')
        def single_line___SELF_DEFINED_ASSIGNMENT_boolean_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : SELF_DEFINED ASSIGNMENT arithmetic SEMICOLON ')
        def single_line___SELF_DEFINED_ASSIGNMENT_arithmetic_SEMICOLON_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("assignment",p)
            self.Head = newNode
            return newNode

        @self.pg.production('single_line : SELF_DEFINED COLON single_line ')
        def single_line___SELF_DEFINED_COLON_single_line_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("goto_label",p)
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

        @self.pg.production('function_call : SELF_DEFINED OPEN_PAREN CLOSE_PARENT ')
        def function_call___SELF_DEFINED_OPEN_PAREN_CLOSE_PARENT_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("function call",p)
            self.Head = newNode
            return newNode

        @self.pg.production('param : literal ')
        def param___literal_(p):
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

        @self.pg.production('param : literal COMMA param ')
        def param___literal_COMMA_param_(p):
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

        @self.pg.production('literal : INTEGER ')
        def literal___INTEGER_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("literal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('literal : STRING ')
        def literal___STRING_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("literal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('literal : PRECISION ')
        def literal___PRECISION_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("literal",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : TYPE SELF_DEFINED ')
        def args___TYPE_SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("argument",p)
            self.Head = newNode
            return newNode

        @self.pg.production('args : TYPE SELF_DEFINED COMMA args ')
        def args___TYPE_SELF_DEFINED_COMMA_args_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("argument",p)
            self.Head = newNode
            return newNode

        @self.pg.production('boolean : boolean COMPARISON boolean ')
        def boolean___boolean_COMPARISON_boolean_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("boolean",p)
            self.Head = newNode
            return newNode

        @self.pg.production('boolean : boolean LOGICAL boolean ')
        def boolean___boolean_LOGICAL_boolean_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("boolean",p)
            self.Head = newNode
            return newNode

        @self.pg.production('boolean : arithmetic ')
        def boolean___arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("boolean",p)
            self.Head = newNode
            return newNode

        @self.pg.production('boolean : function_call ')
        def boolean___function_call_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("boolean",p)
            self.Head = newNode
            return newNode

        @self.pg.production('boolean : SELF_DEFINED ')
        def boolean___SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("boolean",p)
            self.Head = newNode
            return newNode

        @self.pg.production('boolean : boolean ')
        def boolean___boolean_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("boolean",p)
            self.Head = newNode
            return newNode

        @self.pg.production('boolean : numeral ')
        def boolean___numeral_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("boolean",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic ARITHMETIC arithmetic ')
        def arithmetic___arithmetic_ARITHMETIC_arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : numeral ')
        def arithmetic___numeral_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : arithmetic ')
        def arithmetic___arithmetic_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('arithmetic : unary ')
        def arithmetic___unary_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("arithmetic",p)
            self.Head = newNode
            return newNode

        @self.pg.production('numeral : INTEGER ')
        def numeral___INTEGER_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("numeral",p)
            self.Head = newNode
            return newNode

        @self.pg.production('numeral : PRECISION ')
        def numeral___PRECISION_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("numeral",p)
            self.Head = newNode
            return newNode

        @self.pg.production('non_contiguous : PRECISION ')
        def non_contiguous___PRECISION_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("non contiguous",p)
            self.Head = newNode
            return newNode

        @self.pg.production('non_contiguous : INTEGER ')
        def non_contiguous___INTEGER_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("non contiguous",p)
            self.Head = newNode
            return newNode

        @self.pg.production('non_contiguous : STRING ')
        def non_contiguous___STRING_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("non contiguous",p)
            self.Head = newNode
            return newNode

        @self.pg.production('non_contiguous : SELF_DEFINED ')
        def non_contiguous___SELF_DEFINED_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("non contiguous",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary : ARITHMETIC non_contiguous ')
        def unary___ARITHMETIC_non_contiguous_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary : non_contiguous ARITHMETIC ')
        def unary___non_contiguous_ARITHMETIC_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("unary_op",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary : BEHAVIOR OPEN_PAREN non_contiguous CLOSE_PAREN ')
        def unary___BEHAVIOR_OPEN_PAREN_non_contiguous_CLOSE_PAREN_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("sizeof_self_def",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary : BEHAVIOR OPEN_PAREN TYPE CLOSE_PAREN ')
        def unary___BEHAVIOR_OPEN_PAREN_TYPE_CLOSE_PAREN_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("sizeof_type",p)
            self.Head = newNode
            return newNode

        @self.pg.production('unary : OPEN_PAREN TYPE CLOSE_PAREN ')
        def unary___OPEN_PAREN_TYPE_CLOSE_PAREN_(p):
            """
            Boilerplate BNF function
            param: p: the matching set of tokens
            :return: The node of the abstract syntax tree
            """
            newNode = AbstractSyntaxTree("cast",p)
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



    