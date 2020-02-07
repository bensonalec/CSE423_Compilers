"""
This module is only supposed to generate the documentation for the compiler as a whole including User Manual. 
"""

import os
import re
import itertools

import bs4

if __name__ == "__main__":
    # Setus up /docs for the newly generated documentation.
    os.system("rm -rf ../docs/*")
    os.system("pdoc --html -o ../docs ../src")

    # Opens the necessary files to modify
    index = open("../docs/src/index.html", 'r+')
    user = open("User Manual.html", "r")
    design = open("design_doc.html", "r")

    # Reads the content if each file
    page_parser = bs4.BeautifulSoup(index.read(), "html.parser")
    usr_parser = bs4.BeautifulSoup(user.read(), "html.parser")
    des_parser = bs4.BeautifulSoup(design.read(), "html.parser")

    # Adds some inline styling to certain tags located within the design document.
    for th in itertools.chain(des_parser.select("th"), usr_parser.select("th")):
        style = "padding: 10px;"
        if 'style' in th:
            th['style'] += style
        else:
            th['style'] = style

    for td in itertools.chain(des_parser.select("td"), usr_parser.select("td")):
        b = True
        style = "text-align: center; "
        if td.string == "✓":
            style += "background: rgb(170, 255, 170);"
        elif td.string == "✕":
            style += "background: rgb(255, 170, 170);"

        else:
            b = False

        if b:
            if 'style' in td:
                td['style'] += style
            else:
                td['style'] = style

    for pre in itertools.chain(des_parser.select("pre"), usr_parser.select("pre")):
        style = "overflow-x: auto;"
        if 'style' in pre:
            pre['style'] += style
        else:
            pre['style'] = style

    # Assigns IDs for the table of contents
    sections = []
    idx = -1

    for idx, dd in enumerate(des_parser.select("h2"), idx + 1):
        dd['id'] = f"section_{idx}" if 'id' not in dd else dd['id']
        sections.append(dd)
        
    for idx, h3 in enumerate(des_parser.select("h3"), idx + 1):
        h3['id'] = f"section_{idx}" if 'id' not in h3 else h3['id']
        sections.append(h3)

    for idx, um in enumerate(usr_parser.select("h2"), idx + 1):
        um['id'] = f"section_{idx}" if 'id' not in um else um['id']
        sections.append(um)
        
    for idx, h3 in enumerate(usr_parser.select("h3"), idx + 1):
        h3['id'] = f"section_{idx}" if 'id' not in h3 else h3['id']
        sections.append(h3)

    # Generates and inserts the table of contents into the website
    for ul in page_parser.select(".toc ul"):
        for section in sections[::-1]:
            tag = page_parser.new_tag("li")
            tag.string = section.string
            tag.string.wrap(page_parser.new_tag("a", href=f"#{section['id']}"))
            tag.a.string.wrap(page_parser.new_tag(f"h{int(section.name[1])+1}"))
            ul.insert(0, tag)

    # Adjusts the title of the page
    header = page_parser.find("header")
    for child in header.children:
        child.string = "CSE 423 Compilers"

    # Generates and replaces the header of the document.
    names = page_parser.new_tag("div", style="display: flex; flex-wrap: wrap; justify-content: center;")

    span_a = page_parser.new_tag("span", style="flex-grow: 1;")
    span_j = page_parser.new_tag("span", style="flex-grow: 1;")
    span_o = page_parser.new_tag("span", style="flex-grow: 1;")
    span_k = page_parser.new_tag("span", style="flex-grow: 1;")

    span_a.string = "Alexander Benson"
    span_j.string = "Jacob Garcia"
    span_o.string = "Ole Jeger Hoffstuen"
    span_k.string = "Keaton Jones"

    span_a.string.wrap(page_parser.new_tag("h5"))
    span_j.string.wrap(page_parser.new_tag("h5"))
    span_o.string.wrap(page_parser.new_tag("h5"))
    span_k.string.wrap(page_parser.new_tag("h5"))

    names.append(span_a)
    names.append(span_j)
    names.append(span_o)
    names.append(span_k)

    header.insert_after(names)

    # Add inline javascript to allow for management of examples
    for i, (link, rep) in enumerate(zip(usr_parser.select(".example_buttons"), usr_parser.select(".example_representations"))):
        for j, (a, div) in enumerate(zip(link.children, rep.children)):
            if type(a) != type(bs4.NavigableString("")) or type(div) != type(bs4.NavigableString("")):
                a["onclick"] = f"""[...document.getElementsByClassName("representation_{i}")].forEach(function(elem, index) {{ if (index === {(j-1)/2}) {{ elem.style.display = "block";}} else {{ elem.style.display = "none";}}}})"""
                div['class'] = f"representation_{i}" if 'class' not in div else div['class']
                div['style'] = "display: none;" if 'style' not in div else div['style']
            rep.div['style'] = "display: block;"

    content = page_parser.find("section")
    content.append(des_parser)
    content.append(usr_parser)

    # Writes content to the file
    index.seek(0)
    index.write(page_parser.prettify())

    # Closes the files as they aren't needed anymore
    index.close()
    user.close()
    design.close()

    # Ensures consistent folder structure with what is expected by github.
    os.system("mv ../docs/src/* ../docs/")
    os.system("rm -rf ../docs/src")
    os.system("cp ./architecture.png ../docs/architecture.png")