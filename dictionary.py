# CONSTANTS

not_found = "Not found in dictionary. Please search again."
no_data = "No data or malformed entry. Please consult your lexicographer."
xslt_error = "Error processing XML/XSLT"
lang_results_msg = "Results for {search_lang_name} search"
search_lang = "en"
search_lang_name = "English"
data_lang = "cel-x-brit"
data_lang_name = "Brittonic"
search_button_name = "Search"
page_title = "Brittonic Dictionary"
page_lang = "en"

word_index = "word_index.xml"
dir = "xml"

# CODE FOLLOWS

index_lang = ""

import lxml.etree as ET
from urllib.parse import parse_qs
import os
import sys
import re
from unicodedata import normalize

def input_form():
    html = """<p>
      <form id=\"myForm\" action=\"/\" method=\"get\">
        {search_lang_name}: <input type=\"text\" id=\"myInput\" name=\"q\">
        <input type=\"hidden\" name=\"lang\" value=\"{search_lang}\">
        <input type=\"submit\" value=\"{search_button_name}\">
      </form>
    </p>
    <p>
      <form id=\"myForm2\" action=\"/\" method=\"get\">
        {data_lang_name}: <input type=\"text\" id=\"myInput2\" name=\"q\">
        <input type=\"hidden\" name=\"lang\" value=\"{data_lang}\">
        <input type=\"submit\" value=\"{search_button_name}\">
      </form>
    </p>
    <!--script>
      document.getElementById(\"myForm\").addEventListener(\"submit\", function(e) {
      e.preventDefault();
      const val = document.getElementById(\"myInput\").value;
      const lang = document.getElementById(\"lang\").value;
      window.location = \"/?\" + encodeURIComponent(val);
      });
    </script-->"""
    html = html.replace("{search_lang_name}", search_lang_name)
    html = html.replace("{data_lang_name}", data_lang_name)
    html = html.replace("{search_lang}", search_lang)
    html = html.replace("{data_lang}", data_lang)
    html = html.replace("{search_button_name}", search_button_name)
    return(html)
    
def head():
    head = """  <title>{page_title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="title" property="og:title" content="{page_title}">
    <meta name="Keywords" content="keywords">
    <meta name="Description" content="{page_title}">
    <meta property="og:description" content="{page_title}">
    <link rel="stylesheet" href="style.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">"""
    head = head.replace("{page_title}", page_title)
    return(head)

#query_string = os.environ.get("QUERY_STRING", "") # only from browser
query_string = os.environ.get("QUERY_STRING") or (sys.argv[1] if len(sys.argv) > 1 else "") # from browser or command line
    
# Required if we decide to parse the query string
#print(query_string)
params = parse_qs(query_string)
#print(params)
entry = params.get("q", [""])[0]
lang = params.get("lang", [""])[0]
#print("Content-Type: text/plain\n")
#print(f"Entry: {entry}")
#print(f"  Lang: {lang}")

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

# Check the index
file_ref = ""
if os.path.isfile(word_index):
    try:
        # file exists so show xml
        tree = ET.parse(word_index)
        #tree = ET.parse(word_index, parser=ET.XMLParser(encoding="utf-8"))
        result = tree.xpath(f'//word[word-form="{entry}"]/file-ref/text()')
        index_lang = tree.xpath(f'//word[word-form="{entry}"]/lang/text()')
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
matches = index_root.xpath(f'word[word-form="{entry}"]')
if not matches:
    matches = index_root.xpath(f'word[contains(word-form, "{entry}")]')
#matches = index_root.xpath(f'word[starts-with(word-form, "{entry}")]')

#matches = list({(m.findtext("word-form"), m.findtext("lang"), m.findtext("file-ref")): m for m in matches}.values())
#matches = list({m.findtext("file-ref"): m for m in matches}.values())
#matches = list(dict.fromkeys(matches))
#print([m.text for m in matches])
#print(matches)
#for m in matches:
#    print(ET.tostring(m, encoding="unicode"))

results = []

for w in matches:
    if w.findtext("lang") == lang:
        #results.append(w.findtext("file-ref"))
        #if file_ref not in results:
        if w.findtext("file-ref") not in results:
            results.append(w.findtext("file-ref"))
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
    #            x.findtext("lang")
    #        ))


if len(results) == 1:
    file_path = dir + "/" + results[0] + ".xml"

    if os.path.isfile(file_path):
        try:
            html = ET.parse(file_path)
            xslt = ET.parse("entry.xsl")
            transform = ET.XSLT(xslt)
            res = transform(html)

            res = ET.tostring(res, pretty_print=True, encoding="unicode")
            res = "<!DOCTYPE HTML>\n" + res
            res = res.replace("<body>", "<body>\n    " + input_form())
            res = res.replace("<html>", "<html lang=\"" + page_lang + "\">")
            res = res.replace('<table border="1"/>', "<p>" + no_data + "</p>")
            res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

            print(res)

        except (ET.XMLSyntaxError, ET.XSLTApplyError) as e:
            #print(f"Error processing XML/XSLT: {e}")
            print(xslt_error + ": " + e)

elif len(results) > 15:
    res = "<!DOCTYPE HTML>\n<html lang=\"" + page_lang + "\">\n  <body>\n"
    res += input_form()

    if lang == search_lang:
        #res += "\n    <b>Results for " +  search_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b><br/><br/>"
        res = res.replace("{search_lang_name}", search_lang_name)
    if lang == data_lang:
        #res += "\n    <b>Results for " + data_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b><br/><br/>"
        res = res.replace("{search_lang_name}", data_lang_name)

    #res += "\n    <ul>"
    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

    for r in results:
        #res += "<li>" + r + "</li>"
        #res += '\n        <li><a href="/?q=' + r + '&lang=' + data_lang + '">' + r + '</a></li>'
        res += '\n        <a href="/?q=' + r + '&lang=' + data_lang + '">' + r + '</a>&nbsp;'
    res += "\n  </body>\n</html>"

    print(res)

elif len(results) > 1:
    res = "<!DOCTYPE HTML>\n<html lang=\"" + page_lang + "\">\n  <body>\n"
    res += input_form()

    if lang == search_lang:
        #res += "\n    <b>Results for " +  search_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        res = res.replace("{search_lang_name}", search_lang_name)
    if lang == data_lang:
        #res += "\n    <b>Results for " + data_lang_name + " search: <u>" + entry + "</u></b>"
        res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        res = res.replace("{search_lang_name}", data_lang_name)

    res += "\n    <ul>"
    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")

    for r in results:
        #res += "<li>" + r + "</li>"
        res += '\n        <li><a href="/?q=' + r + '&lang=' + data_lang + '">' + r + '</a></li>'
    res += "\n    </ul>\n  </body>\n</html>"

    print(res)


else:
    res = "<!DOCTYPE HTML>\n<html lang=\"" + lang + "\">\n  <body>\n  </body>\n</html>"

    if entry:
        res = res.replace("<body>", "<body>\n    " + input_form() + "\n    <p>" + not_found + "</p>")
    else:
        res = res.replace("<body>", "<body>\n    " + input_form())

    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    print(res)
