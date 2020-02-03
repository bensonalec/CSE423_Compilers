"""
Creates pydoc documentation for all files in project
"""

import sys
sys.path.pop(0)
from mako.template import Template

import os, glob

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
                "run.py",
                "makoTest.py"
    ]


    for i in listdir("./"):
        if i in ignore_files:
            continue

        if i.endswith(".py"):
            print(i)
            os.system("python3 -m pydoc -w " + i.replace(".py", ""))

    indFile = open("index.html","w")
    mytemplate = Template(filename='sampleTemplate.tmpl')
    links = []
    for file in glob.glob("*.html"):
        links.append(file.replace(".html",""))

    indFile.write(mytemplate.render(ToFill = "SampleName",Sli = links))
    indFile.close()

    os.system("mv *.html ../../docs")


if __name__ == "__main__":
    main()