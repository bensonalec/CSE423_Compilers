"""
Creates pydoc documentation for all files in project
"""

import os

from os import listdir

import pydoc

def main():
    """
    Main function to make pydocs for all .py files in the project.
    :return: Does not return anything
    """

    #need to check for python files in src and then write html pages in ./docs

    #files to be ignored
    ignore_files = [
                "__init__.py",
                "run.py"       
    ]


    for i in listdir("./"):
        if i in ignore_files:
            continue

        if i.endswith(".py"):
            print(i)
            os.system("python3 -m pydoc -w " + i.replace(".py", ""))

    os.system("mv *.html ../../docs")


if __name__ == "__main__":
    main()