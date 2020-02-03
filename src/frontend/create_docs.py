"""
Creates pydoc documentation for all files in project
"""

import sys
#sys.path.pop(0)
from mako.template import Template

import os, glob

from os import listdir

import pdoc

def main():
    """
    Main function to make pydocs for all .py files in the project.
    :return: Does not return anything
    """

    #adds current directory to pdoc path
    path = os.getcwd()
    pdoc.import_path.append(path)

    #files to be ignored
    ignore_files = [
                "__init__.py",
                "run.py",
                "makoTest.py"
    ]

    #for every file in the current directory
    for i in listdir("./"):
        if i in ignore_files:
            continue

        if i.endswith(".py"):
            print(i)

            #run pdoc to generate html
            doc = pdoc.Module(pdoc.import_module(i.replace(".py", "")))

            #generate html
            out_html = doc.html()
            
            #get output filename
            out_file = i.replace(".py", ".html")

            #open and write file
            fd = open(out_file, "w+")
            fd.write(out_html)
            fd.close()


    indFile = open("index.html","w")
    mytemplate = Template(filename='sampleTemplate.tmpl')
    links = []
    for file in glob.glob("*.html"):
        if(file != "index.html"):
            links.append(file.replace(".html",""))

    indFile.write(mytemplate.render(ToFill = "SampleName",Sli = links))
    indFile.close()


    #move all .html files to docs location in the github.
    os.system("mv *.html ../../docs")


if __name__ == "__main__":
    main()