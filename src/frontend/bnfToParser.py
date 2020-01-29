import re

	
funcTemp = 	"""
		@self.pg.production('BNFSPOT')
		def FUNCNAMESPOT(p):
			newNode = AbstractSyntaxTree("NAMESPOT",p)
			self.Head = newNode
			return newNode
"""
headTemp = 	"""
		@self.pg.production('BNFSPOT')
		def program(p):
			newNode = AbstractSyntaxTree("NAMESPOT",p)
			self.Head = newNode
			return newNode
"""

initTemp = """
	def __init__(self):
		self.pg = ParserGenerator(
			TOKENSPOT
		)
		#initialzie head and current node
		self.Head = None
"""

def main(path):
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
    from ast import *
    from warnings import simplefilter

    #we get werid 'non-descriptive' warnings from ParserGenerator, this ignores those
    simplefilter('ignore', ParserGeneratorWarning)


    #setup parser class
    class Parser():

        INITSPOT

        def parse(self):

            FUNCLISTSPOT
        
            @self.pg.error
            def error_handle(token):
                return ValueError(token)

        #boilerplate function
        def get_parser(self):
            return self.pg.build()

        #retrieve the trees head
        def getTree(self):
            return self.Head

    """

    totalOutput = totalOutput.replace("INITSPOT",initFunc)
    totalOutput = totalOutput.replace("FUNCLISTSPOT",functionList)

    # print (totalOutput)

    with open("parser.py", 'w') as f:
        f.write(totalOutput)

if __name__ == "__main__":
    main("BNF_definition")