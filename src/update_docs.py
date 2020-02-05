"""
This module is only supposed to generate the documentation for the compiler as a whole including User Manual. 
"""

import os

if __name__ == "__main__":
    os.system("rm -rf ../docs/*")
    os.system("pdoc --html -o ../docs ../src")

    index = open("../docs/src/index.html", 'r+')
    user = open("User Manual.html", "r")

    page = index.read()
    usr = user.read()

    i = page.index("<section id=\"section-intro\">")
    page = page[:i + len("<section id=\"section-intro\">")] + usr + page[i + len("<section id=\"section-intro\">"):]

    page = page.replace("<th>", "<th style=\"padding: 10px\">")
    page = page.replace("<td>&#x2713;</td>", "<td style=\"background: rgb(170, 255, 170); text-align: center;\">&#x2713;</td>")
    page = page.replace("<td>&#x2715;</td>", "<td style=\"background: rgb(255, 170, 170); text-align: center;\">&#x2715;</td>")
    
    index.seek(0)
    index.write(page)

    index.close()
    user.close()

    os.system("mv ../docs/src/* ../docs/")
    os.system("rm -rf ../docs/src")