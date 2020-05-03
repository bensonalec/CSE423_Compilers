"""
This module is only supposed to generate the documentation for the compiler as a whole including User Manual.
"""

import os
import re
import itertools
import pathlib

import bs4

from copy import deepcopy
from importlib.machinery import SourceFileLoader

print (pathlib.Path(__file__).parent)

prep = SourceFileLoader("preprocessor",   f"{pathlib.Path(__file__).parent}/../src/frontend/preprocessor.py").load_module()
lexe = SourceFileLoader("lexer",          f"{pathlib.Path(__file__).parent}/../src/frontend/lexer.py").load_module()
pars = SourceFileLoader("parser",         f"{pathlib.Path(__file__).parent}/../src/frontend/parser.py").load_module()
astt = SourceFileLoader("AST_builder",    f"{pathlib.Path(__file__).parent}/../src/frontend/AST_builder.py").load_module()
sema = SourceFileLoader("semantics",      f"{pathlib.Path(__file__).parent}/../src/frontend/semantics.py").load_module()
symbol = SourceFileLoader("symbol_table", f"{pathlib.Path(__file__).parent}/../src/frontend/symbol_table.py").load_module()
ir1 = SourceFileLoader("IR_Lv1_Builder",  f"{pathlib.Path(__file__).parent}/../src/optimizer/IR_Lv1_Builder.py").load_module()
asmn = SourceFileLoader("ASMNode",        f"{pathlib.Path(__file__).parent}/../src/backend/ASMNode.py").load_module()
alloc = SourceFileLoader("Allocator",     f"{pathlib.Path(__file__).parent}/../src/backend/allocator.py").load_module()
def retrieve_lex(file):
    lexer = lexe.Lexer().get_lexer()
    tokens = lexer.lex(file)
    lexe.validateTokens(tokens)

    return [(tokens, lexe.tokensToString(deepcopy(tokens)))]

def retrieve_par(file):
    pg = pars.Parser()
    pg.parse()
    parser = pg.get_parser()
    tmp = retrieve_lex(file)
    parser.parse(tmp[-1][0])

    head = pg.getTree()

    return tmp + [(head, head.__repr__())]

def retrieve_ast(file):
    tmp = retrieve_par(file)
    astree = astt.buildAST(tmp[-1][0])

    return tmp + [(astree, str(astree))]

def retrieve_sym(file):
    tmp = retrieve_ast(file)
    sym = symbol.symbol_table(tmp[-1][0])
    sym.analyze()

    return tmp + [(sym, str(sym))]

def retrieve_sem(file):
    tmp = retrieve_sym(file)
    semanticAnal = sema.semantic(tmp[-2][0],tmp[-1][0].symbols)
    semanticAnal.semanticAnalysis()

    return tmp

def retrieve_ir1(file):
    tmp = retrieve_sem(file)

    ir = ir1.LevelOneIR(tmp[-2][0], tmp[-1][0])
    ir.construct()

    return tmp + [(ir, str(ir))]

def retrieve_O1(file):
    tmp = retrieve_ir1(file)

    ir = deepcopy(tmp[-1][0])

    ir.optimize(1)

    return tmp + [(ir, str(ir))]

def retrieve_O2(file):
    tmp = retrieve_O1(file)

    ir = deepcopy(tmp[-2][0])

    ir.optimize(2)

    return tmp + [(ir, str(ir))]

def retrieve_asm(file, name):
    tmp = retrieve_O2(file)
    asm = [z for x in tmp[-3][0].IR for y in x.treeList for z in y.asm()]
    allocator = alloc.Allocator
    asm = allocator.allocateRegisters(asm)

    asm = [
        asmn.ASMNode(None, None, None, boilerPlate=f".file \"{name}\""),
        asmn.ASMNode( None, None,None, boilerPlate=f".text"),
    ] + asm

    return tmp + [(asm, "\n".join([str(x) for x in asm]))]

if __name__ == "__main__":
    # Setus up /docs for the newly generated documentation.
    os.system("rm -rf ../docs/*")
    os.system("pdoc --html -o ../docs ../src")

    # Opens the necessary files to modify
    index = open("../docs/src/index.html", 'r+')
    user = open("User Manual.html", "r")
    design = open("design_doc.html", "r")

    # Reads the content if each file
    page_parser = bs4.BeautifulSoup(index.read(), "html.parser")
    usr_parser = bs4.BeautifulSoup(user.read(), "html.parser")
    des_parser = bs4.BeautifulSoup(design.read(), "html.parser")

    # Store the number of columns to span for later
    colspan = len(usr_parser.table.thead.tr.find_all("th"))

    tf = usr_parser.table.tfoot

    tf['id'] = "table_foot"

    for td in tf.select("td"):
        td['colspan'] = colspan

    # Adds some inline styling to certain tags located within the design document.
    for th in itertools.chain(des_parser.select("th"), usr_parser.select("th")):
        # style = "padding: 10px;"
        # if 'style' in th:
        #     th['style'] += style
        # else:
        #     th['style'] = style

        if len(th.parent.find_all("th")) == 1:
            th['colspan'] = colspan

    for td in itertools.chain(des_parser.select("td"), usr_parser.select("td")):
        b = True

        style = "text-align: center; "

        if td.string == "✓":
            style += "background: rgb(170, 255, 170);"
        elif td.string == "✕":
            style += "background: rgb(255, 170, 170);"
        elif td.string == "−":
            style += "background: rgb(170, 170, 170);"
        elif td.string == "…":
            style += "background: rgb(255, 255, 170);"
        else:
            b = False

        if b:
            if 'style' in td:
                td['style'] += style
            else:
                td['style'] = style

    for pre in itertools.chain(des_parser.select("pre"), usr_parser.select("pre")):
        style = "overflow-x: auto;"
        if 'style' in pre:
            pre['style'] += style
        else:
            pre['style'] = style

    for sup in usr_parser.select("sup"):
        sup.string.wrap(usr_parser.new_tag("a", href="#table_foot"))

    # Assigns IDs for the table of contents
    sections = []
    idx = -1
    examples_id = None

    for idx, dd in enumerate(des_parser.select("h2"), idx + 1):
        dd['id'] = f"section_{idx}" if 'id' not in dd else dd['id']
        sections.append(dd)

    for idx, h3 in enumerate(des_parser.select("h3"), idx + 1):
        h3['id'] = f"section_{idx}" if 'id' not in h3 else h3['id']
        sections.append(h3)

    for idx, um in enumerate(usr_parser.select("h2"), idx + 1):
        um['id'] = f"section_{idx}" if 'id' not in um else um['id']
        sections.append(um)

    for idx, h3 in enumerate(usr_parser.select("h3"), idx + 1):
        if h3.string == "Examples of C Programs and their Intermediate Representations":
            examples_id = f"#section_{idx}"
        h3['id'] = f"section_{idx}" if 'id' not in h3 else h3['id']
        sections.append(h3)

    for a in des_parser.select("a"):
        a['href'] = examples_id if a['href'] == "C_EXAMPLES" else a['href']

    # Generates and inserts the table of contents into the website
    for ul in page_parser.select(".toc ul"):
        for section in sections[::-1]:
            tag = page_parser.new_tag("li")
            tag.string = section.string
            tag.string.wrap(page_parser.new_tag("a", href=f"#{section['id']}"))
            tag.a.string.wrap(page_parser.new_tag(f"h{int(section.name[1])+1}"))
            ul.insert(0, tag)

    # Adjusts the title of the page
    header = page_parser.find("header")
    for child in header.children:
        child.string = "CSE 423 Compilers"

    # Generates and replaces the header of the document.
    names = page_parser.new_tag("div", style="display: flex; flex-wrap: wrap; justify-content: center;")

    span_a = page_parser.new_tag("span", style="flex-grow: 1;")
    span_j = page_parser.new_tag("span", style="flex-grow: 1;")
    span_o = page_parser.new_tag("span", style="flex-grow: 1;")
    span_k = page_parser.new_tag("span", style="flex-grow: 1;")

    span_a.string = "Alexander Benson"
    span_j.string = "Jacob Garcia"
    span_o.string = "Ole Jeger Hoffstuen"
    span_k.string = "Keaton Jones"

    span_a.string.wrap(page_parser.new_tag("h5"))
    span_j.string.wrap(page_parser.new_tag("h5"))
    span_o.string.wrap(page_parser.new_tag("h5"))
    span_k.string.wrap(page_parser.new_tag("h5"))

    names.append(span_a)
    names.append(span_j)
    names.append(span_o)
    names.append(span_k)

    header.insert_after(names)

    doc_loc = usr_parser.select("dl")[-1]
    comp_flags = [
        ("Token List", 0),
        ("Parse Tree", 1),
        ("Abstract Syntax Tree", 2),
        ("Symbol Table", 3),
        ("Linear IR (-O0)", 4),
        ("Linear IR (-O1)", 5),
        ("Linear IR (-O2)", 6),
        ("x86-64 GAS Assembly (-O0)", 7)
    ]

    for program in [x for x in sorted(pathlib.Path("../test/programs").iterdir()) if x.suffix == '.c' ]:
        print (program)
        title = usr_parser.new_tag("dt")
        title.string = program.stem
        title.string.wrap(usr_parser.new_tag("h4"))

        data = usr_parser.new_tag("dd")
        data.append(usr_parser.new_tag("div", attrs={'class' : "example_buttons"}))
        for name in ["Program"] + [x[0] for x in comp_flags]:
            a = usr_parser.new_tag("a")
            a.string = name
            data.select("div")[-1].append(a)

        par = usr_parser.new_tag("div", attrs={'class' : "example_representations"})
        outs = retrieve_asm(prep.run(program.read_text(), program.resolve()), program.name)
        outs.insert(0, ("", program.read_text()))
        for idx, arg in enumerate([""] + [x[-1] for x in comp_flags]):
            div = usr_parser.new_tag("div")
            div.append(usr_parser.new_tag("pre", attrs={'style' : "overflow-x: auto;"}))
            div.pre.string = outs[idx][-1]
            if idx == 0:
                div.pre.string.wrap(usr_parser.new_tag("code", attrs={'class' : "C++ hljs"}))

            par.append(div)
        data.append(par)
        doc_loc.append(title)
        doc_loc.append(data)
        # break

    # Add inline javascript to allow for management of examples
    for i, (link, rep) in enumerate(zip(usr_parser.select(".example_buttons"), usr_parser.select(".example_representations"))):
        for j, (a, div) in enumerate(zip(link.children, rep.children)):
            if type(a) != type(bs4.NavigableString("")) or type(div) != type(bs4.NavigableString("")):
                a["onclick"] = f"""[...document.getElementsByClassName("representation_{i}")].forEach(function(elem, index) {{ if (index === {(j)}) {{ elem.style.display = "block";}} else {{ elem.style.display = "none";}}}})"""
                div['class'] = f"representation_{i}" if 'class' not in div else div['class']
                div['style'] = "display: none;" if 'style' not in div else div['style']
            rep.div['style'] = "display: block;"

    content = page_parser.find("section")
    content.append(des_parser)
    content.append(usr_parser)

    # Writes content to the file
    index.seek(0)
    index.write(page_parser.prettify())

    # Closes the files as they aren't needed anymore
    index.close()
    user.close()
    design.close()

    # Ensures consistent folder structure with what is expected by github.
    os.system("mv ../docs/src/* ../docs/")
    os.system("rm -rf ../docs/src")
    os.system("cp ./architecture.png ../docs/architecture.png")