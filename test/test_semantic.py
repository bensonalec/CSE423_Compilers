import sys
import os
sys.path.insert(0,'../src/frontend')

import unittest
import lexer as lex
import parser as par
import preprocessor as pre
import AST_builder as ast
import semantics as sem


path_to_C_files = "./programs/"
path_to_output_files = "./expected_output/semantic/"

class SemanticAnalysisTest(unittest.TestCase):

    # Add program into list if for some reason, we shouldn't test it.
    skip_programs = ["While.c","Identifiers_Variables_Functions.c","Unary.c","Pre_Processor.c","Assignment.c","Goto.c","If_Else.c","Return.c"]

    maxDiff = None

    def test_semantic(self):
        print()

        for c_filename in os.listdir(path_to_C_files):
            
            if c_filename.endswith('.c') and c_filename not in self.skip_programs:
                print(c_filename)
                fi = open(path_to_C_files + c_filename)
                text_input = fi.read()
                fi.close()

                # Naming scheme for expected output is same as C-file, but no extension
                expected_filename = os.path.splitext(c_filename)[0]
                fi = open(path_to_output_files + expected_filename)
                expected = fi.read()
                fi.close()
                lexer = lex.Lexer().get_lexer()
                tokens = lexer.lex(text_input)
                lex.validateTokens(tokens)

                pg = par.Parser()
                pg.parse()
                parser = pg.get_parser()
                parser.parse(tokens)

                head = pg.getTree()

                astree = ast.buildAST(head)

                sym = sem.symbol_table(astree)
                sym.analyze()
                
                self.assertEqual(sym.lineSemanticErrors(), expected)
                
                print(f"Semantic Analysis test passed with: {c_filename}")

if __name__ == '__main__':
    unittest.main()

