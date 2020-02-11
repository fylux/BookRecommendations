# Book Recommendations
The goal of this project is to provide book recommendations in an useful way. For that purpose, the recommendations are integrated in a web application allowing users to explore books and authors, taking advantage of recommendations as well as by enhancing the information about the books with information extracted from Wikimedia. The project is composed of three main parts.
 - Scraping and grouping information about books.
 - Training of a Neural Network for book recommendations.
 - Exposing book related information in a web application.
 
## Book Scraping


## Recomendation System
The recommendation system used is based on the hypothesis that a good way of determining the similarity between books is considering the common link between their corresponding Wikipedia article. Such idea has proven to be sucessful (e.g. [here](http://www.aaai.org/Papers/Workshops/2008/WS-08-15/WS08-15-005.pdf)) and has been used as the foundations for state of the art tools for semantic related algorithms, such as [WikiBrain](http://shilad.github.io/wikibrain)


## Web Application
The web application is based on a Flask server that serves the web content, do all the book related processing, and calls the recommendation system to make use of the recommendations in the web.

The server uses the model that previously already trained for the recommendation system for showing other books that might be similar to the book that the user is checking. Moreover, it allows the user to explore also those books (as well as their corresponding Wikipedia page) and keep finding further recommendations. Although the recommendations are fundamental for book exploration, they are only an small building block of the app. To offer a valuable experience to the user the server makes much more work related with showing information about each book, associations, images, links, etc. For that purpose, it makes use of a combination of the information that was extracted by the scrapper, together with some custom and real time requests using Wikipedia's API. 

### Cleaning and Filtering
Due to the unstructured and informal structure of much of the information in Wikipedia, a significant part of the application is devoted to making it more fault tolerant and exploring alternatives ways of finding missing information. For instance, something so simple as the year of a book might be missing in the infobox of an article, encoded in a different format or even contain comments that are only visible in the source code. Similar and bigger issues arise and basically every piece of information.

### Perfomance Enhancements
It is common to serve information related with the a book that was previously checked. Based on this idea, the server implements a caching system so that missing information of a given book does not need to be fetched twice if the same book is served again, what results in big performance improvements in particular when doing things such as page reloading or exploring related books.

Relying on Wikpedia's API is often slow, what makes hard to offer a fluid experience to the user. However, sometimes it is very important to use it, in particular when some information is missing. For that purpose, the system has been developed in such a way that for the main book that is being checked it spend a fair amount of time searching for information, while for book recommendations and other books it follows a best effort approach, were books whose related information cannot be retrieved quickly are discarded in order to offer a fluent experience.

Finally, the images of the webpage are loaded asynchronously in order to offer a more fluid experience.

## Technologies
This project is mostly based on Python, in particular for all the aspects related scraping and machine learning. However, the web application makes use of specific web technologies such as HTML and CSS. Regarding the libraries that have been used, for scraping relies mostly on [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) together with some parsing utilies. The recommendation system is built using [Keras](https://github.com/keras-team/keras) and [Tensorflow](https://github.com/tensorflow/tensorflow). Finally, the web server is based on [Flask](https://github.com/pallets/flask).

## Code Structure

## Deployment

<!--
A minimal documentation (README file) should be provided to explain thegoal of the project, the structure of the code, the dependencies, and how to deploy and run thesystem
-->
