import re
import sys

def build_case(node):
    #builds argement to go in gimple string

    #first node is the opperator
    opp = node.name

    #next find first arguement
    if node.children[0].name == "var" or node.children[0].name == "call":
        first_arg = node.children[0].children[0].name
    else:
        first_arg = node.children[0].name

    #next find second arguement
    if node.children[1].name == "var" or node.children[1].name == "call":
        second_arg = node.children[1].name
    else:
        second_arg = node.children[1].name

    return f'{first_arg} {opp} {second_arg}'


def breakdownBoolean(root, labelDigit, success_label, failure_label):

    #NOTE root needs to be the parent of the first "&&" or "||"

    #list of individual conditionals
    conds = []

    #an array of symbols
    syms = []
    lines = []

    while(root.children[0].name == "&&" or root.children[0].name == "||"):
        syms.append(root.children[0])
        conds.append(root.children[1])
        root = root.children[0]
    for k in root.children:
        if k.name in ["<=", "<", ">=", ">", "==", "!="]:
            conds.append(k)
    if root.name in ["<=", "<", ">=", ">", "==", "!="]:
        conds.append(root)

    next_opp = None
    tmp_lab = []
    for ind, case in enumerate(conds[::-1]):
        if case.name == "body":
            continue

        if ind == 0:
            if len(syms) > 0:
                cur_opp = syms.pop()
            else:
                cur_opp = None

            next_opp = cur_opp

        else:
            cur_opp = next_opp
            if syms != []:
                next_opp = syms.pop()
            else:
                next_opp = None

        temp_label1 = f"{labelDigit}"
        labelDigit += 1
        temp_label2 = f"{labelDigit}"
        labelDigit += 1

        if len(case.children) > 1:
            declare, labelDigit = breakdownArithmetic(case.children[1], labelDigit)
            #declare is a list of returned arithmetic lines.

            if declare != []:

                #add declarations before
                lines.extend(declare)

                #replace operator with created variable name
                arg = build_case(case)
                arg = arg.replace(case.children[1].name, declare[-1].split(" ")[0])

            else:
                #None complex arithmatic
                arg = build_case(case) 
        
        else:
            #if only variable name
            arg = case.children[0].name

        #appends if statement and labels based on current and next opperator. This also does short circuiting
        if cur_opp == None:
            lines.append(f'if ({arg}) goto <D.{success_label}>; else goto <D.{failure_label}>;')

        elif cur_opp.name == "&&" and not next_opp == None:
            if next_opp.name == "||":
                lines.append(f'if ({arg}) goto <D.{temp_label2}>; else goto <D.{temp_label1}>;')
                lines.append(f'<D.{temp_label1}>:')
                tmp_lab.append(temp_label2)
            else:
                lines.append(f'if ({arg}) goto <D.{temp_label1}>; else goto <D.{temp_label2}>;')
                lines.append(f'<D.{temp_label1}>:')
                tmp_lab.append(temp_label2)
        elif cur_opp.name == "||" and not next_opp == None:
            if next_opp.name == "&&":
                lines.append(f'if ({arg}) goto <D.{temp_label1}>; else goto <D.{temp_label2}>;')
                lines.append(f'<D.{temp_label1}>:')
                tmp_lab.append(temp_label2)                           
            else:
                lines.append(f'if ({arg}) goto <D.{temp_label1}>; else goto <D.{temp_label2}>;')
                lines.append(f'<D.{temp_label2}>:')
                tmp_lab.append(temp_label1)
        else:
            #this is the last operation
            if cur_opp.name == "&&":
                    lines.append(f'if ({arg}) goto <D.{success_label}>; else goto <D.{failure_label}>;')  
            elif cur_opp.name == "||":
                    lines.append(f'if ({arg}) goto <D.{success_label}>; else goto <D.{failure_label}>;')                                                          

        #if next conditional statement is different
        if next_opp == None or next_opp.name != cur_opp.name:
            save = []
            if next_opp == None and tmp_lab != []: 

                #replace with success label in lines
                for i in lines:
                    for j in tmp_lab:
                        if j in i:
                            if cur_opp.name == "||":
                                lines[lines.index(i)] = i.replace(j, f'{success_label}')
                            else:
                                lines[lines.index(i)] = i.replace(j, f'{failure_label}') 

            else:
                if tmp_lab != []: 
                    #append goto for to be used in next statement
                    save.append(tmp_lab.pop())
                for i in tmp_lab:
                    #add label
                    lines.append(f'{i}:')

                tmp_lab = save

    return lines, labelDigit



def breakdownArithmetic(root, labelDigit):
    ntv = [root]

    isOp = r'^(\+|\-|\/|\*|\%)$'
    opCheck = re.compile(isOp)
    Stack = []

    lines = []
    
    # fill up stack with all operands / operations 
    while ntv != []:
        cur = ntv[0]
        Stack.append(cur.name)

        # Beginning of function call parameters
        if cur.parent.name == 'call':
            
            param_string = ""
            for param in cur.children:
                tmp, labelDigit = breakdownArithmetic(param, labelDigit)
                lines.extend(tmp)
                param_string += f"D.{labelDigit-1},"

            #remove params so they dont get added to Stack
            ntv[0].children = []

            Stack.append(f"({param_string[:-1]})") #tmp variable
            

        ntv = [x for x in cur.children] + ntv[1:]

    last = len(Stack)
    for i in Stack[::-1]:
        ind = last- 1
        
        if(opCheck.match(i)):

            # two operands
            v1 = Stack[ind+1]
            v2 = Stack[ind+2]

            # append the operation
            lines.append(f"D.{labelDigit} = {v1} {i} {v2};")

            # modify the stack to get rid of operands but keep new tmp variable
            Stack = Stack[:ind] + [f"D.{labelDigit}"] + Stack[ind+3:]

            # increment tmp variable for IR
            labelDigit += 1

        elif(i == "var"):

            # modify stack to get rid of 'var'
            Stack = Stack[:ind] + Stack[ind+1:]

        elif(i == "call"):

            # modify function name to include parameter tmp variable
            Stack[ind+1] = Stack[ind+1] + f"{Stack[ind+2]}"

            # modify stack to get rid of 'call'
            Stack = Stack[:ind] + Stack[ind+1:]

            # modify stack to get rid of parameter tmp variable
            Stack = Stack[:ind+1] + Stack[ind+2:]

        else:
            pass

        last -= 1

    # final assignment to the passed in variable if something still on stack (i.e. literal integer)
    if len(Stack) > 0:
        lines.append(f"D.{labelDigit} = {Stack[0]};")
        labelDigit += 1

    return lines, labelDigit
