import sys
import os
import importlib
sys.path.insert(0, '../src/frontend')
sys.path.insert(0, '../src/optimizer')
sys.path.insert(0, '../src/backend')

import unittest
from unittest.mock import patch
from copy import deepcopy

pre = importlib.import_module("preprocessor",  "../src/frontend")
lex = importlib.import_module("lexer",         "../src/frontend")
par = importlib.import_module("parser",        "../src/frontend")
ast = importlib.import_module("AST_builder",   "../src/frontend")
sem = importlib.import_module("semantics",     "../src/frontend")
sym = importlib.import_module("symbol_table",  "../src/frontend")
ir = importlib.import_module("IR_Lv1_Builder", "../src/optimizer")
alloc = importlib.import_module("allocator", "../src/backend")
asmn = importlib.import_module("ASMNode", "../src/backend")
# ir = importlib.import_module("IR_Lv1_Builder", "../src/optimizer")

C_root = "./programs/"

offset = max([len(x) for x in os.listdir(C_root)]) + 1 + max([len("Preprocessor"), len("Lexer"), len("Parser"), len("AST"), len("Symbol"), len("Semantic"), len("IR"), len("Assembly")])

stat_dict = {
    "OK" : "\033[32mOK\033[00m",
    "FAIL" : "\033[31mFAIL\033[00m",
    "SKIPPED" : "\033[34mSKIPPED\033[00m",
}
def output(test, file, status):
    print(f"{test} test for {file.ljust(offset-len(test))}{stat_dict[status]}")

def retrieve_lex(file):
    lexer = lex.Lexer().get_lexer()
    tokens = lexer.lex(file)
    lex.validateTokens(tokens)

    return tokens

def retrieve_par(file):
    pg = par.Parser()
    pg.parse()
    parser = pg.get_parser()

    parser.parse(retrieve_lex(file))

    head = pg.getTree()

    return head

def retrieve_ast(file):
    astree = ast.buildAST(retrieve_par(file))

    return astree

def retrieve_sym(file):
    symb = sym.symbol_table(retrieve_ast(file))
    symb.analyze()

    return symb

def retrieve_sem(file):
    asTree = retrieve_ast(file)
    sym = retrieve_sym(file)
    semanticAnal = sem.semantic(asTree,sym.symbols)
    semanticAnal.semanticAnalysis()

    return semanticAnal.lineSemanticErrors()

def retrieve_ir(file):
    astHead = retrieve_ast(file)
    symbolTable = retrieve_sym(file)

    ir1 = ir.LevelOneIR(astHead, symbolTable)
    ir1.construct()
    return ir1

def retrieve_asm(file, name):
    ir1 = retrieve_ir(file)
    asm = [z for x in ir1.IR for y in x.treeList for z in y.asm()]

    # Allocate registers for assembly instructions
    allocator = alloc.Allocator
    asm = allocator.allocateRegisters(asm)

    asm = [
        asmn.ASMNode(None, None, None, boilerPlate=f".file \"{name}\""),
        asmn.ASMNode( None, None,None, boilerPlate=f".text"),
    ] + asm

    return asm


class PreprocessorTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = []
        expected_path = os.path.abspath("./expected_output/preprocessor")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:

                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    self.assertEqual(pre.run(inp.read(), f"{C_root}/{file}"), exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("Preprocessor", file, status)

class LexerTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = []
        expected_path = os.path.abspath("./expected_output/lexer")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:

                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    proc = pre.run(inp.read(), f"{C_root}/{file}")
                    tok = retrieve_lex(proc)
                    self.assertEqual(lex.tokensToString(tok), exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("Lexer", file, status)

class ParserTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = []
        expected_path = os.path.abspath("./expected_output/parser")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:

                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    proc = pre.run(inp.read(), f"{C_root}/{file}")
                    pars = retrieve_par(proc)
                    self.assertEqual(pars.__repr__(), exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("Parser", file, status)

class ASTTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = []
        expected_path = os.path.abspath("./expected_output/ast")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:

                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    proc = pre.run(inp.read(), f"{C_root}/{file}")
                    asttree = retrieve_ast(proc)
                    self.assertEqual(str(asttree), exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("AST", file, status)

class SymbolTableTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = ["Functions_Strings.c", "Initialization_Strings.c"]
        expected_path = os.path.abspath("./expected_output/symboltable")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:

                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    proc = pre.run(inp.read(), f"{C_root}/{file}")
                    symb = retrieve_sym(proc)
                    self.assertEqual(str(symb), exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("Symbol Table", file, status)

class SemanticTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = ["Initialization_Strings.c","Functions_Strings.c"]
        expected_path = os.path.abspath("./expected_output/semantic")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:
                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    proc = pre.run(inp.read(), f"{C_root}/{file}")
                    sema = retrieve_sem(proc)
                    self.assertEqual(sema, exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("Semantic", file, status)

class IRTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = ["Initialization_Strings.c","Functions_Strings.c"]
        expected_path = os.path.abspath("./expected_output/ir")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:
                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    proc = pre.run(inp.read(), f"{C_root}/{file}")
                    l1ir = retrieve_ir(proc)
                    self.assertEqual(str(l1ir), exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("IR", file, status)

class ASMTests(unittest.TestCase):

    maxDiff = None

    def test(self):
        self.skip = ["Initialization_Strings.c","Functions_Strings.c", "Keywords.c", "Switch.c"]
        expected_path = os.path.abspath("./expected_output/asm")
        print("")
        for file in [x for x in sorted(os.listdir(C_root)) if x.endswith('.c')]:
            status = "FAIL"
            if file not in self.skip:
                with self.subTest(), open(f"{C_root}/{file}", "r") as inp, open(f"{expected_path}/{file[:-2]}") as exp:
                    proc = pre.run(inp.read(), f"{C_root}/{file}")
                    asm = retrieve_asm(proc,file)
                    self.assertEqual("\n".join([str(x) for x in asm]) + "\n", exp.read())
                    status = "OK"
            else:
                status = "SKIPPED"

            output("ASM", file, status)

if __name__ == '__main__':
    unittest.main()
