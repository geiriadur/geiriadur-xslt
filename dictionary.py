# GLOBALS
#
# CONSTANTS

keys = "keys.yaml" # This is critical to finding the YAML values
word_index = "word_index.xml"
dir = "xml"
default_page_lang = "en"

# VARIABLES (ENGLISH DEFAULTS - CHANGE IN YAML FILE NOT HERE)

not_found = "Not found in dictionary. Please search again."
no_data = "No data or malformed entry. Please consult your lexicographer."
xslt_error = "Error processing XML/XSLT"
lang_results_msg = "Results for {results_lang_name} search"
search_lang = "en"
search_lang_name = "English"
data_lang = "cy"
data_lang_name = "Welsh"
search_button_name = "Search"
page_title = "Welsh Dictionary"
page_lang = "en"

index_lang = ""

# CODE FOLLOWS

import lxml.etree as ET
from urllib.parse import parse_qs
import os
import sys
import re
from unicodedata import normalize

def transform_html(html):

    html = html.replace("{search_lang_name}", search_lang_name)
    html = html.replace("{data_lang_name}", data_lang_name)
    html = html.replace("{search_lang}", search_lang)
    html = html.replace("{data_lang}", data_lang)
    html = html.replace("{search_button_name}", search_button_name)
    html = html.replace("{page_title}", page_title)
    html = html.replace("{language}", page_lang)

    # Translation keys
    #print(tkeys)
    if 'tkeys' in globals():
      for key, value in tkeys.items():
        #print(key+"==="+value)
        html = html.replace(key, value)
        #globals()[key] = value

    return html

def input_form():
    html = '''<p>
      <form id="myForm\" action="/" method="get">
        {search_lang_name}: <input type="text" id="myInput" name="q">
        <input type="hidden" name="sl" value="{search_lang}">
        <input type="hidden" name="lang" value="{language}">
        <input type="submit" value="{search_button_name}">
      </form>
    </p>
    <p>
      <form id="myForm2" action="/" method="get">
        {data_lang_name}: <input type="text" id="myInput2" name="q">
        <input type="hidden" name="sl" value="{data_lang}">
        <input type="hidden" name="lang" value="{language}">
        <input type="submit" value="{search_button_name}">
      </form>
    </p>
    <!--script>
      document.getElementById("myForm").addEventListener("submit", function(e) {
      e.preventDefault();
      const val = document.getElementById("myInput").value;
      const query_lang = document.getElementById("slang").value;
      window.location = "/?" + encodeURIComponent(val);
      });
    </script-->'''
    #html = html.replace("{search_lang_name}", search_lang_name)
    #html = html.replace("{data_lang_name}", data_lang_name)
    #html = html.replace("{search_lang}", search_lang)
    #html = html.replace("{data_lang}", data_lang)
    #html = html.replace("{search_button_name}", search_button_name)
    return(html)

def head():
    head = '''  <title>{page_title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="title" property="og:title" content="{page_title}">
    <meta name="Keywords" content="keywords">
    <meta name="Description" content="{page_title}">
    <meta property="og:description" content="{page_title}">
    <link rel="stylesheet" href="style.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">'''
    #head = head.replace("{page_title}", page_title)
    return(head)

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

###
import yaml

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

stream = open(keys, 'r')
dictionary = yaml.load(stream, Loader=yaml.SafeLoader) #safe
#dictionary = yaml.load(stream) # unsafe

word_index = dictionary.get("word_index")
dir = dictionary.get("dir")
default_page_lang = dictionary.get("default_page_lang")

if page_lang == "" or not page_lang: page_lang = default_page_lang

#missing = [v for v in ["word_index", "dir", "default_page_lang"] if v not in globals()]
#for m in missing:
  #print("Variable \""+ m + "\" is missing in key file.")

#present = [v for v in ["word_index", "dir", "default_page_lang"] if v in globals()]
#for p in present:
  #print("Variable \""+ p + "\" is present in key file.")
  #print(p + " == " + globals()[p])
#print("\n")

value = dictionary.get(page_lang, dictionary["en"])
#lang = next(k for k, v in dictionary.items() if v is value)

for key, value in value.items():
  globals()[key] = value

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

index_tree = ET.parse("word_index.xml")
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
            res = transform_html(res)

            print(res)

        except (ET.XMLSyntaxError, ET.XSLTApplyError) as e:
            #print(f"Error processing XML/XSLT: {e}")
            print(xslt_error + ": " + e)

elif len(results) > 15:
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
    res = transform_html(res)

    print(res)

elif len(results) > 1:
    res = "<!DOCTYPE HTML>\n<html lang=\"" + page_lang + "\">\n  <body>\n"
    res += input_form()

    if query_lang == search_lang:
        #res += "\n    <b>Results for " +  search_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        res = res.replace("{results_lang_name}", search_lang_name)
    if query_lang == data_lang:
        #res += "\n    <b>Results for " + data_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        res = res.replace("{results_lang_name}", data_lang_name)

    res += "\n    <ul>"
    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

    #print(results)

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
    res = transform_html(res)

    print(res)


else:
    res = "<!DOCTYPE HTML>\n<html lang=\"" + query_lang + "\">\n  <body>\n  </body>\n</html>"

    if entry:
        res = res.replace("<body>", "<body>\n    " + input_form() + "\n    <p>" + not_found + "</p>")
    else:
        res = res.replace("<body>", "<body>\n    " + input_form())

    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

    # Translate to interface language
    res = transform_html(res)

    print(res)
