#!/usr/bin/python
# Change the above comment to the python interpreter location
import cgitb, cgi
import os
import json

DOCS_PATH = 'static'

# path to the directory containing the documents
cgitb.enable()

print('Content-type: text/html\n')

def openJson(fileName):
    with open(fileName) as jsonFile:
        return json.load(jsonFile)

def sortKey(key):
    # Function to sort the documents based on their tfidf score
    score = 0
    for word in userInputWords:
        dataWord = wordsData[key].get(word)
        if dataWord:
            score += dataWord['tfidf']
    scoreData[key] = score
    return score * pageRankData[key]

def pageData(file):
    with open(os.path.join(DOCS_PATH, file), encoding="utf-8", errors='backslashreplace') as document:
        return document.read()

form = cgi.FieldStorage()
# Collect attributes from the url (GET request)
query = form.getfirst('query', None)
queryType = form.getfirst('type', None)

if query and queryType: 
    # if the user is searching 
    query = query.lower()
    userInputWords = query.split()
    scoreData = {}
    wordsData = openJson('tfidf.json')
    pageRankData = openJson('pagerank.json')
    pageIndex = openJson('index.dat')
    # sort the documents based of the tfidf score
    sortedResults = sorted(wordsData, key=sortKey, reverse=True)
    finalResult = []
    # removes the documents without the query term from results
    for sortedResult in sortedResults:
        if scoreData[sortedResult] != 0:
            finalResult.append(sortedResult)
    
    if not finalResult:
        print("No Results Found")
    else:
        finalResult = finalResult[:25]
        if queryType == 'search':
            # returns the list of links to the document if search button is clicked
            for index, result in enumerate(finalResult, start=1):
                resultElement = f'''<div style="padding: 10px;border-bottom: 1px solid black;">
                <h3 style="margin: 2px;">{pageIndex[result][1]}</h3>
                <p style="margin: 2px;">{pageIndex[result][0]}</p>
                <a href="{pageIndex[result][0]}">Go to page</a><br>
                </div>'''
                print(resultElement)
        elif queryType == 'lucky':
            # directly takes the user to the most approprite page if 'feeling lucky' is clicked
            if finalResult:
                print(pageData(finalResult[0]))
else:
    # user requests the homepage, with the seach input form
    with open('form.html', encoding="utf-8") as file:
        print(file.read())
