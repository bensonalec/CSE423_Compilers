""" 
This module only serves to simplify boolean and arithmetical expressions making sure that operations are taken care of correctly.
"""

import os
import re
import sys
from importlib.machinery import SourceFileLoader

ast = SourceFileLoader("AST_builder", f"{os.path.dirname(__file__)}/../frontend/AST_builder.py").load_module()

def breakdownExpression(root, tvs = [], success = None, failure = None, labelList = []):
    lines = []
    ns = []
    log_ops = ['||', '&&']
    comp_ops = ["<=", "<", ">=", ">", "==", "!="]
    arth_ops = ["+", "-", "*", "/", "%", "<<", ">>", "|", "&", "^", "!", "~"]
    spec_ops = ["++", "--"]
    ass_ops = ["=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "|=", "&=", "^="]
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
            tmp_label = max(labelList)
            labelList.append(tmp_label+1)
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
            tmp_label = max(labelList)
            labelList.append(tmp_label+1)
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
                if ass_ops.index(node.name) == 0:
                    # Case 1: Assignment is constant. ie. int i = 0
                    if len(node.children[1].children) == 0:
                        lines.append(f"{tvs.pop()} = {node.children[1].name};")
                    # Case 2: Assignment is complex
                    else:
                        pass
                        # removes the last occurrence of the variable name in tvs
                        del tvs[len(tvs)-1 - tvs[::-1].index(node.children[0].children[len(node.children[0].children)-1].name)]

                        lines.append(f"{node.children[0].children[len(node.children[0].children)-1].name} {node.name} {tvs.pop()};")
                else:
                    # create a temporary parent node
                    p = ast.ASTNode("=", None)

                    # append the variable who is assigned a value as its first child
                    p.children.append(node.children[0])

                    # create a right subtree with the correct operation
                    r = ast.ASTNode(node.name[:-1], p)
                    p.children.append(r)

                    # assign the variable as the left operand of the new expression
                    r.children.append(node.children[0])

                    # assign the remaining operations as the right operand of the new expression
                    r.children.append(node.children[1])

                    tmp, tvs, labelList = breakdownExpression(p, tvs, success, failure, labelList)

                    lines.extend(tmp)

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
