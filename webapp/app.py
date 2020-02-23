import json
import urllib.request
import re
import wikipedia
import hashlib
import numpy as np
import random
import urllib.request

from collections import Counter
from itertools import chain
import requests
import wptools

from keras.models import Model
from keras.models import load_model

from flask_ngrok import run_with_ngrok
from flask import Flask
from flask import render_template_string, render_template

random.seed(100)

wikipedia.set_lang("en")


books = []

with urllib.request.urlopen('https://github.com/fylux/BookRecommendations/blob/master/data/books.ndjson?raw=true') as fin:
with open("../data/books.ndjson") as fin:
    books = [json.loads(l) for l in fin]

# Remove non-book articles
books = [book for book in books if 'Wikipedia:' not in book[0]]
print(f'There are {len(books)} books.')

def existsUrl(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok

unknownImg = "../static/img/unknown_book.png"
cache_img_url = {}
def getImg(idx, fast=False):
    if idx in cache_img_url:
        return cache_img_url[idx]

    url = ""
    if 'image' in books[idx][1]:
        img = books[idx][1]['image']
        ext = img[-4:].lower()
        if 'File:' == img[:5]:
            img = img[5:]
        if ext in ['.jpg','.png','.svg','.gif']:
            url = getImgUrl(img.replace(" ","_"))

    if url != "":
        cache_img_url[idx] = url
        return cache_img_url[idx]

    elif fast: return unknownImg

    try:
        p = wptools.page(index_book[idx])
        p.get()
        url = p.data['image'][0]['url']
        if existsUrl(url):
            cache_img_url[idx] = url
            return cache_img_url[idx]
    except:
        pass

    cache_img_url[idx] = unknownImg
    return cache_img_url[idx]

def getImgUrl(imgName):
    if imgName == "": return ""
    md5sum = hashlib.md5(imgName.encode('utf-8')).hexdigest()
    url = "https://upload.wikimedia.org/wikipedia/commons/"+md5sum[0]+"/"+md5sum[:2]+"/"+imgName
    if existsUrl(url): return url
    url = "https://upload.wikimedia.org/wikipedia/en/"+md5sum[0]+"/"+md5sum[:2]+"/"+imgName
    if existsUrl(url): return url
    url = "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+imgName
    if existsUrl(url): return url
    return ""


def getYear(idx):
    fields = ["published","pub_date","release_date","caption"]
    for field in fields:
        if field in books[idx][1]:
            m = re.findall('\d\d\d\d',  books[idx][1][field])
            if len(m) > 0:
                return m[0]
    return "-1"

def getAuthor(idx):
    fields = ["author"]
    for field in fields:
        if field in books[idx][1]:
            return books[idx][1][field]
    return ""

def cleanBrackets(text):
    text = re.sub(r'\([^()]*\)', '', text)
    text = re.sub(r'\([^()]*\)', '', text)
    text = re.sub(r' ,', ',', text)
    return re.sub(r' ', ' ', text)

cache_summary = {}
def getSummary(pageName):
    if pageName in cache_summary: return cache_summary[pageName]

    pageName = pageName.replace(" ","_")
    try:
        cache_summary[pageName] = cleanSummary(wikipedia.summary(pageName, sentences=2))
        return cache_summary[pageName]
    except:
        pass

    try:
        alternativeName = wikipedia.search(pageName)[0]
        cache_summary[pageName] = cleanBrackets(wikipedia.summary(alternativeName, sentences=2))
        return cache_summary[pageName]
    except:
        return ""

book_index = {book[0]: idx for idx, book in enumerate(books)}
index_book = {idx: book for book, idx in book_index.items()}

book_author = {}
book_year = {}
book_index = {}
index_book = {}
books_of_author = {}

for i, book in enumerate(books):
    book_index.update({book[0] : i})
    index_book.update({i : book[0]})

    author = getAuthor(i)
    book_author.update({i : author})
    book_year.update({i : getYear(i)})
    
    if author not in books_of_author:
        books_of_author.update({author : [i]})
    else:
        books_of_author[author].append(i)

for author, author_books in books_of_author.items():
    books_of_author[author] = sorted(author_books, key=lambda id: int(book_year[id]))

model = load_model("../embeddings/model.h5")
book_layer = model.get_layer('book_embedding')
book_weights = book_layer.get_weights()[0]
book_weights = book_weights / np.linalg.norm(book_weights, axis = 1).reshape((-1, 1))

def find_similar(name, weights, n = 10, return_dist = False):
    n += 1
    
    # Make sure book exists
    try:
        # Calculate dot product between book and all others
        dists = np.dot(weights, weights[book_index[name]])
    except KeyError:
        print(f'{name} Not Found.')
        return
    
    # Sort distance from smallest to largest
    sorted_dists = np.argsort(dists)
    
    # Take the last n sorted distances
    closest = sorted_dists[-n:][:-1]

    if return_dist:
        return [index_book[c] for c in reversed(closest)]


app = Flask(__name__)

run_with_ngrok(app)

@app.route("/")
def main_page():
    return book_page("Don Quixote")

@app.route("/book/<book>")
def book_page(book):
    book = book.replace('_',' ')
    img_url = pred = "",
    year = author = summary = ""
    if book in book_index:
        idx = book_index[book]
        img_url = getImg(idx)
        year = getYear(idx)
        author = getAuthor(idx)
        summary = getSummary(book)

        pred = find_similar(book, book_weights, n = 9, return_dist = True)
        other_books = []
        for b in pred:
            url = getImg(book_index[b],fast=True)
            if url != "":
                other_books.append({'name':b,'url':url})
            if len(other_books) >= 5: break

        return render_template("book.html", book_name=cleanBrackets(book), author=author, year=year,img_url=img_url, summary = summary, other_books=other_books)
    else:
        return render_template_string("Error book not found")

@app.route("/author/<author>")
def author_page(author):
    author = author.replace('_',' ')
    if author in books_of_author:
        raw_books = books_of_author[author]
        books = [ {'name': index_book[b], 'url' : getImg(b, fast=True), 'year': getYear(b)} for b in raw_books]

        return render_template("author.html", author = author, books = books)
    else:
        return render_template_string("Error author not found")

app.run()