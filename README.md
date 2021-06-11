#  An attempt to understand how search engines sort the results on the results page. 

*prototype*

1. [`crawler.py`](crawler.py) script can be used to crawl through wikipedia articles starting from a `seedUrl`. 
2. The below values are  calculated from the cleaned data of the article webpage, These values can be used to determine how relevant a term is to a document and also how important the document itself is.
    - Term Frequency Inverse Document Frequency (TFIDF)
    - PageRank
  

___
### Reference 
- [Term Frequency Inverse Document Frequency](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Page Rank](https://en.wikipedia.org/wiki/PageRank)