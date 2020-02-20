import sys
sys.path.append('../src/frontend')

import unittest
from preprocessor import *

path_to_C_files = "./C_testing_code/programs/"
path_to_output_files = "./expected_output/preprocessor/"

class PreProcessorTests(unittest.TestCase):

    maxDiff = None

    def test_RemoveComments(self):
        fi = open(path_to_C_files + "comments.c")
        text_input = fi.read()
        fi.close()

        fi = open(path_to_output_files + "comments")
        expected = fi.read()
        fi.close()

        self.assertEqual(remove_comments(text_input), expected)

    def test_FindPreprocessors(self):
        fi = open(path_to_C_files + "comments.c")
        text_input = fi.read()
        fi.close()
        
        fi = open(path_to_output_files + "preProcessor")
        expected = fi.read()
        fi.close()

        self.assertEqual(str(find_preprocessors(text_input)), expected)
        
    def test_GetText(self):

        fi = open(path_to_output_files + "getText")
        expected = fi.read()
        fi.close()

        self.assertEqual(get_text(path_to_C_files + "test.h"), expected)

    def test_Cleanup(self):
        fi = open(path_to_C_files + "comments.c")
        text_input = fi.read()
        fi.close()
        
        fi = open(path_to_output_files + "cleanup")
        expected = fi.read()
        fi.close()

        self.assertEqual(cleanup(text_input), expected)

    def test_RunPreProcessor(self):
        fi = open(path_to_C_files + "simple_preProcessor.c")
        text_input = fi.read()
        fi.close()

        fi = open(path_to_output_files + "simple_preProcessor")
        expected = fi.read()
        fi.close()

        self.assertEqual(run(text_input), expected)

        
