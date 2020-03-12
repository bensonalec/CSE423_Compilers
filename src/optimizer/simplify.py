""" 
This module only serves to simplify boolean and arithmetical expressions making sure that operations are taken care of correctly.
"""

import os
import re
import sys
from importlib.machinery import SourceFileLoader

ast = SourceFileLoader("AST_builder", f"{os.path.dirname(__file__)}/../frontend/AST_builder.py").load_module()

def build_case(node, list_one, list_two):

    if list_two == [] and list_one == []:
        if node.children != []:
            arg = f"{node.children[0].name} > 0"
            return arg
        else:
            arg = f"{node.name} > 0"
            return arg

    elif list_two == []:
        arg = f"{list_one[-1].split(' ')[0]} > 0"
        return arg

    else:

        #first node is the opperator
        opp = node.name

        #next find second arguement
        second_arg = list_two[-1].split(' ')[0]

        #next find first arguement
        first_arg = list_one[-1].split(' ')[0]

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
        conds.append(k)

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

        # case is a conditional with two children
        if len(case.children) > 1 and case.name in ["<=", "<", ">=", ">", "==", "!="]:
            declare_one, labelDigit = breakdownExpression(case.children[0], labelDigit)
            declare_two, labelDigit = breakdownExpression(case.children[1], labelDigit)
           
            lines.extend(declare_one)
            lines.extend(declare_two)

            arg = build_case(case, declare_one, declare_two)

        # case is without conditional
        else:
            declare_one, labelDigit = breakdownExpression(case, labelDigit)
            lines.extend(declare_one)
            arg = build_case(case, declare_one, []) 
        

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
                    lines.append(f'<D.{i}>:')

                tmp_lab = save

    return lines, labelDigit



def breakdownArithmetic(root, labelDigit):

    # log_ops = ['||', '&&']
    # comp_ops = ["<=", "<", ">=", ">", "==", "!="]
    arth_ops = ["+", "-", "*", "/", "%", "<<", ">>", "!", "~"]
    spec_ops = ["++", "--"]
    ass_ops = ["="]
    id_ops = ["var", "call"]




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

def breakdownExpression(root, tvs = [], success = None, failure = None, labelList = []):
    lines = []
    ns = []
    log_ops = ['||', '&&']
    comp_ops = ["<=", "<", ">=", ">", "==", "!="]
    arth_ops = ["+", "-", "*", "/", "%", "<<", ">>", "!", "~"]
    spec_ops = ["++", "--"]
    ass_ops = ["="]
    id_ops = ["var", "call"]

    if success not in labelList and success != None:
        labelList.append(success)
    if failure not in labelList and failure != None:
        labelList.append(failure)

    # If there is a logical operator remove all comparison operators to avoid double evaluation
    if root.name in log_ops:
        index = log_ops.index(root.name)
        if index == 0:
            # OR
            tmp_label = max(labelList)+1
            labelList.append(tmp_label)
            tmpNode = root.children[0]
            if tmpNode.name not in comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[0])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))
            lhs, tvs, labelList = breakdownExpression(tmpNode, tvs, success, tmp_label, labelList)
            tmpNode = root.children[1]
            if tmpNode.name not in comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[1])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))
            rhs, tvs, labelList = breakdownExpression(tmpNode, tvs, success, failure, labelList)
            lines.extend(lhs)
            lines.append(f"<D.{tmp_label}>:")
            lines.extend(rhs)
        elif index == 1:
            # AND
            tmp_label = max(labelList)+1
            labelList.append(tmp_label)
            tmpNode = root.children[0]
            if tmpNode.name not in comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[0])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))
            lhs, tvs, labelList = breakdownExpression(tmpNode, tvs, tmp_label, failure, labelList)
            tmpNode = root.children[1]
            if tmpNode.name not in comp_ops and tmpNode.name not in log_ops:
                tmpNode = ast.ASTNode("!=", None)
                tmpNode.children.append(root.children[1])
                tmpNode.children.append(ast.ASTNode("0", tmpNode))
            rhs, tvs, labelList = breakdownExpression(tmpNode, tvs, success, failure, labelList)
            lines.extend(lhs)
            lines.append(f"<D.{tmp_label}>:")
            lines.extend(rhs)
    else:
        ntv = [root]

        while ntv != []:
            cur = ntv[-1]
            ns.insert(0, cur)
            ntv = ntv[:-1] + cur.children

        ns = [x for x in ns if x.name in arth_ops or x.name in spec_ops or x.name in ass_ops or x.name in id_ops or x.name in comp_ops]
        for node in ns:
        
            if node.name in comp_ops:
                ops = [tvs.pop() for x in node.children if len(x.children) != 0]
                
                # Case 1: ops is empty
                if ops == [] and len(node.children) > 1:
                    v1 = node.children[0].name 
                    v2 = node.children[1].name

                # Case 2: two elem in ops
                elif len(ops) == 2:
                    v2 = ops[0]
                    v1 = ops[1]

                else:
                    pos = [node.children.index(x) for x in node.children if len(x.children) != 0 and len(node.children) > 1]

                    # Case 3: one elem in ops but its the left element in the operation
                    if pos == [0]:
                        v1 = ops[0]
                        v2 = node.children[1].name

                    # Case 4: one elem in ops but its the right element in the operation
                    elif pos == [1]:
                        v1 = node.children[0].name
                        v2 = ops[0]

                lines.append(f"if ({v1} {node.name} {v2}) goto <D.{success}>; else goto <D.{failure}>;")

            elif node.name in arth_ops:
                ops = [tvs.pop() for x in node.children if len(x.children) != 0]

                # if node.parent.parent.name == "call":
                #     continue
                
                # Case 1: ops is empty
                if ops == [] and len(node.children) > 1:
                    lines.append(f"_{len(tvs)} = {node.children[0].name} {node.name} {node.children[1].name};")
                # Case 2: two elem in ops
                elif len(ops) == 2:
                    lines.append(f"_{len(tvs)} = {ops[0]} {node.name} {ops[1]};")
                else:
                    pos = [node.children.index(x) for x in node.children if len(x.children) != 0 and len(node.children) > 1]

                    # Case 3: one elem in ops but its the left element in the operation
                    if pos == [0]:
                        lines.append(f"_{len(tvs)} = {ops[0]} {node.name} {node.children[1].name};")
                    # Case 4: one elem in ops but its the right element in the operation
                    elif pos == [1]:
                        lines.append(f"_{len(tvs)} = {node.children[0].name} {node.name} {ops[0]};")
                    # Case 5: Its a unary operator
                    elif pos == []:
                        lines.append(f"_{len(tvs)} = {node.name}{ops[0] if ops != [] else node.children[0].name};")
                
                tvs.append(f"_{len(tvs)}")

            elif node.name in spec_ops:
                pass
                var = tvs.pop()
                lines.append(f"_{len(tvs)} = {var};")
                if [node.children.index(x) for x in node.children if x.name == "NULL"][0] == 1:
                    lines.append(f"{var} = {var} {node.name[0]} 1;")
                else:
                    lines.insert(len(lines) - 2, f"{var} = {var} {node.name[0]} 1;")
            
            elif node.name in ass_ops:
                # Case 1: Assignment is constant. ie. int i = 0
                if len(node.children[1].children) == 0:
                    lines.append(f"{tvs.pop()} = {node.children[1].name};")
                # Case 2: Assignment is complex
                else:
                    pass
                    # removes the last occurrence of the variable name in tvs
                    del tvs[len(tvs)-1 - tvs[::-1].index(node.children[0].children[len(node.children[0].children)-1].name)]

                    lines.append(f"{node.children[0].children[len(node.children[0].children)-1].name} {node.name} {tvs.pop()};")

            elif node.name in id_ops:
                if node.name == "var":
                    tvs.append(f"{node.children[len(node.children)-1].name}")
                elif node.name == "call":
                    param_string = ""
                    complex_params = [tvs.pop() for x in node.children[0].children if len(x.children) != 0]
                    for i in node.children[0].children:
                        if i.children == []:
                            param_string += i.name + ","
                            pass
                        else:
                            param_string += complex_params.pop() + ","
                    lines.append(f"_{len(tvs)} = {node.children[0].name}({param_string[:-1]});")
                    tvs.append(f"_{len(tvs)}")

    return lines, tvs, labelList
