import os
import re

def remove_comments(text):
    """
    Removes comments from the given text

    Args:
        text: The string representation of C code.
    
    Returns:
        The text with all C comments removed.
    """

    # Regex that will capture both '//' and '/* */' style comments
    regex = r"/(\*(\w|\W)*?\*/|/([^\n]*))"
    
    return re.sub(regex, '', text)



def find_preprocessors(text):
    """
    Finds all preprocessor keywords from the given text.

    Args:
        text: The string representation of C code.
    
    Returns:
        List of the found preprocessor keywords and their corresponding values.
    """

    regex = r"#\s*(warning|else|endif|include|undef|ifdef|ifndef|if|elif|pragma|define|if|elif|error|pragma|line)([\t\f ]+[^\s]+)([\t\f ]+[^\s]+)*"
    li = re.findall(regex, text)
    return li



def get_text(file_name, path):
    """
    Opens and retrieves the text from an import file and preprocesses this text.

    Args:
        file_name: The import file name.
    
    Returns:
        Text of the import file.
    """
    fi = open(path + "/" + file_name, "r")
    text = fi.read()
    fi.close()

    # Run preprocessing on imported file
    text = run(text, path)

    return text



def cleanup(text):
    """
    Cleans up C code text by removing pre-processing lines.

    Args:
        text: text format of C code to be cleaned up.
    
    Returns:
        New text of the C code after cleanup.
    """

    new_text = ""

    for line in text.splitlines():
        if not line.startswith('#'):
            new_text += line + "\n"

    return new_text



def run(text, path):
    """
    Performs pre-processing on C code text.

    Args:
        text: text format of C code to be pre-processed.
    
    Returns:
        Text of the C code after pre-processing.
    """

    # Remove comments from text
    text = remove_comments(text)

    # Find all preprocessor elements (if any)
    # NOTE: Currrently the list is sorted so the '#define' statements are 
    #       first on the list. This prevents the manipulation of the imported C code.
    proc_list = sorted(find_preprocessors(text), key = lambda x: x[0])


    for pre_proc in proc_list:
        # Determine which are 'includes', 'defines', etc..

        if pre_proc[0] == "define":

            try:

                variable = pre_proc[1].replace(" ", "") #strip whitespace
                value = pre_proc[2].replace(" ", "")

                # Delete the pre-processor instruction from the C code
                text = re.sub(rf"\s*#define {variable} {value}", "", text)

                # Replace occurences of VARIABLE with VALUE in C code
                text = re.sub(rf"{variable}", value, text)

            except Exception:
                raise BaseException("Invalid '#define' statement")

        if pre_proc[0] == "include":

            # Try to match to standard library import (i.e. <xyz.h>)
            file_name = ["".join(x) for x in re.findall('<([^"]*)>', pre_proc[1])]
            if file_name:
                # TODO: add capability to search for standard libraries

                # Delete the pre-processor instruction from the C code
                text = re.sub(rf'\s*#include <{file_name[0]}>\n', "", text)
                #text = get_text(PATH_TO_STD_LIBRARIES) + text
                continue
            
            # Try to match to local library import (i.e. "xyz.h", 'xyz.h')
            file_name = ["".join(x) for x in re.findall('["]([^"]*)["]|[\']([^"]*)[\']', pre_proc[1])]
            if file_name:

                # Delete the pre-processor instruction from the C code
                text = re.sub(rf'\s*#include \"{file_name[0]}\"\n', "", text)
                text = get_text(file_name[0], os.path.abspath(os.path.dirname(path))) + text

            else:
                raise BaseException("Invalid '#include' statement")



    # We are continuing to impliment more "supplimental" pre-processor features, but cleanup for now.
    text = cleanup(text)

    return text


def main():
    fi = open("./test_files/test.c", "r")
    text = fi.read()
    fi.close()
    text = run(text)

    print(text)

if __name__ == "__main__":
    main()