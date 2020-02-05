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
    toc_usr = []
    for idx, heading in enumerate(sections):
        start_point = usr.find("<h3>", heading)
        toc_usr.append((f"#section-{idx}", usr[start_point + len("<h3>"):usr.find("</h3>", start_point)]))
        usr = usr.replace("<h3>", f"<h3 id=\"section-{idx}\">", 1)

    sections = [m.start() for m in re.finditer('<h3>', des)]
    toc_des = []
    for idx, heading in enumerate(sections):
        start_point = des.find("<h3>", heading)
        toc_des.append((f"#section-{idx}", des[start_point + len("<h3>"):des.find("</h3>", start_point)]))
        des = des.replace("<h3>", f"<h3 id=\"section-{idx}\">", 1)

    usr = usr.replace("<th>", "<th style=\"padding: 10px\">")
    usr = usr.replace("<td>&#x2713;</td>", "<td style=\"background: rgb(170, 255, 170); text-align: center;\">&#x2713;</td>")
    usr = usr.replace("<td>&#x2715;</td>", "<td style=\"background: rgb(255, 170, 170); text-align: center;\">&#x2715;</td>")
    usr = usr.replace("<pre>", "<pre style=\"overflow-x:auto;\">")

    des = des.replace("<th>", "<th style=\"padding: 10px\">")
    des = des.replace("<td>&#x2713;</td>", "<td style=\"background: rgb(170, 255, 170); text-align: center;\">&#x2713;</td>")
    des = des.replace("<td>&#x2715;</td>", "<td style=\"background: rgb(255, 170, 170); text-align: center;\">&#x2715;</td>")
    des = des.replace("<pre>", "<pre style=\"overflow-x:auto;\">")

    table_usr = """
<li>
    <h3>
        <a href="#header-usermanual">User Manual</a>
    </h3>
    <ul>
"""
    for section in toc_usr:
        table_usr += f"""
        <li>
            <a href="{section[0]}">{section[1]}</a>
        </li>
"""
    table_usr += """
    </ul>
</li>"""

    table_des = """
<li>
    <h3>
        <a href="#header-design">Design Document</a>
    </h3>
    <ul>
"""
    for section in toc_des:
        table_des += f"""
        <li>
            <a href="{section[0]}">{section[1]}</a>
        </li>
"""
    table_des += """
    </ul>
</li>"""

    page = page.replace("""<header>
<h1 class="title">Namespace <code>src</code></h1>
</header>""", """<header>
<h1 class="title">CSE 423 Compilers</h1>
</header>
<div style="display: flex; flex-wrap: wrap; justify-content: center;">
<span style="flex-grow: 1;"><h5>Alexander Benson</h5></span>
<span style="flex-grow: 1;"><h5>Jacob Garcia</h5></span>
<span style="flex-grow: 1;"><h5>Ole Jeger Hoffstuen</h5></span>
<span style="flex-grow: 1;"><h5>Keaton Jones</h5></span>
</div>""")

    i = page.index("<ul id=\"index\">")
    page = page[:i + len("<ul id=\"index\">")] + table_des + table_usr + page[i + len("<ul id=\"index\">"):]

    i = page.index("<section id=\"section-intro\">")
    page = page[:i + len("<section id=\"section-intro\">")] + des + usr + page[i + len("<section id=\"section-intro\">"):]

    
    index.seek(0)
    index.write(page)

    index.close()
    user.close()
    design.close()

    os.system("mv ../docs/src/* ../docs/")
    os.system("rm -rf ../docs/src")