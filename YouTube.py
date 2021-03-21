import urllib.parse
import html

def searchHistory(filePath):
    with open(filePath, encoding="utf8") as file:
        raw = file.readline()
        while raw[:8] != "</style>":
            raw = file.readline()
        file.close()

    queries = raw.split("query=")
    matchable = []
    for query in queries:
        query = query[:query.index('"')]
        query = " ".join(query.split("+"))
        matchable.append(urllib.parse.unquote(query))

    return matchable[1:]

def watchHistory(filePath):
    with open(filePath, encoding="utf8") as file:
        raw = file.readline()
        while raw[:8] != "</style>":
            raw = file.readline()
        file.close()

    queries = raw.split("</a>")
    matchable = []
    for query in queries:
        query = query[query.rindex('">') + 2:]
        matchable.append(html.unescape(query))

    return matchable[:-1]