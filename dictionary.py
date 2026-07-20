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
regex_on = params.get("regex", [""])[0]
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
# allow regex characters back in after checking code for HTML and XPATH insertion
entry = re.sub(r'[<>:"/\\]', '', entry)

# make it lower case for searches
entry = entry.lower()

#entry = query_string # NO LONGER REQUIRED, SEE ABOVE
#entry = "llann" # FOR TESTING - NO LONGER REQUIRED, SEE ABOVE

# Moved code to functions.py

# Default page language if none specified
if page_lang == "" or not page_lang: page_lang = default_page_lang

# Gets translation keys
get_keys(keys, page_lang)
# Gets values required for interface
defs = get_defs(page_lang)
for key, value in defs:
    #print(key, value)
    globals()[key] = value

'''
# This is a hack because get_keys() isn't getting some of the values from functions.py
# See above for get_defs that returns the lot unless they are arrays (i.e. the keys)
vars = [
  "word_index", 
  "dir", 
  "default_page_lang", 
  "random_word_on", 
  "regex_on", 
  "regex_tickbox"
  ]
for v in vars:
  globals()[v] = get_xml(v, page_lang)
  #print(v+"="+str(globals()[v])+"<br/>")
'''

# Mae sure that the value given as a parameter isn't overwritten, if present
# and restrict possible values, though they are not used in an injectable form
regex_on = params.get("regex", [""])[0]
if regex_on == "True" or regex_on == "1": regex_on = True
else: regex_on = False

# Moved code to functions.py
# Fetch results
#results = check_index(entry, query_lang)
# Check if regex
is_regex = any(c in entry for c in r".^$*+?{}[]\|()")
#print(entry)
#print(entry, is_regex)
try:
    re.compile(entry)
    valid_regex = True
except re.error:
    valid_regex = False
#print(regex_on)
if is_regex and valid_regex and regex_on:
    #print("regex") # FOR TESTING
    # Fetch results via regex
    results = check_index_regex(entry, query_lang)
else:
    # Fetch results normally
    results = check_index(entry, query_lang)

'''
# Check the index
file_ref = ""
if os.path.isfile(word_index):
    try:
        # file exists so show xml
        tree = ET.parse(word_index)
        #tree = ET.parse(word_index, parser=ET.XMLParser(encoding="utf-8"))
        result = tree.xpath(f'//word[search-form="{entry}"]/file-ref/text()')
        index_lang = tree.xpath(f'//word[search-form="{entry}"]/slang/text()')
        index_lang = index_lang[0] if index_lang else ""
        file_ref = result[0] if result else None
        #print(entry) # FOR TESTING: PRINTS the word searched for
        #print(file_ref) # FOR TESTING: Prints the file_ref that it's found in according to the index e.g. {file_ref}.xml
        # FOR TESTING: The three following lines print the index
        #xml = ET.parse(word_index)
        #xml = ET.tostring(xml, pretty_print=True, encoding="unicode")
        #print(xml)
    except (ET.XMLSyntaxError, ET.XSLTApplyError) as e:
        #print(f"Error processing XML/XSLT: {e}")
        print(xslt_error + ": " + e)

#file_path = entry+".xml" # Old way that works directly with entry from query_string as filename
#file_path = str(file_ref)+".xml" # New way that works by checking entry from query_string in index for filename
file_path = dir + "/" + str(file_ref)+".xml" # New way that works by checking entry from query_string in index for filename
#if os.path.exists(file_path):
#if os.path.isfile(file_path):

index_tree = ET.parse(word_index)
index_root = index_tree.getroot()
#matches = index_root.xpath(f'word[word-form="{entry}"]')
#matches = index_root.xpath(f'word[contains(word-form, "{entry}")]')
matches = index_root.xpath(f'word[search-form="{entry}"]')
if not matches:
    matches = index_root.xpath(f'word[contains(search-form, "{entry}")]')
#matches = index_root.xpath(f'word[starts-with(word-form, "{entry}")]')

#matches = list({(m.findtext("word-form"), m.findtext("slang"), m.findtext("file-ref")): m for m in matches}.values())
#matches = list({m.findtext("file-ref"): m for m in matches}.values())
#matches = list(dict.fromkeys(matches))

#FOR TESTING
#for m in matches:
#    print(ET.tostring(m, encoding="unicode")+" : ")

results = []

for w in matches:
    if w.findtext("slang") == query_lang:
        #results.append(w.findtext("file-ref"))
        #if file_ref not in results:
        if w.findtext("word-form") not in results:
            results.append(w.findtext("word-form")+":"+w.findtext("search-form")+":"+w.findtext("file-ref"))
        results = sorted(results)

    #file_ref = w.findtext("file-ref")
    #file_path = dir + "/" + file_ref + ".xml"

    #if os.path.isfile(file_path):
    #    tree = ET.parse(file_path)
    #    root = tree.getroot()

    #    for x in root.xpath("//word"):
    #    #for x in root.xpath(f'word[word-form="{entry}"]'):
    #        results.append((
    #            x.findtext("word-form"),
    #            x.findtext("slang")
    #        ))
'''

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

#print(len(results))
#print(results)

if len(results) == 1:
    word_form = results[0].split(':')[0]
    search_form = results[0].split(':')[1]
    file_ref = results[0].split(':')[2]
    file_path = dir + "/" + file_ref + ".xml"
    #file_path = get_xml("dir", page_lang) + "/" + file_ref + ".xml" # not now necessary

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
            res = res.replace("<body>", "<body>\n    " + input_form(regex_on))
            res = res.replace("<html>", "<html lang=\"" + page_lang + "\">")
            res = res.replace('<table border="1"/>', "<p>" + no_data + "</p>")
            res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

            # This line superscripts digits
            res = re.sub(r'(<td>[^<]*?)(\d)', r'\1<sup>\2</sup>', res)

            res = transform_regex_lebels(res, query_lang, search_lang, regex_on)
            '''if regex_on:
              if query_lang == search_lang:
                print("search")
                res = res.replace("{search_regex_checked}", "checked")
                res = res.replace(" {data_regex_checked}", "")
              elif query_lang == data_lang:
                print("data")
                res = res.replace(" {search_regex_checked}", "")
                res = res.replace("{data_regex_checked}", "checked")
            else:
              res = res.replace(" {search_regex_checked}", "")
              res = res.replace(" {data_regex_checked}", "")'''

            # Translate to interface language
            res = transform_html(res, page_lang)

            print(res)

        except (ET.XMLSyntaxError, ET.XSLTApplyError) as e:
            #print(f"Error processing XML/XSLT: {e}")
            print(xslt_error + ": " + e)

elif len(results) > 15:
    res = get_res(entry, query_lang, regex_on)
    '''
    res = "<!DOCTYPE HTML>\n<html lang=\"" + page_lang + "\">\n  <body>\n"
    res += input_form()

    if query_lang == search_lang:
        #res += "\n    <b>Results for " +  search_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b><br/><br/>"
        res = res.replace("{results_lang_name}", search_lang_name)
    if query_lang == data_lang:
        #res += "\n    <b>Results for " + data_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b><br/><br/>"
        res = res.replace("{results_lang_name}", data_lang_name)

    #res += "\n    <ul>"
    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    '''

    # Deduplicate any results found [MOVED UP]
    #results = list({item.split(':')[0]: item for item in results}.values())
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
    res = get_res(entry, query_lang, regex_on)
    '''
    res = "<!DOCTYPE HTML>\n<html lang=\"" + page_lang + "\">\n  <body>\n"
    res += input_form()

    if query_lang == search_lang:
        print(search_lang_name)
        #res += "\n    <b>Results for " +  search_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        res = res.replace("{results_lang_name}", search_lang_name)
    if query_lang == data_lang:
        #res += "\n    <b>Results for " + data_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        res = res.replace("{results_lang_name}", data_lang_name)

    res += "\n    <ul>"
    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    '''

    # Deduplicate any results found [MOVED UP]
    #results = list({item.split(':')[0]: item for item in results}.values())
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
    res = res_no_results(entry, page_lang, regex_on)
    '''
    res = "<!DOCTYPE HTML>\n<html lang=\"" + query_lang + "\">\n  <body>\n  </body>\n</html>"

    if entry:
        res = res.replace("<body>", "<body>\n    " + input_form() + "\n    <p>" + not_found + "</p>")
    else:
        res = res.replace("<body>", "<body>\n    " + input_form())

        # Print a random word from the data language
        if 'random_word_on' in globals() and random_word_on:
          random_word = random_word(data_lang)
          random_word = '<a href="/?q=' + random_word + '&sl=' + data_lang + '&lang=' + page_lang + '">' + random_word + '</a>'
          res = res.replace("</body>", "  " + random_word + "\n</body>")

    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    '''

    # Translate to interface language
    res = transform_html(res, page_lang)

    print(res)
