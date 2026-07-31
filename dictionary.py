
import lxml.etree as ET
from urllib.parse import parse_qs
import os
import sys
import re
from unicodedata import normalize

# Import functions from other .py
#from globals import *
from functions import *

# CODE FOLLOWS

#query_string = os.environ.get("QUERY_STRING", "") # only from browser
query_string = os.environ.get("QUERY_STRING") or (sys.argv[1] if len(sys.argv) > 1 else "") # from browser or command line

# Required to parse the query string
params = parse_qs(query_string)
entry = params.get("q", [""])[0]
query_lang = params.get("sl", [""])[0]
page_lang = params.get("lang", [""])[0]

# normalise to make it safe
entry = normalize("NFC", entry)
# remove unsafe characters, allow only letters, numbers, dash, underscore and unicode
#entry = re.sub(r'[<>:"/\\|?*]', '', entry)
# allow regex characters back in (with checking code for HTML and XPATH insertion below)
entry = re.sub(r'[<>:"/\\]', '', entry)

# make it lower case for searches
entry = entry.lower()

# Default page language if none specified
if page_lang == "" or not page_lang: page_lang = default_page_lang

# Gets translation keys
get_keys(keys, page_lang)
# Gets values required for interface
defs = get_defs(page_lang)
for key, value in defs:
    globals()[key] = value

# Mae sure that the value given as a parameter isn't overwritten, if present
# and restrict possible values, though they are not used in an injectable form
regex_on = params.get("regex", [""])[0]
if regex_on == "True" or regex_on == "1": regex_on = True
else: regex_on = False

xslt_setting = xslt_default # Default setting
# Mae sure that the value given as a parameter isn't overwritten, if present
# and restrict possible values, though they are not used in an injectable form
xslt_param = params.get("x", [""])[0]
if xslt_alt_enabled:
    if xslt_param: xslt_alt_on = xslt_param # Check parameter is enabled before setting
    if xslt_alt_on == "True" or xslt_alt_on == "1": xslt_alt_on = True # For the user parameter
    else: xslt_alt_on = False # Disable any other values 
    if xslt_alt_on: xslt_setting = xslt_alt
    else: xslt_setting = xslt_default
else:
    xslt_setting = xslt_default

# Check if regex
is_regex = any(c in entry for c in r".^$*+?{}[]\|()")
try:
    re.compile(entry)
    valid_regex = True
except re.error:
    valid_regex = False
if is_regex and valid_regex and regex_on:
    # Fetch results via regex
    results = check_index_regex(entry, query_lang)
else:
    # Fetch results normally
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

# Deduplicate any results found
results = list({item.split(':')[0]: item for item in results}.values())
#seen = set()
#results = [
#    r for r in results
#    if not (r.split(':')[0] in seen or seen.add(r.split(':')[0]))
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

            #for entry in root.findall('entry'):
            #    if target not in entry.findtext('./meta/headword-ref', ''):
            #        root.remove(entry)

            for tag in entry_tags:
                #for entry in root.findall(tag): # If tag is in root
                for entry in root.xpath(f'.//{tag}'): # If tag is nested
                    headwords = [h.text.strip() for tag in word_form_tags for h in entry.xpath(f'.//{tag}') if h.text]

                    #if target not in headwords:
                    #    root.remove(entry)

                    if target not in headwords:
                        parent = entry.getparent()
                        if parent is not None:
                            parent.remove(entry)

            xslt = ET.parse(xslt_setting)
            transform = ET.XSLT(xslt)
            #print(ET.tostring(root, encoding="unicode")) ## FOR TESTING XSLT
            res = transform(html)
            res = ET.tostring(res, pretty_print=True, encoding="unicode")
            res = "<!DOCTYPE HTML>\n" + res
            res = res.replace("<body>", "<body>\n    " + input_form(query_string, query_lang, page_lang, regex_on))
            res = res.replace("<html>", "<html lang=\"" + page_lang + "\">")
            #res = res.replace('<table border="1"/>', "<p>" + no_data + "</p>")
            res = res.replace('<table border="1"/>', "<p>" + globals()[page_lang]['no_data'] + "</p>") # in the correct language
            res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

            # This line superscripts digits
            res = re.sub(r'(<td>[^<]*?)(\d)', r'\1<sup>\2</sup>', res)

            res = transform_regex_labels(res, query_lang, regex_on, xslt_alt_on)

            # Translate to interface language
            res = transform_html(res, page_lang)

            print(res)

        except (ET.XMLSyntaxError, ET.XSLTApplyError) as e:
            #print(f"Error processing XML/XSLT: {e}")
            #print(xslt_error + ": " + e)
            print(globals()[page_lang]['xslt_error'] + ": " + e) # in the correct language

elif len(results) > 15:
    res = get_res(entry, query_string, query_lang, page_lang, regex_on, xslt_alt_on)

    for r in results:
        r = r.split(':')[0]
        res_add = '\n        <a href="/?q=' + r + '&sl=' + data_lang + '&lang='+ page_lang + '">' + r + '</a>&nbsp;'
        res_add = res_add.replace('">', '&regex='+str(int(regex_on))+'&x='+str(int(xslt_alt_on))+'">')
        res += res_add


    res += "\n  </body>\n</html>"

    # Translate to interface language
    res = transform_html(res, page_lang)

    print(res)

elif len(results) > 1:
    res = get_res(entry, query_string, query_lang, page_lang, regex_on, xslt_alt_on)

    for r in results:
        r = r.split(':')[0]
        res_add = '\n        <li><a href="/?q=' + r + '&sl=' + data_lang + '&lang='+ page_lang + '">' + r + '</a></li>'
        res_add = res_add.replace('">', '&regex='+str(int(regex_on))+'&x='+str(int(xslt_alt_on))+'">')
        res += res_add
    res += "\n    </ul>\n  </body>\n</html>"

    # Translate to interface language
    res = transform_html(res, page_lang)

    print(res)


else:
    res = res_no_results(entry, query_string, query_lang, page_lang, regex_on, xslt_alt_on)

    # Translate to interface language
    res = transform_html(res, page_lang)

    print(res)
