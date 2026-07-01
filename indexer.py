# CONSTANTS

# Stopwords for translation
stopwords = ["or", "and", "ones", "one"]
# Text language
text_lang = "cel-x-brit"
# Translation language
translation_lang = "en"

folder = "xml"  # folder with XML files
index_file = "word_index.xml"

# CODE FOLLOWS

import os
import re
from lxml import etree as ET

# Load or create the index
if os.path.isfile(index_file):
    index_tree = ET.parse(index_file)
    index_root = index_tree.getroot()
else:
    index_root = ET.Element("index")
    index_tree = ET.ElementTree(index_root)

# Iterate over all XML files except word_index.xml
for filename in os.listdir(folder):
    if not filename.endswith(".xml") or filename == index_file:
        continue

    path = os.path.join(folder, filename)
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
                        if not index_root.xpath(f'word[word-form="{word}" and file-ref="{os.path.splitext(filename)[0]}"]'):
                        #if not index_root.xpath(f'word[word-form="{word}"]'):
                            w = ET.SubElement(index_root, "word")
                            ET.SubElement(w, "word-form").text = word
                            if tag == "translation":
                                ET.SubElement(w, "lang").text = translation_lang
                            else:
                                ET.SubElement(w, "lang").text = text_lang
                            ET.SubElement(w, "file-ref").text = os.path.splitext(filename)[0]

    except ET.XMLSyntaxError:
        print(f"Skipping malformed XML: {filename}")

# Write back the index
index_root[:] = sorted(index_root, key=lambda w: (w.findtext("word-form") or "").lower())
ET.indent(index_root, space="    ")  # 4 spaces per level
index_tree.write(index_file, encoding="UTF-8", xml_declaration=True, pretty_print=True)
