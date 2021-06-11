import sys
import json

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

wordsData = openJson('tfidf.json')
pageRankData = openJson('pagerank.json')
pageIndex = openJson('index.dat')

userInputWords = sys.argv[1:]
scoreData = {}
tfidfRank = {}
finalResult = []

sortedResults = sorted(wordsData, key=sortKey, reverse=True)
for sortedResult in sortedResults:
    if scoreData[sortedResult] != 0:
        finalResult.append(sortedResult)

print("The pageranks * tfidf based on the query")
count = 0
for key, value in scoreData.items():
    if count == 25:
        break
    count += 1
    print(f'{pageIndex[key][1]} - TFIDF: {value}, Pagerank: {pageRankData[key]}')
print()
print("The pages ordered based on the query")
count = 0
for item in finalResult:
    if count == 25:
        break
    count += 1
    print(pageIndex[item])

