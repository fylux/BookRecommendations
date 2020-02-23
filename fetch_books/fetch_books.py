import urllib.request
import requests
import bz2
import subprocess
import xml.sax
import re
import mwparserfromhell
import json
import os
import sys

from bs4 import BeautifulSoup

compFile = 'wikipedia_articles_comp.bz2'
decompFile = 'wikipedia_articles.xml'

# If we want to download the file automatically
# urllib.request.urlretrieve("https://dumps.wikimedia.org/enwiki/20200201/enwiki-20200201-pages-articles.xml.bz2", compFile)

# Decompress the file if not already uncompressed
if os.path.exists(compFile):
    command = f'bzcat {compFile} >> {decompFile}'
    subprocess.call([command], shell = True)
elif not (os.path.exists(decompFile)):
    print(f'File {decompFile} does not exit')


def process_article(title, text, timestamp):
    """Process a wikipedia article looking for Infobox book"""

    template = 'Infobox book'
    wikicode = mwparserfromhell.parse(text)
    wikicode.filter_comments()

    # Search through templates for the template
    matches = wikicode.filter_templates(matches = template)
    
    # Filter out errant matches
    matches = [x for x in matches if x.name.strip_code().strip().lower() == template.lower()]
    
    if len(matches) >= 1:
        # Extract information from infobox
        properties = {param.name.strip_code().strip(): param.value.strip_code().strip() 
                      for param in matches[0].params
                      if param.value.strip_code().strip()}

        wikilinks = [x.title.strip_code().strip() for x in wikicode.filter_wikilinks()]
        exlinks = [x.url.strip_code().strip() for x in wikicode.filter_external_links()]

        # Find length of article
        text_length = len(wikicode.strip_code().strip())

        return (title, properties, wikilinks, exlinks, timestamp, text_length)

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Parse through XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._books = []
        self._article_count = 0
        self._non_matches = []

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text', 'timestamp'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            self._article_count += 1
            book = process_article(**self._values, template = 'Infobox book')
            if book:
                self._books.append(book)

handler = WikiXmlHandler()
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

# Parse the entire file
with open(decompFile) as file_in:
    for i, line in enumerate(file_in.readlines()):
        if i % 10_000 == 0: print(f"Line {i}")
        try:
            parser.feed(line)
        except StopIteration:
            print("End parsing")
            break
    
books = handler._books

print(f'\nSearched through {handler._article_count} articles.')
print(f'\nFound {len(books)} books.')

with open('../data/books.ndjson', 'wt') as fout:
    for l in books:
        fout.write(json.dumps(l) + '\n')