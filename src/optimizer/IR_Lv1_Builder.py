import re
import sys
import importlib

simp = importlib.import_module("simplify", __name__)
ast = importlib.import_module("AST_builder", __name__)

class LevelOneIR():
    def __init__(self,astHead,symTable):
        self.astHead = astHead
        self.symTable = symTable
        self.IR = []

    def construct(self):

        sym = self.symTable
        ntv = self.astHead

        varIndex = 0
        lastVarName = "_" + str(varIndex)
        bodyList = []

        # list of all bodies within functions in our C program
        for x in self.astHead.children:
            if x.name == "func":
                bodyList.append((x.children[1].name,x.children[3]))

        returnDigit = 1234
        labelDigit = returnDigit + 1
        for i in bodyList:
            lines , labelDigit = returnLines(i[1], returnDigit, labelDigit)
            returnDigit = labelDigit + 1

        self.IR = lines

        return lines

def buildBoilerPlate(symTable):
    namesandparams = []
    functionNames = [(x.name,x.type) for x in symTable.symbols if x.is_function]
    params = [(x.name,x.scope,x.type) for x in symTable.symbols if x.is_param]

    for x in functionNames:
        track = 0
        paramsLi = []
        for i in params:
            if x[0] == i[1].split("/")[1]:
                track+=1

                paramsLi.append((i[2],i[0]))
        if track == 0:
            namesandparams.append((x[0],paramsLi,x[1]))
        else:
            namesandparams.append((x[0],paramsLi,x[1]))
    return namesandparams

def returnLines(node,returnDigit,labelDigit,successDigit=None,failureDigit=None):
    lines = []
    for element in node.children:
        try:
            splits = [["=","+="],["for"],["body"],["branch"],["return"],["call"],["while","do_while"],["break"],["continue"],["goto"],["label"], ["++", "--"]]
            ind = [splits.index(x) for x in splits if element.name in x]
            ind = ind[0]
            if ind == 0:
                #Assignment

                varName = element.children[0].children[0].name #temporary
                
                # Initialize variable (if needed)
                if len(element.children[0].children) > 1:
                    varType = element.children[0].children[0].name
                    varName = element.children[0].children[1].name
                    lines.append(f"{varType} {varName};")

                # Breakdown arithmetic nodes
                tmp, tvs, labelList = simp.breakdownExpression(element, [], labelList=[labelDigit])
                lines.extend(tmp)
                # print (labelDigit)
                if labelList != []:
                    labelDigit = labelList[-1]
                # print (labelDigit)

            elif ind == 1:
                # For Loop

                # Initialize variable
                if element.children[0].children != []:
                    initNode = ast.ASTNode("body", None)
                    initNode.children.append(element.children[0])
                    tmp, labelDigit = returnLines(initNode, returnDigit, labelDigit)
                    lines.extend(tmp)               
                
                # Keep track of label for conditional block (if conditional exist)
                conditionLabel = None
                if element.children[1].children != []:
                    lines.append(f"goto <D.{labelDigit}>;")
                    conditionLabel = labelDigit
                    labelDigit += 1

                # Add the label that belongs to the start of the loop
                lines.append(f"<D.{labelDigit}>:")
                
                # Assign labels for start/end of loop
                loopStart = labelDigit 
                loopEnd = labelDigit + 1
                labelDigit += 2

                # recursivly deal with the body of the loop
                tmp, labelDigit = returnLines(element.children[3], returnDigit, labelDigit, loopEnd, loopStart)
                lines.extend(tmp)

                # Add the "end-of-loop" assignment/arithmetic
                if element.children[2].children != []:
                    initNode = ast.ASTNode("body", None)
                    initNode.children.append(element.children[2])
                    tmp, labelDigit = returnLines(initNode, returnDigit, labelDigit)
                    lines.extend(tmp) 

                # Start of conditionals for the loop
                if conditionLabel != None:
                    lines.append(f"<D.{conditionLabel}>:")
                    # TODO: Create tempoary AST if its a unary logical comparison
                    tmpNode = element.children[1]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[1])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))
                    tmp, tvs, labelList = simp.breakdownExpression(tmpNode, [], loopStart, loopEnd)
                    lines.extend(tmp)
                    lines.append(f"<D.{loopEnd}>:")
                    if labelList != []:
                        labelDigit = labelList[-1]
                else:
                    # No conditional (jump to start of body...always True)
                    lines.append(f"goto <D.{loopStart}>;")

                # increment twice for new index
                labelDigit += 2

                pass
            elif ind == 2:
                print("Body")
            elif ind == 3:
                # If/Else statement(s)

                # list of goto labels to be appended at end of if blocks
                end_if = []

                #for each case in a branch
                for case in element.children:
                    #create label for body if true and label to skip to correct place if false.
                    success_label = labelDigit
                    labelDigit += 1
                    failure_label = labelDigit
                    labelDigit += 1

                    #default is an 'else'. Only has one child, body
                    if case.name == "default":
                        #Get lines for the body and assign new labeldigit
                        tmp, labelDigit = returnLines(case.children[0], returnDigit, labelDigit, success_label, failure_label)
                        lines.extend(tmp)
                        continue

                    # TODO: Create tempoary AST if its a unary logical comparison
                    tmpNode = case.children[0]
                    if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(case.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))

                    #break down argument for if statement into smaller if statements
                    temp_lines, tvs, labelList = simp.breakdownExpression(tmpNode, [], success_label, failure_label)
                    # print (labelList)
                    if labelList != []:
                        labelDigit = labelList[-1] + 1
                    # print (labelDigit)
                    #adds broken down if statement
                    lines.extend(temp_lines)
                    
                    #Add goto for body statement
                    lines.append(f"<D.{success_label}>:")

                    #Get lines for the if body and assign new labeldigit
                    tmp, labelDigit = returnLines(case.children[1],returnDigit, labelDigit, success_label, failure_label)
                    # print (labelDigit)
                    lines.extend(tmp)

                    #append goto for end of if body
                    lines.append(f'goto <D.{labelDigit}>;')
                    end_if.append(labelDigit)
                    labelDigit += 1

                    lines.append(f"<D.{failure_label}>:")

                for i in end_if:
                    lines.append(f'<D.{i}>:')

            elif ind == 4: 
                #Return
                

                # If returns some type of arithmetic expression, breaks it down.
                if len(element.children) > 0 and element.children[0].children != []:
                    tmp, tvs, labelList = simp.breakdownExpression(element.children[0], [])
                    lines.extend(tmp)
                    lines.append(f"D.{returnDigit} = {tvs[-1]};")
                    lines.append(f"return D.{returnDigit};")
                    if labelList != []:
                        labelDigit = labelList[-1]

                elif len(element.children) > 0 and element.children[0].children == []:
                    lines.append(f"return {element.children[0].name};")

                # Returns nothing
                else:
                    lines.append(f"return;") 

            elif ind == 5:
                #Function Call
                func_call = element.children[0].name

                # function call has parameters
                if element.children[0] != []:
                    tmp, tvs, labelList = simp.breakdownExpression(element, tvs=[], labelList=[labelDigit])
                    tmp[-1] = tmp[-1].split(' = ')[1]
                    lines.extend(tmp)
                    if labelList != []:
                        labelDigit = labelList[-1] + 1
                
                # no parameters
                else:
                    lines.append(f"{func_call}();")

            elif ind == 6:
                #While and Do While

                # Jump straight to conditionals for only 'While' statements
                if element.name == "while":
                    lines.append(f"goto <D.{labelDigit}>;")
                
                # Keep track of label for conditional block
                conditionLabel = labelDigit
                labelDigit += 1
            
                # Add the label that belongs to the start of the loop
                lines.append(f"<D.{labelDigit}>:")
                
                # Assign labels for start/end of loop
                loopStart = labelDigit 
                loopEnd = labelDigit + 1
                labelDigit += 2

                # recursivly deal with the body of the loop
                tmp, labelDigit = returnLines(element.children[1], returnDigit, labelDigit, loopStart, loopEnd)
                lines.extend(tmp)

                # Start of conditionals for the loop
                lines.append(f"<D.{conditionLabel}>:")
                # TODO: Create tempoary AST if its a unary logical comparison
                tmpNode = element.children[0]
                if tmpNode.name not in ['||', '&&', "<=", "<", ">=", ">", "==", "!="]:
                        tmpNode = ast.ASTNode("!=", None)
                        tmpNode.children.append(element.children[0])
                        tmpNode.children.append(ast.ASTNode("0", tmpNode))
                tmp, tvs, labelList = simp.breakdownExpression(tmpNode, labelDigit, loopStart, loopEnd)
                lines.extend(tmp)
                lines.append(f"<D.{loopEnd}>:")

                if labelList != []:
                    labelDigit = labelList[-1]
                # increment twice for new index (twce, in case it was a do while)
                labelDigit += 2

            elif ind == 7:
                # Break
                lines.append(f"goto <D.{failureDigit}>;")

            elif ind == 8:
                # Continue
                lines.append(f"goto <D.{successDigit}>;")

            elif ind == 9:
                lines.append(f"goto {element.children[0].name}")
            elif ind == 10:
                lines.append(f"{element.children[0].name}:")
                if(len(element.children) > 1):
                    temp_lines, labelDigit = returnLines(element.children[1], returnDigit, labelDigit)
                    lines.extend(temp_lines)
            elif ind == 11:
                tmp, tvs, labelList_ = simp.breakdownExpression(element, [])
                lines.extend(tmp)
            else:
                print("Unsupported at this time")

        except Warning:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass
    
    return lines, labelDigit
