import numpy as np
import random
import json
import urllib.request

from keras.layers import Input, Embedding, Dot, Reshape, Dense
from keras.models import Model
from collections import Counter, OrderedDict

random.seed(100)

books = []

# with urllib.request.urlopen('https://github.com/fylux/BookRecommendations/blob/master/data/books.ndjson?raw=true') as fin:
with open("../data/books.ndjson") as fin:
    books = [json.loads(l) for l in fin]

# Remove non-book articles
books = [book for book in books if 'Wikipedia:' not in book[0]]
print(f'There are {len(books)} books.')

book_index = {book[0]: idx for idx, book in enumerate(books)}
index_book = {idx: book for book, idx in book_index.items()}

# Wikilinks for each book
wikilinks = []
for book in books:
    links = list({link.lower() for link in book[2]})
    wikilinks.extend(links)

print(f"There are {len(set(wikilinks))} unique wikilinks.")

# Sort by highest count
counts = sorted(Counter(wikilinks).items(), key = lambda x: x[1], reverse = True)
wikilink_counts = OrderedDict(counts)

to_remove = ['hardcover', 'paperback', 'hardback', 'e-book', 'wikipedia:wikiproject books', 'wikipedia:wikiproject novels']
for t in to_remove:
    wikilinks.remove(t)
    _ = wikilink_counts.pop(t)

# Since there are so many links let's take only those that appear at least 4 times
links = [t[0] for t in wikilink_counts.items() if t[1] >= 4]

link_index = {link: idx for idx, link in enumerate(links)}
index_link = {idx: link for link, idx in link_index.items()}

print(f'{len(link_index)} wikilinks will be used.')

pairs = []

# Iterate through each book and its links
for book in books:
    b_index = book_index[book[0]]
    pairs.extend((b_index, link_index[link.lower()])for link in book[2] if link.lower() in links)

pairs_set = set(pairs)

def generate_batch(pairs, n_positive = 50, negative_ratio = 1.0):
    batch_size = n_positive * (1 + negative_ratio)
    batch = np.zeros((batch_size, 3))
    
    while True:
        # Random positive examples
        for idx, (book_id, link_id) in enumerate(random.sample(pairs, n_positive)):
            batch[idx, :] = (book_id, link_id, 1)

        idx += 1
        
        # Add negative examples 
        while idx < batch_size:
            random_book = random.randrange(len(books))
            random_link = random.randrange(len(links))
            
            # Check to make sure this is not a positive example
            if (random_book, random_link) not in pairs_set:
                batch[idx, :] = (random_book, random_link, -1)
                idx += 1
                
        np.random.shuffle(batch)
        yield {'book': batch[:, 0], 'link': batch[:, 1]}, batch[:, 2]


def book_embedding_model(embedding_size = 50):
    book = Input(name = 'book', shape = [1])
    link = Input(name = 'link', shape = [1])
    
    book_embedding = Embedding(name = 'book_embedding',
                               input_dim = len(book_index),
                               output_dim = embedding_size)(book)
    
    link_embedding = Embedding(name = 'link_embedding',
                               input_dim = len(link_index),
                               output_dim = embedding_size)(link)
    
    merged = Dot(name = 'dot_product', normalize = True, axes = 2)([book_embedding, link_embedding])
    merged = Reshape(target_shape = [1])(merged)

    model = Model(inputs = [book, link], outputs = merged)
    model.compile(optimizer = 'Adam', loss = 'mse')
    
    return model

model = book_embedding_model()
n_positive = 1024
negative_ratio = 2

batches = generate_batch(pairs, n_positive, negative_ratio)
model.fit_generator(batches, epochs = 15, steps_per_epoch = len(pairs) // n_positive, verbose = 2);

model.save('model.h5')