"""
This module is only supposed to generate the documentation for the compiler as a whole including User Manual. 
"""

import os

if __name__ == "__main__":
    os.system("pdoc --html -o ../docs ../src --force")

    index = open("../docs/src/index.html", 'r+')
    user = open("User Manual.html", "r")

    page = index.read()
    usr = user.read()

    i = page.index("<section id=\"section-intro\">")
    page = page[:i + len("<section id=\"section-intro\">")] + usr + page[i + len("<section id=\"section-intro\">"):]
    index.seek(0)
    index.write(page)

    index.close()
    user.close()