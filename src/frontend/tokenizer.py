import sys

class token():
    def __init__(self,cont,eval):
        self.content = None
        self.eval = None


#Highest level function, calls other function in order to return ordered collection of tokens.
def tokenize():
    pass


#fi is string. This function will handle file io. Returns list of all line in file.
def read_file(fi):
    pass

#Takes in one line of input as input. Returns list of tokens, and throws error for invalid token.
#All team memeber will approach this problem and discuss solution at a later meet date.
def validate(line):
    pass


#Prints all token classes. Takes in a list of tokens
def print_tokens(li):
    pass

if __name__ == "__main__":
    tokenize()
