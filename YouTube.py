# Retrieves relevant data from the YouTube search history or watch history .html files of the Google Takeout .zip file.

import urllib.parse
import html

# Returns a list of string data points from the search-history.html file of a user's YouTube data.
def searchHistory(filePath):
    # Getting the important data from the bottom of the html file.
    with open(filePath, encoding="utf8") as file:
        raw = file.readline()
        while raw[:8] != "</style>":
            raw = file.readline()
        file.close()

    # Splitting the html file to get the search data, raw looks like: '...query=search+text+here"...'
    queries = raw.split("query=")
    matchable = []
    for query in queries:
        query = query[:query.index('"')]
        query = " ".join(query.split("+"))
        matchable.append(urllib.parse.unquote(query))

    return matchable[1:]

# Returns a list of string data points from the watch-history.html file of a user's YouTube data.
def watchHistory(filePath):
    with open(filePath, encoding="utf8") as file:
        raw = file.readline()
        while raw[:8] != "</style>":
            raw = file.readline()
        file.close()

    # Splitting the html file to get the video title, raw looks like: '...">video title here</a>...'
    queries = raw.split("</a>")
    matchable = []
    for query in queries:
        query = query[query.rindex('">') + 2:]
        matchable.append(html.unescape(query))

    return matchable[:-1]