#from __main__ import *
from globals import *
import lxml.etree as ET
import os
from html import escape
import re

# FUNCTIONS

'''
# No longer required
def get_xml(value, page_lang):
  get_keys(keys, page_lang)
  return globals()[value]
'''

def transform_html(html, page_lang):
    html = html.replace("{search_lang_name}", search_lang_name)
    html = html.replace("{data_lang_name}", data_lang_name)
    html = html.replace("{search_lang}", search_lang)
    html = html.replace("{data_lang}", data_lang)
    html = html.replace("{search_button_name}", search_button_name)
    html = html.replace("{page_title}", page_title)
    html = html.replace("{language}", page_lang)
    html = html.replace("{regex_label}", regex_label)


    # Translation keys
    #print(tkeys)
    if 'tkeys' in globals():
      for key, value in tkeys.items():
        #print(key+"==="+value)
        html = html.replace(key, value)
        #globals()[key] = value

    return html


def transform_regex_lebels(res, query_lang, search_lang, regex_on):
    if query_lang == search_lang:
        #res += "\n    <b>Results for " +  search_lang_name + " search: <u>" + entry + "</u></b>"
        #res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        # AVOID HTML INJECTION
        #res += "\n    <b>"+lang_results_msg+": <u>" + escape(entry) + "</u></b>"
        #res = res.replace("{results_lang_name}", search_lang_name)
        if regex_on:
          res = res.replace("{search_regex_checked}", "checked")
          res = res.replace(" {data_regex_checked}", "")
        else:
          res = res.replace(" {search_regex_checked}", "")
          res = res.replace(" {data_regex_checked}", "")
    if query_lang == data_lang:
        #res += "\n    <b>Results for " + data_lang_name + " search: <u>" + entry + "</u></b>"
        #res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        # AVOID HTML INJECTION
        #res += "\n    <b>"+lang_results_msg+": <u>" + escape(entry) + "</u></b>"
        #res = res.replace("{results_lang_name}", data_lang_name)
        if regex_on:
          res = res.replace(" {search_regex_checked}", "")
          res = res.replace("{data_regex_checked}", "checked")
        else:
          res = res.replace(" {search_regex_checked}", "")
          res = res.replace(" {data_regex_checked}", "")
    return res

def input_form(regex_on):
    html = '''<p>
      <form id="myForm\" action="/" method="get">
        {search_lang_name}: <input type="text" id="myInput" name="q">
        <input type="hidden" name="sl" value="{search_lang}">
        <input type="hidden" name="lang" value="{language}">
        <input type="submit" value="{search_button_name}">
        <!-- {regex_label}? --><!--input type="checkbox" id="regex" name="regex" value="1" {search_regex_checked}-->
        {search_regex_line}
      </form>
    </p>
    <p>
      <form id="myForm2" action="/" method="get">
        {data_lang_name}: <input type="text" id="myInput2" name="q">
        <input type="hidden" name="sl" value="{data_lang}">
        <input type="hidden" name="lang" value="{language}">
        <input type="submit" value="{search_button_name}">
        <!-- {regex_label}? --><!--input type="checkbox" id="regex" name="regex" value="1" {data_regex_checked}-->
        {data_regex_line}
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
    if regex_tickbox:
      html = html.replace('{search_regex_line}', '{regex_label}? <input type="checkbox" id="regex" name="regex" value="1" {search_regex_checked}>')
      html = html.replace('{data_regex_line}', '{regex_label}? <input type="checkbox" id="regex" name="regex" value="1" {data_regex_checked}>')
    else:
      html = html.replace("{search_regex_line}", "")
      html = html.replace("{data_regex_line}", "")

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

def get_defs(fetch_lang):
    import yaml

    from yaml import load
    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader

    stream = open(keys, 'r')
    dictionary = yaml.load(stream, Loader=yaml.SafeLoader) #safe
    #dictionary = yaml.load(stream) # unsafe

    defs = []

    for key, value in dictionary.items():
        if not isinstance(value, dict):
            defs.append((key, value))
    #print(defs)
    return defs

    '''#print(dictionary.keys())
    data = dictionary
    for key in dictionary:
      value = dictionary[key]
      if isinstance(value, dict):
          print(f"{key} contains keys")
          print("<br/>")
      else:
          print(f"{key} does not contain keys")
          print("<br/>")
    print("<br/>")
    for key, value in dictionary.items():
      if isinstance(value, dict):
          print(f"{key}: has nested items")
          print("<br/>")
      else:
          print(f"{key}: no nested items")
          print("<br/>")'''

def get_keys(keys, fetch_lang):
    import yaml

    from yaml import load
    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader

    stream = open(keys, 'r')
    dictionary = yaml.load(stream, Loader=yaml.SafeLoader) #safe
    #dictionary = yaml.load(stream) # unsafe

    # These are only local and won't work outside the function
    #word_index = dictionary.get("word_index")
    #dir = dictionary.get("dir")
    #default_page_lang = dictionary.get("default_page_lang")

    globals()['word_index'] = dictionary.get("word_index")
    globals()['dir'] = dictionary.get("dir")
    globals()['default_page_lang'] = dictionary.get("default_page_lang")
    globals()['random_word_on'] = dictionary.get("random_word_on")
    globals()['regex_on'] = dictionary.get("regex_on")
    globals()['regex_tickbox'] = dictionary.get("regex_tickbox")

    #missing = [v for v in ["word_index", "dir", "default_page_lang"] if v not in globals()]
    #for m in missing:
      #print("Variable \""+ m + "\" is missing in key file.")

    #present = [v for v in ["word_index", "dir", "default_page_lang"] if v in globals()]
    #for p in present:
      #print("Variable \""+ p + "\" is present in key file.")
      #print(p + " == " + globals()[p])
    #print("\n")

    value = dictionary.get(fetch_lang, dictionary["en"])
    #lang = next(k for k, v in dictionary.items() if v is value)

    for key, value in value.items():
      globals()[key] = value # Could potentially overwrite any global
      # Safer because it prevents overwriting values already is use
      #if not key in globals(): globals()[key] = value
      #print(str(key)+" : "+str(value))
      #print(key, type(value), repr(value))

def check_index(entry, query_lang):
    # Check the index
    file_ref = ""
    if os.path.isfile(word_index):
        try:
            # file exists so show xml
            tree = ET.parse(word_index)
            #tree = ET.parse(word_index, parser=ET.XMLParser(encoding="utf-8"))
            #result = tree.xpath(f'//word[search-form="{entry}"]/file-ref/text()')
            # REMOVE XPATH INJECTION
            result = tree.xpath(
                '//word[search-form=$term]/file-ref/text()',
                term=entry
            )
            #index_lang = tree.xpath(f'//word[search-form="{entry}"]/slang/text()')
            # REMOVE XPATH INJECTION
            index_lang = tree.xpath(
                '//word[search-form=$term]/slang/text()',
                term=entry
            )
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

    index_tree = ET.parse(word_index)
    index_root = index_tree.getroot()
    #matches = index_root.xpath(f'word[word-form="{entry}"]')
    #matches = index_root.xpath(f'word[contains(word-form, "{entry}")]')
    #matches = index_root.xpath(f'word[search-form="{entry}"]')
    # REMOVE XPATH INJECTION
    matches = index_root.xpath(
        'word[search-form=$term]',
        term=entry
    )
    if not matches:
        #matches = index_root.xpath(f'word[contains(search-form, "{entry}")]')
        # REMOVE XPATH INJECTION
        matches = index_root.xpath(
            'word[contains(search-form, $term)]',
            term=entry
        )

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
    return results

def check_index_regex(entry, query_lang):
    pattern = re.compile(entry)
    results = []

    index_tree = ET.parse(word_index)
    index_root = index_tree.getroot()

    for w in index_root.xpath('//word'):
        search_form = w.findtext("search-form", "")

        if pattern.search(search_form) and w.findtext("slang") == query_lang:
            results.append(
                w.findtext("word-form") + ":" +
                w.findtext("search-form") + ":" +
                w.findtext("file-ref")
            )

    return sorted(results)

def get_random_word(query_lang):
    results = check_index("", query_lang) # Deliberate empty search
    # Deduplicate any results found
    results = list({item.split(':')[0]: item for item in results}.values())
    results = list({item.split(':')[1]: item for item in results}.values())
    import random
    result = random.choice(results).split(':')[0]
    return(result)

def get_res(entry, query_lang, regex_on):
    #res = "<!DOCTYPE HTML>\n<html lang=\"" + page_lang + "\">\n  <body>\n"
    # SHOULD BE SAFE BUT AVOID HTML INJECTIONJUST IN CASE
    res = "<!DOCTYPE HTML>\n<html lang=\"" + escape(page_lang) + "\">\n  <body>\n"
    res += input_form(regex_on)

    #res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
    # AVOID HTML INJECTION
    res += "\n    <b>"+lang_results_msg+": <u>" + escape(entry) + "</u></b>"
    # Change message and slect radio button if regex used
    #print(search_msg +":"+regex_msg) # FOR TESTING
    if regex_on:
      res = res.replace(search_msg + " {results_lang_name}", " " + regex_msg + " {results_lang_name}")
      res = res.replace("{results_lang_name} "+ search_msg, "{results_lang_name} " + regex_msg)
      res = res.replace("{regex_checked}", "checked")
    else:
    #  res = res.replace(" {results_lang_name}", " " + search_msg + " {results_lang_name}")
    #  res = res.replace("{results_lang_name} ", "{results_lang_name} " + search_msg)
      res = res.replace(" {regex_checked}", "")

    res = transform_regex_lebels(res, query_lang, search_lang, regex_on)
    if query_lang == search_lang:
        #res += "\n    <b>Results for " +  search_lang_name + " search: <u>" + entry + "</u></b>"
        #res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        # AVOID HTML INJECTION
        #res += "\n    <b>"+lang_results_msg+": <u>" + escape(entry) + "</u></b>"
        res = res.replace("{results_lang_name}", search_lang_name)
        '''if regex_on:
          res = res.replace("{search_regex_checked}", "checked")
          res = res.replace(" {data_regex_checked}", "")
        else:
          res = res.replace(" {search_regex_checked}", "")
          res = res.replace(" {data_regex_checked}", "")'''
    if query_lang == data_lang:
        #res += "\n    <b>Results for " + data_lang_name + " search: <u>" + entry + "</u></b>"
        #res += "\n    <b>"+lang_results_msg+": <u>" + entry + "</u></b>"
        # AVOID HTML INJECTION
        #res += "\n    <b>"+lang_results_msg+": <u>" + escape(entry) + "</u></b>"
        res = res.replace("{results_lang_name}", data_lang_name)
        '''if regex_on:
          res = res.replace(" {search_regex_checked}", "")
          res = res.replace("{data_regex_checked}", "checked")
        else:
          res = res.replace(" {search_regex_checked}", "")
          res = res.replace(" {data_regex_checked}", "")'''

    res += "\n    <ul>"
    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    return res

def res_no_results(entry, query_lang, regex_on):
    res = "<!DOCTYPE HTML>\n<html lang=\"" + query_lang + "\">\n  <body>\n  </body>\n</html>"

    if entry:
        res = res.replace("<body>", "<body>\n    " + input_form(regex_on) + "\n    <p>" + not_found + "</p>")
    else:
        res = res.replace("<body>", "<body>\n    " + input_form(regex_on))

        # Print a random word from the data language
        if 'random_word_on' in globals() and random_word_on:
          random_word = get_random_word(data_lang)
          random_word = '<a href="/?q=' + random_word + '&sl=' + data_lang + '&lang=' + query_lang + '">' + random_word + '</a>'
          res = res.replace("</body>", "  " + random_word + "\n</body>")

    res = transform_regex_lebels(res, query_lang, search_lang, regex_on)
    # Select radio button if regex used
    '''if regex_on:
      res = res.replace(" {search_regex_checked}", "")
      res = res.replace("{data_regex_checked}", "checked")
    else:
      res = res.replace(" {search_regex_checked}", "")
      res = res.replace(" {data_regex_checked}", "")'''


    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    return res
