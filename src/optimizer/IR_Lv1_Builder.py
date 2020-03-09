import re
import sys
import importlib

simp = importlib.import_module("simplify", __name__)
ast = importlib.import_module("AST_builder", __name__)


class LevelOneIR():
    def __init__(self,astHead,symTable):
        self.astHead = astHead
        self.symTable = symTable

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
            for x in lines:
                print(x)
            returnDigit = labelDigit + 1

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

def returnLines(node,returnDigit,labelDigit):
    lines = []
    for element in node.children:
        try:
            splits = [["=","+="],["for"],["body"],["branch"],["return"],["call"],["while","do_while"],["break"],["continue"],["goto"],["label"]]
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
                tmp, labelDigit = simp.breakdownArithmetic(element.children[1], labelDigit)
                lines.extend(tmp)
                lines.append(f"{varName} = D.{labelDigit-1};")

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
                tmp, labelDigit = returnLines(element.children[3], returnDigit, labelDigit)
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
                    tmp, labelDigit = simp.breakdownBoolean(element, labelDigit, loopStart, loopEnd)
                    lines.extend(tmp)
                    lines.append(f"<D.{loopEnd}>:")
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
                    
                    #default is an 'else'. Only has one child, body
                    if case.name == "default":
                        #Get lines for the body and assign new labeldigit
                        tmp, labelDigit = returnLines(case.children[0], returnDigit, labelDigit)
                        lines.extend(tmp)
                        continue

                    #create label for body if true and label to skip to correct place if false.
                    success_label = f"{labelDigit}"
                    labelDigit += 1
                    failure_label = f"{labelDigit}"
                    labelDigit += 1

                    #break down argument for if statement into smaller if statements
                    temp_lines, labelDigit = simp.breakdownBoolean(case, labelDigit, success_label, failure_label)
                    
                    #adds broken down if statement
                    lines.extend(temp_lines)
                    
                    #Add goto for body statement
                    lines.append(f"<D.{success_label}>:")

                    #Get lines for the if body and assign new labeldigit
                    tmp, labelDigit = returnLines(case.children[1],returnDigit, labelDigit)
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
                if len(element.children) > 0:
                    tmp, tmpDigit = simp.breakdownArithmetic(element.children[0], returnDigit)
                    lines.extend(tmp)
                    lines.append(f"D.{returnDigit} = D.{tmpDigit-1}")
                    lines.append(f"return D.{returnDigit};")
                
                # Returns nothing
                else:
                    lines.append(f"return;") 

            elif ind == 5:
                #Function Call
                func_call = element.children[0].name

                # function call has parameters
                if func_call.children != []:
                    tmp, labelDigit = simp.breakdownArithmetic(func_call.children[0], labelDigit)
                    lines.extend(tmp)
                    lines.append(f"{func_call.name}(D.{labelDigit});")
                    returnDigit += labelDigit
                
                # no parameters
                else:
                    lines.append(f"{func_call.name}();")

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
                tmp, labelDigit = returnLines(element.children[1], returnDigit, labelDigit)
                lines.extend(tmp)

                # Start of conditionals for the loop
                lines.append(f"<D.{conditionLabel}>:")
                tmp, labelDigit = simp.breakdownBoolean(element, labelDigit, loopStart, loopEnd)
                lines.extend(tmp)
                lines.append(f"<D.{loopEnd}>:")

                # increment twice for new index (twce, in case it was a do while)
                labelDigit += 2

            elif ind == 7:
                print("Break")
            elif ind == 8:
                print("Continue")
            elif ind == 9:
                print("Goto")
            elif ind == 10:
                print("Label")
            else:
                print("Unsupported at this time")

        except Warning:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass
    
    return lines, labelDigit