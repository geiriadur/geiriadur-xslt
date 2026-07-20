import lxml.etree as ET
from urllib.parse import parse_qs
import os
import sys
import re
from unicodedata import normalize

# Moved code to globals.py
#from globals import *
# Moved code to functions.py
from functions import *

# CODE FOLLOWS

#query_string = os.environ.get("QUERY_STRING", "") # only from browser
query_string = os.environ.get("QUERY_STRING") or (sys.argv[1] if len(sys.argv) > 1 else "") # from browser or command line

# Required if we decide to parse the query string
#print(query_string)
params = parse_qs(query_string)
#print(params)
entry = params.get("q", [""])[0]
query_lang = params.get("sl", [""])[0]
page_lang = params.get("lang", [""])[0]
#print("Content-Type: text/plain\n")
#print(f"Entry: {entry}")
#print(f"  Lang: {page_lang}")

# remove unsafe characters, allow only letters, numbers, dash, underscore
#entry = re.sub(r'[^a-zA-Z0-9_-]', '', query_string)
#entry = re.sub(r'[^a-zA-Z0-9_-]', '', entry)
# normalise to make it safe
#entry = normalize("NFC", query_string)
entry = normalize("NFC", entry)
# remove unsafe characters, allow only letters, numbers, dash, underscore and unicode
entry = re.sub(r'[<>:"/\\|?*]', '', entry)

# make it lower case for searches
entry = entry.lower()

#entry = query_string # NO LONGER REQUIRED, SEE ABOVE
#entry = "llann" # FOR TESTING - NO LONGER REQUIRED, SEE ABOVE

# Moved code to functions.py

# Default page language if none specified
if page_lang == "" or not page_lang: page_lang = default_page_lang

# Gets values required for interface including translations
get_keys(keys, page_lang)

# Moved code to functions.py
# Fetch results
results = check_index(entry, query_lang)

# Deduplicate in the case that all the results point to the same word
if len({r.split(':')[1] for r in results}) == 1:
    # Deduplicate any results found
    results = list({item.split(':')[1]: item for item in results}.values())
    #seen = set()
    #results = [
    #    r for r in results
    #    if not (r.split(':')[1] in seen or seen.add(r.split(':')[1]))
    #]

if len(results) == 1:
    word_form = results[0].split(':')[0]
    search_form = results[0].split(':')[1]
    file_ref = results[0].split(':')[2]
    file_path = dir + "/" + file_ref + ".xml"

    if os.path.isfile(file_path):
        try:
            html = ET.parse(file_path)

            root = html.getroot()
            target = word_form

            for entry in root.findall('entry'):
                #if entry.findtext('./meta/headword-ref') != target:
                if target not in entry.findtext('./meta/headword-ref', ''):
                #if target not in entry.findtext('//', ''):
                    root.remove(entry)

            xslt = ET.parse("entry.xsl")
            transform = ET.XSLT(xslt)
            res = transform(html)
            res = ET.tostring(res, pretty_print=True, encoding="unicode")
            res = "<!DOCTYPE HTML>\n" + res
            res = res.replace("<body>", "<body>\n    " + input_form())
            res = res.replace("<html>", "<html lang=\"" + page_lang + "\">")
            res = res.replace('<table border="1"/>', "<p>" + no_data + "</p>")
            res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

            # This line superscripts digits
            res = re.sub(r'(<td>[^<]*?)(\d)', r'\1<sup>\2</sup>', res)

            # Translate to interface language
            res = transform_html(res, page_lang)

            print(res)

        except (ET.XMLSyntaxError, ET.XSLTApplyError) as e:
            #print(f"Error processing XML/XSLT: {e}")
            print(xslt_error + ": " + e)

elif len(results) > 15:
    res = get_res(entry, query_lang)

    # Deduplicate any results found
    results = list({item.split(':')[0]: item for item in results}.values())
    #seen = set()
    #results = [
    #    r for r in results
    #    if not (r.split(':')[0] in seen or seen.add(r.split(':')[0]))
    #]

    for r in results:
        #res += "<li>" + r + "</li>"
        #res += '\n        <li><a href="/?q=' + r + '&sl=' + data_lang + '">' + r + '</a></li>'
        r = r.split(':')[0]
        #res += '\n        <a href="/?q=' + r + '&sl=' + data_lang + '">' + r + '</a>&nbsp;'
        res += '\n        <a href="/?q=' + r + '&sl=' + data_lang + '&lang='+ page_lang + '">' + r + '</a>&nbsp;'
    res += "\n  </body>\n</html>"

    # Translate to interface language
    res = transform_html(res, page_lang)

    print(res)

elif len(results) > 1:
    res = get_res(entry, query_lang)

    # Deduplicate any results found
    results = list({item.split(':')[0]: item for item in results}.values())
    #seen = set()
    #results = [
    #    r for r in results
    #    if not (r.split(':')[0] in seen or seen.add(r.split(':')[0]))
    #]

    for r in results:
        #res += "<li>" + r + "</li>"
        r = r.split(':')[0]
        #res += '\n        <li><a href="/?q=' + r + '&sl=' + data_lang + '">' + r + '</a></li>'
        res += '\n        <li><a href="/?q=' + r + '&sl=' + data_lang + '&lang='+ page_lang + '">' + r + '</a></li>'
    res += "\n    </ul>\n  </body>\n</html>"

    # Translate to interface language
    res = transform_html(res, page_lang)

    print(res)


else:
    res = res_no_results(entry, page_lang)

    # Translate to interface language
    res = transform_html(res, page_lang)

    print(res)
