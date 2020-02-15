from rply import LexerGenerator
from rply.errors import LexingError
import copy
import re

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()
    
    def _add_tokens(self):
        self.lexer.add("COMMENT",       r"/(\*(\w|\W)*?\*/|/([^\n]*))") # Catches both multi-line and single line comments
        self.lexer.add("PREPROCESSOR",  r"#\s*(warning|else|endif|include|undef|ifdef|ifndef|if|elif|pragma|define|if|elif|error|pragma|line)([\t\f ]+[^\s]+)*")
        self.lexer.add("CHAR",          r"\'\\?[\w\;\\ \%\"\']\'")
        self.lexer.add("STRING",        r"(\"([\w+\\ \"']|[`\-=~[\]\;,./!@#$%^&*()_+{}|:<>?])*\")") # Classifies single characters and multiple characters as a string
        self.lexer.add("HEX",           r"0x[\dA-Fa-f]+")
        self.lexer.add("OCT",           r"0[0-7]{1,3}")
        self.lexer.add("BIN",           r"0b[01]+")
        self.lexer.add("PRECISION",     r"\-?(\d|[1-9]\d+)\.\d*")
        self.lexer.add("INTEGER",       r"\-?([1-9]\d*|\d)")
        self.lexer.add("EQ",            r"={2}")
        self.lexer.add("LEQ",           r"<=")
        self.lexer.add("GEQ",           r">=")
        self.lexer.add("NEQ",           r"!=")
        self.lexer.add("LT",            r"<")
        self.lexer.add("GT",            r">")
        self.lexer.add("AEQ",           r"\+=")
        self.lexer.add("SEQ",           r"-=")
        self.lexer.add("MEQ",           r"\*=")
        self.lexer.add("DEQ",           r"/=")
        self.lexer.add("MODEQ",         r"%=")
        self.lexer.add("LSEQ",          r"<{2}=")
        self.lexer.add("RSEQ",          r">{2}=")
        self.lexer.add("BOEQ",          r"\|=")
        self.lexer.add("BAEQ",          r"&=")
        self.lexer.add("XEQ",           r"\^=")
        self.lexer.add("CEQ",           r"~=")
        self.lexer.add("SET",           r"=")
        self.lexer.add("INC",           r"\+{2}")
        self.lexer.add("DEC",           r"-{2}")
        self.lexer.add("AND",           r"&{2}")
        self.lexer.add("OR",            r"\|{2}")
        self.lexer.add("MOD",           r"%")
        self.lexer.add("MUL",           r"\*")
        self.lexer.add("DIV",           r"/")
        self.lexer.add("ADD",           r"\+")
        self.lexer.add("SUB",           r"-")
        self.lexer.add("NOT",           r"!")
        self.lexer.add("LSH",           r"<{2}")
        self.lexer.add("RSH",           r">{2}")
        self.lexer.add("BOR",           r"\|")
        self.lexer.add("BAND",          r"&")
        self.lexer.add("XOR",           r"\^")
        self.lexer.add("COMP",          r"~")
        self.lexer.add("ACCESS",        r"->|\.|\[|\]")
        self.lexer.add("SIZEOF",        r"\bsizeof\b")
        self.lexer.add("TYPEDEF",       r"\btypedef\b")
        self.lexer.add("FUNC_MODIF",    r"\binline\b")
        self.lexer.add("VAR_MODIF",     r"\b(register|volatile)\b")
        self.lexer.add("BOTH_MODIF",    r"\b(const|signed|static|unsigned|extern)\b")
        self.lexer.add("GOTO",          r"\bgoto\b")
        self.lexer.add("RETURN",        r"\breturn\b")
        self.lexer.add("BREAK",         r"\bbreak\b")
        self.lexer.add("CONTINUE",      r"\bcontinue\b")
        self.lexer.add("FOR_LOOP",      r"\bfor\b")
        self.lexer.add("WHILE_LOOP",    r"\bwhile\b")
        self.lexer.add("DO_LOOP",       r"\bdo\b")
        self.lexer.add("IF_BRANCH",     r"\bif\b")
        self.lexer.add("ELSE_BRANCH",   r"\belse\b")
        self.lexer.add("SWITCH_BRANCH", r"\bswitch\b")
        self.lexer.add("CASE",          r"\bcase\b")
        self.lexer.add("DEFAULT",       r"\bdefault\b")
        self.lexer.add("NULL",          r"\bNULL\b")
        self.lexer.add("TYPE",          r"\b(auto|long double|double|float|long long (int)?|long|int|short|char|void)\b")
        self.lexer.add("MEM_STRUCT",    r"\b(struct|union|enum)\b")
        self.lexer.add("SELF_DEFINED",  r"[a-zA-Z_]\w*")
        self.lexer.add("OPEN_PAREN",    r"\(")
        self.lexer.add("CLOSE_PAREN",   r"\)")
        self.lexer.add("OPEN_BRACE",    r"\{")
        self.lexer.add("CLOSE_BRACE",   r"\}")
        self.lexer.add("SEMICOLON",     r";")
        self.lexer.add("COLON",         r":")
        self.lexer.add("COMMA",         r",")
        self.lexer.add("INVALID",       r".+?") # Just to catch stuff we havent thought about yet
        self.lexer.ignore(r'\s+')
        self.lexer.ignore(r'\n')
        self.lexer.ignore(r'\t')
    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
    
def tokensToString(tokens):
    """
    Iterates through the tokens and generates a string of all of them

    Args:
        tokens: The token object that is returned from the lexer.
    """
    out = ""
    for tok in tokens:
        out+= str(tok) + "\n"
    return out

def validateTokens(tokens):
    """
    Validates the given token list.

    Args:
        tokens: The token object that is returned from the lexer.
    
    Returns:
        The same token object if there were no invalid tokens.

    Raises:
        LexingError: If there is at least one invalid token this is raised. 
    """
    cpy = copy.deepcopy(tokens)
    status = "PASS"

    # Goes through copy list and looks for any "invalid tokens".
    # The lexer will mark any unknown tokens with the name, "INVALID".
    for i in cpy:
        if (i.name == "INVALID"):
            print_error(i)
            status = "FAIL" # status is changed

    
    if (status == "FAIL"):
        raise LexingError("invalid token", i.source_pos)
    else:
        return tokens

def print_error(token):
    """
    Prints lexer error message. Currently we only experience invalid token
    errors. The input `token` is a `Token` object, imported from `rply`.

    Args:
        token: The token object that is returned from the lexer.
    """
    print(f"LexingError: Invalid Token \'{token.value}\' at, {token.source_pos}\n")
        