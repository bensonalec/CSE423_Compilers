from lexer import Lexer
from rply import errors

file = open("test.c","r")
text_input = file.read()

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)

print(tokens)
try: 
    for tok in tokens:
        print(tok)
except errors.LexingError as err:
    print(err)
    
