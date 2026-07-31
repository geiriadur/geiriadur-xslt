from globals import *
from functions import get_defs, get_keys

# CONSTANTS

# Stopwords for translation

# Gets values required for indexer
get_defs("page_lang")
get_keys(keys, page_lang)
# Have to do this again to get the results
from functions import *

# CODE FOLLOWS

import os
import re
from lxml import etree as ET

# Load or create the index
if os.path.isfile(word_index):
    index_tree = ET.parse(word_index)
    index_root = index_tree.getroot()
else:
    index_root = ET.Element("index")
    index_tree = ET.ElementTree(index_root)

# Iterate over all XML files except word_index.xml
for filename in os.listdir(dir):
    if not filename.endswith(".xml") or filename == word_index:
        continue

    path = os.path.join(dir, filename)
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        # Find all headword-form, plural-form, fem-form elements
        for tag in tags:
            for elem in root.xpath(f"//{tag}"):
                # New code to allow searching the words in the translation
                entry = elem.text.strip()
                if tag in full_text_tags:
                    entry = ''.join(elem.itertext()).strip()
                else:
                    entry = elem.text.strip()
                lang = elem.get("lang", "")
                lang = elem.get("lang", elem.get("{http://www.w3.org/XML/1998/namespace}lang", ""))
                print(entry, lang) # Screen output at command line
                # With Python's split you can only use one delimiter at a time
                # Old method split all fields, not just translation
                #words = re.split(r"[:;,.\(\)\-\s]", entry)
                pattern = r"\b"
                if tag == "translation":
                    pattern = r"[:;,.\(\)\-\s]"
                # Includes capture groups i.e. the items in the above regex
                #words = re.split(pattern, entry)
                # This method does not include capture groups
                delim="<-split->"
                #words = re.split(delim, re.sub(pattern, delim, entry))
                # Slightly faster to use inbuilt split rather than re operations twice
                entry = re.sub(pattern, delim, entry)
                words = entry.split(delim)
                # Remove unwanted common words
                if tag == "translation":
                    words = [block_word for block_word in words if block_word not in stopwords]
                for word in words:
                    word = word.strip()
                    if word and not any(c.isalnum() for c in word): continue # Stops search-forms that are only punctuation
                    if word:
                        # Avoid duplicate entries
                        if not index_root.xpath(f'word[search-form="{word}" and file-ref="{os.path.splitext(filename)[0]}"]'):
                        #if not index_root.xpath(f'word[search-form="{word}"]'):

                            #entry = elem.xpath('./ancestor::entry[1]')[0]
                            ##entry = elem.xpath('./ancestor::*[1]')[0] # Attempt 1
                            ##entry = elem.xpath('./ancestor::' + '|./ancestor::'.join(entry_tags) + '[1]')[0] # Attempt 2
                            ##print(elem.tag, elem.getroottree().getpath(elem)) # FOR TESTING
                            entries = elem.xpath('./ancestor::' + '|./ancestor::'.join(entry_tags) + '[1]')
                            if not entries:
                                continue
                            entry = entries[0]
                            #headwords = [h.text.strip() for h in entry.findall('./head/headword-form')]
                            headwords = [h.text.strip() for tag in word_form_tags for h in entry.xpath(f'.//{tag}') if h.text]
                            #headword = entry.findtext('./head/headword-form', '')
                            for headword in headwords:
                                w = ET.SubElement(index_root, "word")

                                ET.SubElement(w, "word-form").text = headword
                                ET.SubElement(w, "search-form").text = word

                                #if tag == "translation":
                                #    ET.SubElement(w, "slang").text = lang # or search_lang
                                #else:
                                #    ET.SubElement(w, "slang").text = data_lang
                                ET.SubElement(w, "slang").text = lang or data_lang

                                ET.SubElement(w, "file-ref").text = os.path.splitext(filename)[0]

    except ET.XMLSyntaxError:
        print(f"Skipping malformed XML: {filename}")

# Write back the index
index_root[:] = sorted(index_root, key=lambda w: (w.findtext("word-form") or "").lower())
ET.indent(index_root, space="    ")  # 4 spaces per level
index_tree.write(word_index, encoding="UTF-8", xml_declaration=True, pretty_print=True)
