# Book Recommendations
The goal of this project is to provide book recommendations in an useful way. For that purpose, the recommendations are integrated in a web application allowing users to explore books and authors, taking advantage of recommendations as well as by enhancing the information about the books with information extracted from Wikimedia. The project is composed of three main parts.
 - Scraping and grouping information about books.
 - Training of a Neural Network for book recommendations.
 - Exposing book related information in a web application.
 
### Technologies
This project is mostly based on Python, in particular for all the aspects related scraping and machine learning. However, the web application makes use of specific web technologies such as HTML, CSS and JavaScript. Regarding the libraries that have been used, for scraping relies mostly on [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) together with some parsing utilies. The recommendation system is built using [Keras](https://github.com/keras-team/keras) and [Tensorflow](https://github.com/tensorflow/tensorflow). Finally, the web server is based on [Flask](https://github.com/pallets/flask).
 
## Book Scraping
To gather all the data about books in Wikipedia we rely on [dumps](https://dumps.wikimedia.org/enwiki/20200201/) which are basically backups of Wikipedia that are done monthly and that contain all the articles that exist.
The system analyses the dumps searching for articles that correspond to books, for that purpose it search for the existance of the "Infobox Book" template that is common among all book articles. Nonetheless, since the amount of data that is has to process is so large, it can take around 10 hours to finish. The final result is a JSON file containing all the information corresponding of each book article.

## Recomendation System
The recommendation system used is based on the hypothesis that a good way of determining the similarity between books is considering the common wikilinks between their corresponding Wikipedia article. Such idea has proven to be sucessful (e.g. [here](http://www.aaai.org/Papers/Workshops/2008/WS-08-15/WS08-15-005.pdf)) and has been used as the foundations for state of the art tools for semantic related algorithms, such as [WikiBrain](http://shilad.github.io/wikibrain).

### Entity Embeddings
In order to be able to make recommendations, we want to map each book to a position in a vector space, where books that are near in the space correspond to books that are similar. For that purpose, we will build a low dimensional learned representation of the data. This way, instead of having a one-hot encoding with as many dimensions as books, we will map them to a new dimension where distance has meaning.
To build the embeddings we use a Neural Network. Although there are plenty of resources about how to approach such task, the idea is to train the network with thousands of examples of pairs (link,book) and it will try to predict if such link appears in a given book.. Finally the weights of the network will correspond to the embeddings.
Once that we have a representation of books as embeddings, we normalize so that the dot product between two embeddings becomes the cosine similarity. Hence, in order to find similar books we can just find the books with the most cosine similarity.

## Web Application
The web application is based on a Flask server that serves the web content, do all the book related processing, and calls the recommendation system to make use of the recommendations in the web.

The server uses the model that previously already trained for the recommendation system for showing other books that might be similar to the book that the user is checking. Moreover, it allows the user to explore also those books (as well as their corresponding Wikipedia page) and keep finding further recommendations. Although the recommendations are fundamental for book exploration, they are only an small building block of the app. To offer a valuable experience to the user the server makes much more work related with showing information about each book, associations, images, links, etc. For that purpose, it makes use of a combination of the information that was extracted by the scrapper, together with some custom and real time requests using Wikipedia's API. 

### Cleaning and Filtering
Due to the unstructured and informal structure of much of the information in Wikipedia, a significant part of the application is devoted to making it more fault tolerant and exploring alternatives ways of finding missing information. For instance, something so simple as the year of a book might be missing in the infobox of an article, encoded in a different format or even contain comments that are only visible in the source code. Similar and bigger issues arise and basically every piece of information.

### Perfomance Enhancements
It is common to serve information related with the a book that was previously checked. Based on this idea, the server implements a caching system so that missing information of a given book does not need to be fetched twice if the same book is served again, what results in big performance improvements in particular when doing things such as page reloading or exploring related books.

Relying on Wikpedia's API is often slow, what makes hard to offer a fluid experience to the user. However, sometimes it is very important to use it, in particular when some information is missing. For that purpose, the system has been developed in such a way that for the main book that is being checked it spend a fair amount of time searching for information, while for book recommendations and other books it follows a best effort approach, were books whose related information cannot be retrieved quickly are discarded in order to offer a fluent experience.

Finally, the images of the webpage are loaded asynchronously in order to offer a more fluid experience.

## Plugin
In addition to the described functionalities, an experimental web plugin has been developed in order to be able to access to the web through Wikipedia. At this stage of development it can be run through Greasemonkey in Firefox. The associated code is in the folder "/plugin".

<p align="center">
<img src="https://i.imgur.com/xwmDq4N.png" width="75%">
</p>

## Code Structure
The system is composed of several programs. The program "fetch_wikipedia_books.py" corresponds to the processing of Wikipedia's Dump and generated a JSON file with all the books. Secondly, the program "generate_embeddings.py" uses the previously generated JSON file to generate a dataset of pairs of links and articles and uses them to train a Neural Network and finally generate the embeddings. Finally, the web application is contained in the folder "webapp". Such folder, on the one hand has all the HTML, CSS and JS used for the web. And on the other hand it contains the sever app in "app.py" which initially loads in memory information about books and the embeddings, and then it uses such information in combination with many other functions to serve the data that the user requests.

### Deployment
The deployment is simple considering the previous explanation about code structure. First run "/fetch_books/fetch_books.py" to generate the JSON file, then "/embeddings/generate_embeddings.py" and finally "app.py" to run the application. However, since the two initial steps should only be done once and they are very time consuming, in order to deploy the page is enough to simply run "app.py", unless that the dataset of books is updated.

### Dependencies
In order to execute the system is it necessary to have Python 3.6+ and the packages listed at the beggining of each script .
