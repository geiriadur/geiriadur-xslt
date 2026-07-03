#from __main__ import *
from globals import *
import lxml.etree as ET
import os

# FUNCTIONS

def transform_html(html, page_lang):
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

    # These are only local and won't  work outside the function
    #word_index = dictionary.get("word_index")
    #dir = dictionary.get("dir")
    #default_page_lang = dictionary.get("default_page_lang")

    globals()['word_index'] = dictionary.get("word_index")
    globals()['dir'] = dictionary.get("dir")
    globals()['default_page_lang'] = dictionary.get("default_page_lang")
    globals()['random_word_on'] = dictionary.get("random_word_on")

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
    return results

def get_random_word(query_lang):
    results = check_index("", query_lang) # Deliberate empty search
    # Deduplicate any results found
    results = list({item.split(':')[0]: item for item in results}.values())
    results = list({item.split(':')[1]: item for item in results}.values())
    import random
    result = random.choice(results).split(':')[0]
    return(result)

def get_res(entry, query_lang):
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
    return res

def res_no_results(entry, query_lang):
    res = "<!DOCTYPE HTML>\n<html lang=\"" + query_lang + "\">\n  <body>\n  </body>\n</html>"

    if entry:
        res = res.replace("<body>", "<body>\n    " + input_form() + "\n    <p>" + not_found + "</p>")
    else:
        res = res.replace("<body>", "<body>\n    " + input_form())

        # Print a random word from the data language
        if 'random_word_on' in globals() and random_word_on:
          random_word = get_random_word(data_lang)
          random_word = '<a href="/?q=' + random_word + '&sl=' + data_lang + '&lang=' + query_lang + '">' + random_word + '</a>'
          res = res.replace("</body>", "  " + random_word + "\n</body>")

    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    return res
