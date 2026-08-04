#from __main__ import *
from globals import *
import lxml.etree as ET
from urllib.parse import parse_qs
import os
import sys
from html import escape
import re

# FUNCTIONS

def transform_html(html, page_lang):
    for l in search_langs:
      if 'lang'+str(search_langs.index(l)+1) in globals():
          html = html.replace("{lang"+str(search_langs.index(l)+1)+"}", globals()['lang'+str(search_langs.index(l)+1)])
      if 'lang'+str(search_langs.index(l)+1)+"_name" in globals():
          html = html.replace("{lang"+str(search_langs.index(l)+1)+"_name}", globals()['lang'+str(search_langs.index(l)+1)+'_name'])
    html = html.replace("{search_button_name}", search_button_name)
    html = html.replace("{page_title}", page_title)
    html = html.replace("{language}", page_lang)
    html = html.replace("{regex_label}", regex_label)
    html = html.replace("{xslt_alt_label}", xslt_alt_label)

    # Translation keys
    if 'tkeys' in globals():
      for key, value in tkeys.items():
        html = html.replace(key, value)

    return html


def transform_regex_labels(res, query_lang, regex_on, xslt_alt_on):
    if not query_lang: query_lang = search_langs[0]
    res = res.replace('{'+query_lang+'_checked}', 'checked')
    for l in search_langs:
        if not l == query_lang:
            res = res.replace(' {'+l+'_checked}', '')
    if regex_on:
      res = res.replace("{regex_checked}", "checked")
    else:
      res = res.replace(" {regex_checked}", "")
    # Select radio button if alt xslt used
    if xslt_alt_on:
      res = res.replace("{xslt_alt_checked}", "checked")
    else:
      res = res.replace(" {xslt_alt_checked}", "")

    return res

def input_form(query_string, query_lang, page_lang, regex_on):
    if not page_lang: page_lang = default_page_lang
    html = ""
    for l in interface_langs:
        if 'lang'+str(interface_langs.index(l)+1) in globals() and 'lang'+str(interface_langs.index(l)+1)+"_name" in globals():
            lang_name = globals()[l]["lang"+str(interface_langs.index(l)+1)+"_name"]
            html_add = ""
            if not l == page_lang:
                html_add += '<a href="?'+escape(query_string)+'">'+lang_name+'</a> '
            else:
                html_add += lang_name+' '
            #if not "sl=" in html_add:
            #    html_add = html_add.replace('">', '&sl='+interace_langs[0]+'">')
            if "lang=" in html_add:
                html_add = html_add.replace('lang='+escape(page_lang), 'lang='+l)
            else:
                html_add = html_add.replace('">', '&lang='+l+'">')
            if not l == page_lang or current_lang_label: html += html_add
    if len(interface_langs) > 1: html = "<p>" + html + "</p>"
    else: html = ""
    html += '''\n    <p>
      <form id="myForm" action="/" method="get">
        <p><input type="text" id="myInput3" name="q"></p>
        {lang_section}
        <p><button type="submit" name="">{search_button_name}</button><br/>
        <input type="hidden" name="lang" value="{language}">
        </p>
        <p>{regex_line}<br/>
        {xslt_line}</p>
      </form>
    </p>
    <div id="message"/>'''
    lang_section = "\n"
    for l in search_langs:
        if 'lang'+str(search_langs.index(l)+1) in globals() and 'lang'+str(search_langs.index(l)+1)+"_name" in globals():
            lang_section += '        {lang'+str(search_langs.index(l)+1)+'_name}<input type="radio" name="sl" value="{lang'+str(search_langs.index(l)+1)+'}" {'+l+'_checked}>'
            lang_section += "\n"
    lang_section += "        "
    lang_section = "<p>" + lang_section + "</p>"
    if len(search_langs) > 1:
        html = html.replace("{lang_section}", lang_section)
    else:
        html = html.replace("{lang_section}", "")
    if regex_tickbox:
      html = html.replace('{regex_line}<br/>', '{regex_label}? <input type="checkbox" id="regex" name="regex" value="1" {regex_checked}><br/>')
    else:
      html = html.replace("{regex_line}<br/>", "")
    if xslt_alt_enabled:
      html = html.replace('{xslt_line}', '{xslt_alt_label}? <input type="checkbox" id="xslt_alt" name="x" value="1" {xslt_alt_checked}>')
    else:
      html = html.replace("{xslt_line}", "")

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
        #if not isinstance(value, dict): # Prevents any item with sub-values from being parsed # Removed beause of interface lang labels
            defs.append((key, value))
    return defs

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

    # Gets values required for interface
    defs = get_defs(page_lang)
    for key, value in defs:
        globals()[key] = value

    value = dictionary.get(fetch_lang, dictionary["en"])

    for key, value in value.items():
      #globals()[key] = value # Could potentially overwrite any global
      # Safer because it prevents overwriting values already is use
      #if not key in globals(): globals()[key] = value
      # Only replace the globals if they exist, otherwise leave them
      if key in globals() and isinstance(globals()[key], dict) and isinstance(value, dict):
          globals()[key].update(value)
      else:
          globals()[key] = value

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
        except (ET.XMLSyntaxError, ET.XSLTApplyError) as e:
            print(xslt_error + ": " + e)

    file_path = dir + "/" + str(file_ref)+".xml" # Check entry from query_string in index for filename

    index_tree = ET.parse(word_index)
    index_root = index_tree.getroot()
    # REMOVE XPATH INJECTION
    #matches = index_root.xpath(
    #    'word[search-form=$term]',
    #    term=entry
    #)
    matches = [
        w for w in index_root.xpath('word')
        if w.findtext("search-form", "").lower() == entry
    ]
    if not matches:
        # REMOVE XPATH INJECTION
        #matches = index_root.xpath(
        #    'word[contains(search-form, $term)]',
        #    term=entry
        #)
        matches = [
            w for w in index_root.xpath('word')
            if entry in w.findtext("search-form", "").lower()
        ]

    results = []

    for w in matches:
        if w.findtext("slang") == query_lang:
            if w.findtext("word-form") not in results:
                results.append(w.findtext("word-form")+":"+w.findtext("search-form")+":"+w.findtext("file-ref"))
            results = sorted(results)
    return results

def check_index_regex(entry, query_lang):
    #pattern = re.compile(entry)
    pattern = re.compile(entry, re.IGNORECASE)
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

def get_res(entry, query_string, query_lang, page_lang, regex_on, xslt_alt_on):
    # SHOULD BE SAFE BUT AVOID HTML INJECTION JUST IN CASE
    res = "<!DOCTYPE HTML>\n<html lang=\"" + escape(page_lang) + "\">\n  <body>\n"
    res += input_form(query_string, query_lang, page_lang, regex_on)

    # AVOID HTML INJECTION
    res += "\n    <b>"+lang_results_msg+": <u>" + escape(entry) + "</u></b>"
    # Change message and select radio button if regex used
    if regex_on:
      res = res.replace(search_msg + " {results_lang_name}", " " + regex_msg + " {results_lang_name}")
      res = res.replace("{results_lang_name} "+ search_msg, "{results_lang_name} " + regex_msg)

    res = transform_regex_labels(res, query_lang, regex_on, xslt_alt_on)
    res = res.replace("{results_lang_name}", globals()[page_lang]['lang'+str(search_langs.index(query_lang)+1)+'_name'])

    res += "\n    <ul>"
    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    return res

def res_no_results(entry, query_string, query_lang, page_lang, regex_on, xslt_alt_on):
    res = "<!DOCTYPE HTML>\n<html lang=\"" + page_lang + "\">\n  <body>\n  </body>\n</html>"

    if entry:
        res = res.replace("<body>", "<body>\n    " + input_form(query_string, query_lang, page_lang, regex_on) + "\n    <p>" + not_found + "</p>")
    else:
        res = res.replace("<body>", "<body>\n    " + input_form(query_string, query_lang, page_lang, regex_on))

        # Print a random word from the data language
        if 'random_word_on' in globals() and random_word_on:
          random_word = get_random_word(data_lang)
          random_word = '<a href="/?q=' + random_word + '&sl=' + data_lang + '&lang=' + page_lang + '">' + random_word + '</a>'
          res = res.replace("</body>", "  " + random_word + "\n</body>")

    res = transform_regex_labels(res, query_lang, regex_on, xslt_alt_on)

    res = res.replace("<body>", "<head>\n  " + head() + "\n  </head>\n  <body>")
    return res
