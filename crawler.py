from urllib import request
from urllib.error import URLError
from urllib.parse import urlparse
from http.client import InvalidURL
import re
import os
import json
from fractions import Fraction
from math import isclose
import math
import string
import time

DOCS_PATH = 'static'

def saveMappings(mappingData, fileName):
    with open(fileName, 'w') as jsonFile:
        json.dump(mappingData, jsonFile)

def crawler(seedUrl, maxPages, saveDir, CrawlAlgo):
    """Crawls the web document at seedUrl and saves the files at saveDir
    with filenames as 0.html,1.html,2.html,.. and creates a file named index.dat
    at cwd, which list the mapping between URLs and the filenames.
    Args: 
        seedUrl (int): The url to start crawling from
        maxPages (int): The maximum number of pages to crawl
        SaveDir (str): The location to save the files at
        CrawlAlgo (str): Indicates the crawling algorithm to use [bfs or dfs], uses bfs by default"""
    
    try:
        os.mkdir(saveDir)
    except FileExistsError:
        pass

    def getHTMLBody(url):
        try:
            print(url)
            urlRequest = request.Request(url)
            urlResponse = request.urlopen(urlRequest)
            contentType = urlResponse.headers.get('Content-Type')
            if not contentType or 'text/html' not in contentType:
                return False
            return request.urlopen(urlRequest).read().decode('utf-8', errors='ignore')
        except (URLError, InvalidURL, ValueError):
            print('There was a connection error. trying the next url')
            return False
    
    def getHTMLTitle(pageBody):
        title = re.findall('<title>(.*?)</title>', pageBody)
        if title:
            return title[0]
        else:
            return 'Untitled' 

    def getAllUrls(page, defaultDomain, defaultScheme):
        foundUrls = re.findall(r'(?<=<a href=")[^"]*', page)
        for index, url in enumerate(foundUrls):
            parsedUrl = urlparse(url)
            if not parsedUrl.netloc:
                foundUrls[index] = defaultScheme + "://" + defaultDomain + url
        return foundUrls

    def saveFile(location, fileName, data):
        with open(os.path.join(location, fileName), 'w', errors='ignore') as file:
            file.write(data)
    
    def saveMappings(mappingData, fileName):
        with open(fileName, 'w') as jsonFile:
            json.dump(mappingData, jsonFile)

    def cleanLinksData(linkData, revUrlMap):
        set1 = set(linkData.keys())
        newLinkData = {}
        for key, value in linkData.items():
            commonLinks = set1.intersection(set(value))
            links = list(commonLinks)
            for index, link in enumerate(links):
                links[index] = revUrlMap[link]
            newLinkData[revUrlMap[key]] = links
        return newLinkData

    def revUrlMappings(urlMappings):
        revUrlMappings = {}
        for key, value in urlMappings.items():
            revUrlMappings[value[0]] = key
        return revUrlMappings

    def Process(maxPages, saveDir):
        capturedUrls = []
        capturedUrls.append(seedUrl)
        urlMappings = {}
        pageRankData = {}
        seenUrls = set()

        for pageNumber in range(maxPages):
            while True:
                if capturedUrls:
                    currentUrl = capturedUrls.pop(0)
                    testUrl = urlparse(currentUrl)
                    if not testUrl.path:
                        continue
                    while currentUrl in seenUrls:
                        currentUrl = capturedUrls.pop(0)
                    seenUrls.add(currentUrl)
                else:
                    break
                pageBody = getHTMLBody(currentUrl)
                time.sleep(1)
                if not pageBody:
                    continue
                else:
                    break
            urlMappings[f'{pageNumber}.html'] = [currentUrl, getHTMLTitle(pageBody)]
            saveFile(saveDir, f"{pageNumber}.html", pageBody)
            allOutLinks = getAllUrls(pageBody, testUrl.netloc, testUrl.scheme)
            pageRankData[currentUrl] = allOutLinks
            if CrawlAlgo == 'dfs':
                capturedUrls = allOutLinks + capturedUrls
            else:
                capturedUrls += allOutLinks
                
        revMappings = revUrlMappings(urlMappings)
        saveMappings(urlMappings, 'index.dat')
        pageRankData = cleanLinksData(pageRankData, revMappings)
        # saveMappings(revMappings, 'revindex.dat')
        return pageRankData
    
    return Process(maxPages, saveDir)

# End Of Crawler Code
# Page Rank Code

def getLinkData() -> tuple:
    def addToDict(theDict, key, value):
        if key in theDict:
            theDict[key].append(value)
        else:
            theDict[key] = [value]

    # Creating two dictionaries
    # nodes:outlinks, nodes:inlinks
    inlinkData = {} # links pointing to a node -> {node: [nodes pointing in]}
    outlinkData = pageRankData  # links pointing out of a node -> {node: [nodes pointing out]}
    allNodes = set() # set will all the nodes 

    for key, value in outlinkData.items():
        for item in value:
            addToDict(inlinkData, item, key)
            allNodes.add(item)
            allNodes.add(key) 

    return inlinkData, outlinkData, allNodes 

def dictsAreClose(d1, d2):
    # Function to check if two dictionaries are the same\ 
    # after rounding off
    for key, value in d1.items():
        if not isclose(d2[key], value):
            return False
    return True

def calcDictFraction(d1):
    # Function to get the float from dict values which are Fraction objects
    # This function is not needed if the final Dict doesn't need to be printed 
    for key, value in d1.items():
        d1[key] = round(value.numerator/ value.denominator, 7)
    return d1

def calcRank(rankDict, totalNodes, p=Fraction('0.2'), counter=0):
    # Function to calculate a new cycle of ranks from a dictionary of ranks
    # Function is called recursively to calculate each cycle
    # counter variable in the param counts the number of cycles 
    newRank = {}
    for node in rankDict:
        voteSum = 0
        # Implementation of the equation
        # p / n + ((1 - p) * sum(ri/di)) 
        for inlink in inlinkData.get(node, []):
            inlinkOutlinkLength = len(outlinkData.get(inlink, []))
            inlinkRank = rankDict[inlink]
            currentLinkRank = Fraction(inlinkRank) / Fraction(inlinkOutlinkLength)
            voteSum += currentLinkRank
        # Probability that the user opens a random webpage
        randomProb = p / Fraction(totalNodes) 
        # Probability that the user follows a link to a webpage
        linkProb = (1 - p) * voteSum
        newRank[node] = randomProb + linkProb
    
    # Returns the final two dicts(if needed for debug, can be ignored)\ 
    # and the counter variable, once the match is found the call stack\
    # collapses and the required data is returned
    if dictsAreClose(newRank, rankDict):
        return calcDictFraction(rankDict), rankDict, counter
    return calcRank(newRank, totalNodes,p=p,counter=counter+1)
    # Counter is incremented in each recursive function call


def cleanWords(words):
    # function that removes unwanted words from a list of words
    # and remove unwanted characters at the end/beginning of words 
    for index, word in enumerate(words):
      words[index] = word.strip('.,"')
    words = [word for word in words if wordsFilter(word)]
    return words

def wordsFilter(word):
    # helper function to check if a word is an html remnant
    if len(word) > 45:
        return False
    for letter in word:
        if letter in (string.punctuation + "•–"):
            return False
    return True

def processHTML(cleantext):
    # function to remove html tags and entities
    # (slices the string to use only the wikipedia content div)
    start = cleantext.find('<div id="content"')
    end = cleantext.find("<div id='mw-data-after-content'>")
    if start != -1 and end != -1:
        cleantext = cleantext[start: end]
    cleanReg = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanReg, '', cleantext).lower()
    return cleanWords(cleantext.split())

def getTermFreqency():
    # calculate the frequency of terms in each document. Term Frequency (TF)
    # returns a dictionary containing the data
    termFrequency = {} # Structure -> documentName: {word: frequency}
    for file in os.listdir(DOCS_PATH):
        filePath = os.path.join(DOCS_PATH, file)
        with open(filePath, encoding="utf-8", errors='ignore') as document:
            termFrequency[file] = {}
            cleanedDocument = processHTML(document.read())
            for word in cleanedDocument:
                if word in termFrequency[file]:
                    termFrequency[file][word] += 1
                else:
                    termFrequency[file][word] = 1
    return termFrequency

def getWordsData(termFrequency):
    # Uses the data from termFrequency and calculates documents Frequency (DF)
    # calculates TFIDF from TF and DF 
    # returns dictionary contains terms and tfidf
    docCount = len(termFrequency)
    wordsData = {}
    for document, words in termFrequency.items():
        wordsData[document] = {}
        for word in words:
            wordsData[document][word] = {'tf': words[word]}
            dfCounter = 0
            for values in termFrequency.values():
                if word in values:
                    dfCounter += 1
            wordsData[document][word]['df'] = dfCounter
            wordsData[document][word]['tfidf'] = words[word] / math.log10(docCount/ dfCounter + 1)
    return wordsData

pageRankData = crawler('https://en.wikipedia.org/wiki/Polish_language', 50, 'static', 'bfs')

inlinkData, outlinkData, allNodes = getLinkData()
totalNodes = len(allNodes)
rankDict = dict.fromkeys(allNodes, Fraction(1) / Fraction(totalNodes))
finalDictRounded, finalDict, cycles = calcRank(rankDict, totalNodes, p=Fraction('0.2'))
termFrequency = getTermFreqency()
wordsData = getWordsData(termFrequency)

saveMappings(finalDictRounded, 'pagerank.json')
saveMappings(wordsData, 'tfidf.json')
