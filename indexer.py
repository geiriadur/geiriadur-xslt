from globals import *
from functions import get_keys

# CONSTANTS

# Stopwords for translation
#stopwords = ["or", "and", "ones", "one"]

# Gets values required for indexer
get_keys()
# Have to do this again to get the results
from functions import *

# Moved to globals.py and yaml via functions.py
# Data language
#data_lang = "cy"
# Search language
#search_lang = "en"

#dir = "xml"  # folder with XML files
#word_index = "word_index.xml"

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
        for tag in ["headword-form", "plural-form", "fem-form", "translation"]:
            for elem in root.xpath(f"//{tag}"):
                #word = elem.text.strip()
                # New code to allow searching the words in the translation
                entry = elem.text.strip()
                # With Python's split you can only use one delimiter at a time
                #words = entry.split(",")
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
                    if word:
                        # Avoid duplicate entries
                        if not index_root.xpath(f'word[search-form="{word}" and file-ref="{os.path.splitext(filename)[0]}"]'):
                        #if not index_root.xpath(f'word[search-form="{word}"]'):

                            entry = elem.xpath('./ancestor::entry[1]')[0]
                            headwords = [h.text.strip() for h in entry.findall('./head/headword-form')]
                            #headword = entry.findtext('./head/headword-form', '')
                            '''
                            w = ET.SubElement(index_root, "word")

                            ET.SubElement(w, "word-form").text = headword
                            ET.SubElement(w, "search-form").text = word

                            if tag == "translation":
                                ET.SubElement(w, "slang").text = search_lang
                            else:
                                ET.SubElement(w, "slang").text = data_lang

                            ET.SubElement(w, "file-ref").text = os.path.splitext(filename)[0]

                            '''
                            for headword in headwords:
                                w = ET.SubElement(index_root, "word")

                                ET.SubElement(w, "word-form").text = headword
                                ET.SubElement(w, "search-form").text = word

                                if tag == "translation":
                                    ET.SubElement(w, "slang").text = search_lang
                                else:
                                    ET.SubElement(w, "slang").text = data_lang

                                ET.SubElement(w, "file-ref").text = os.path.splitext(filename)[0]

                            #w = ET.SubElement(index_root, "word")
                            '''
                            if tag == "headword-form":
                                headword = elem.text.strip()
                            else:
                                entry = elem.xpath('./ancestor::entry[1]')[0]
                                headword = entry.findtext('./head/headword-form', '')

                            ET.SubElement(w, "word-form").text = headword
                            '''
                            #entry = elem.xpath('./ancestor::entry[1]')[0]

                            #if tag == "headword-form":
                            #    headwords = [h.text.strip() for h in entry.findall('./head/headword-form')]
                            #else:
                            #    headwords = [entry.findtext('./head/headword-form', '')]

                            #for headword in headwords:
                            #    ET.SubElement(w, "word-form").text = headword

                            #ET.SubElement(w, "search-form").text = word

                            #if tag == "translation":
                            #    ET.SubElement(w, "slang").text = search_lang
                            #else:
                            #    ET.SubElement(w, "slang").text = data_lang
                            #print(headword+":"+word+":"+ os.path.splitext(filename)[0])

                            #file_ref = os.path.splitext(filename)[0]
                            #print(headword + " : " + word + ":" + file_ref)
                            #ET.SubElement(w, "file-ref").text = file_ref
                            #ET.SubElement(w, "file-ref").text = os.path.splitext(filename)[0]

    except ET.XMLSyntaxError:
        print(f"Skipping malformed XML: {filename}")

# Write back the index
index_root[:] = sorted(index_root, key=lambda w: (w.findtext("word-form") or "").lower())
ET.indent(index_root, space="    ")  # 4 spaces per level
index_tree.write(word_index, encoding="UTF-8", xml_declaration=True, pretty_print=True)
