"""
This module is only supposed to generate the documentation for the compiler as a whole including User Manual. 
"""

import os
import re

if __name__ == "__main__":
    os.system("rm -rf ../docs/*")
    os.system("pdoc --html -o ../docs ../src")

    index = open("../docs/src/index.html", 'r+')
    user = open("User Manual.html", "r")
    design = open("design_doc.html", "r")

    page = index.read()
    usr = user.read()
    des = design.read()

    sections = [m.start() for m in re.finditer('<h3>', usr)]
    toc = []
    for idx, heading in enumerate(sections):
        start_point = usr.find("<h3>", heading)
        toc.append((f"#section-{idx}", usr[start_point + len("<h3>"):usr.find("</h3>", start_point)]))
        usr = usr.replace("<h3>", f"<h3 id=\"section-{idx}\">", 1)

    usr = usr.replace("<th>", "<th style=\"padding: 10px\">")
    usr = usr.replace("<td>&#x2713;</td>", "<td style=\"background: rgb(170, 255, 170); text-align: center;\">&#x2713;</td>")
    usr = usr.replace("<td>&#x2715;</td>", "<td style=\"background: rgb(255, 170, 170); text-align: center;\">&#x2715;</td>")
    usr = usr.replace("<pre>", "<pre style=\"overflow-x:auto;\">")

    table = """
<li>
    <h3>
        <a href="#header-usermanual">User Manual</a>
    </h3>
    <ul>
"""
    for section in toc:
        table += f"""
        <li>
            <a href="{section[0]}">{section[1]}</a>
        </li>
"""
    table += """
    </ul>
</li>"""

    i = page.index("<ul id=\"index\">")
    page = page[:i + len("<ul id=\"index\">")] + table + page[i + len("<ul id=\"index\">"):]

    i = page.index("<section id=\"section-intro\">")
    page = page[:i + len("<section id=\"section-intro\">")] + des + usr + page[i + len("<section id=\"section-intro\">"):]

    
    index.seek(0)
    index.write(page)

    index.close()
    user.close()
    design.close()

    os.system("mv ../docs/src/* ../docs/")
    os.system("rm -rf ../docs/src")