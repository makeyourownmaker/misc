#!/usr/bin/python
#
# https://github.com/sefakilic/goodreads/
# http://goodreads.readthedocs.io/en/latest/
# https://www.goodreads.com/api
# https://github.com/sefakilic/goodreads/blob/master/goodreads/book.py
#
# NEXT: add command line options for title/isbn
#       add a verbose option
#       clean up code
#       finalise ratings measure to use:
#         average_rating                                             Maybe
#         average_rating/pages                                       Maybe
#         average_rating*review_count/pages                          Nope
#         average_rating*sqrt(review_count)/pages                    Maybe
#         bayesian average taking into account the number of pages   Probably
#         or a variant like this: http://stackoverflow.com/a/1411455 

import sys
from math import sqrt
from datetime import date
from goodreads import client

gc = client.GoodreadsClient('<API Key>', '<API Secret>')

try:
    book = gc.book(isbn=str(sys.argv[1]))
except:
    print >>sys.stderr, "Missing isbn\t", sys.argv[1]
    exit()


# weighted rating (WR) = (v / (v+m)) * R + (m / (v+m)) * C
# where:
#   * R = average for the movie (mean) = (Rating)
#   * v = number of votes for the movie = (votes)
#   * m = minimum votes required to be listed in the Top 250 (currently 1300)
#   * C = the mean vote across the whole report (currently 6.8)
m = 50  # What is dis fudge factor?
C = 2.5 # What is dis fudge factor?
v = int(book.ratings_count)
R = float(book.average_rating)
bayes = round(R*v/(v+m) + m*C/(v+m), 4)

if book.num_pages == None:
    print >>sys.stderr, book.num_pages, "\t", book.title, "\tMissing num_pages"
    if book.title == "The Visual Display of Quantitative Information":
        book.num_pages = 200
    if book.title == "The Elements of Statistical Learning: Data Mining, Inference, and Prediction":
        book.num_pages = 552
    if book.title == "The New Media Reader [With CDROM]":
        book.num_pages = 839
    if book.title == "Racing the Beam: The Atari Video Computer System":
        book.num_pages = 180
    if book.title == "Nothing is True and Everything is Possible: Adventures in Modern Russia":
        book.num_pages = 304
    if book.title == "Deschooling Society":
        book.num_pages = 150
    if book.title == "An Introduction to Statistical Learning: with Applications in R (Springer Texts in Statistics)":
        book.num_pages = 430
    if book.title == "Machines Who Think: A Personal Inquiry Into the History and Prospects of Artificial Intelligence":
        book.num_pages = 576
    if book.title == "Terrible Beauty: A Cultural History of the Twentieth Century: The People and Ideas that Shaped the Modern Mind: A History":
        book.num_pages = 847
    if book.title == "Code Complete, 2ed":
        book.num_pages = 914


pub_year = book.publication_date[2]

if pub_year == None:
    print >>sys.stderr, pub_year, "\t", book.title, "\tMissing publication_date"
    if book.title == "The Way Things Work":
        pub_year = 1988
    if book.title == "The Elements of Statistical Learning: Data Mining, Inference, and Prediction":
        pub_year = 2001
    if book.title == "The New Media Reader [With CDROM]":
        pub_year = 2003
    if book.title == "Racing the Beam: The Atari Video Computer System":
        pub_year = 2009
    if book.title == "Deschooling Society":
        pub_year = 2000
    if book.title == "An Introduction to Statistical Learning: with Applications in R (Springer Texts in Statistics)":
        pub_year = 2013
    if book.title == "Terrible Beauty: A Cultural History of the Twentieth Century: The People and Ideas that Shaped the Modern Mind: A History":
        pub_year = 2000
    if book.title == "Code Complete, 2ed":
        pub_year = 1993

pub_year = int(pub_year)
now      = date.today().year
years    = now - pub_year

bayes_adj = round(bayes/int(book.num_pages), 4) # NOPE

# Do want to read old books, so encourage that
#bayes_adj = round(bayes*years/int(book.num_pages), 4) # Maybe?
#bayes_adj = round(bayes*sqrt(years)/int(book.num_pages), 4) # Maybe?

# Older books have had longer to acquire reviews, but only lightly penalise that
#bayes_adj = round(bayes/int(book.num_pages*years), 4) # NOPE
#bayes_adj = round(bayes/( int(book.num_pages)*sqrt(years) ), 4) # Maybe?
#bayes_adj = round(bayes/sqrt( int(book.num_pages)*years ), 4)   # Maybe?
#bayes_adj  = round(bayes/( int(book.num_pages)*sqrt(sqrt(years)) ), 4) # Maybe

print book.average_rating, "\t", pub_year, "\t", years, "\t", book.ratings_count, "\t", book.num_pages, "\t", bayes, "\t", bayes_adj, "\t", book.title.encode('utf-8')

exit()


#print "Pages\t",   book.num_pages
#print "Average\t", book.average_rating
#print "Ratings\t", book.ratings_count
#print "Reviews\t", book.text_reviews_count
#print "Dist\t",    book.rating_dist

#authors = book.authors
#print "Author\t", authors[0].name

