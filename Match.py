import string
import pandas as pd

def csvList(filePath):
    hi = pd.read_csv(filePath)
    return hi.iloc[:,1].tolist()

# Returns a dictionary with string keys and integer values, the number of times the string appeared in the list.
def histogram(l):
    """
        >>> histogram(["test", "test", "test", "test", "Never", "gonna", "give", "you", "up", "never", "gonna", "let", "you", "down", "test"])
        {'test': 5, 'Never': 1, 'gonna': 2, 'give': 1, 'you': 2, 'up': 1, 'never': 1, 'let': 1, 'down': 1}
        >>> histogram(["test", "According to all known laws of aviation,", "there is no way a bee should be able to fly.", "test"])
        {'test': 2, 'According to all known laws of aviation,': 1, 'there is no way a bee should be able to fly.': 1}
        >>> histogram("test", "")
        >>> histogram([])
        {}
    """
    hist = {}
    for s in l:
        if s in hist:
            hist[s] += 1
        else:
            hist[s] = 1
    return hist

# Same as histogram() but with each individual noun in a string.
def nounHistogram(l):
    with open(r"/Users/danrs/Documents/Nouns.txt") as file:
        allNouns = set(map(str.strip, file.readlines()))
        file.close()

    nouns = []
    for s in l:
        if type(s) == str:
            for word in s.split():
                search = word.translate(str.maketrans('', '', string.punctuation)).strip().lower()
                # Dictionary does not include some plurals, remove 's' to check.
                if search and (search in allNouns or search[-1] == 's' and search[:-1] in allNouns):
                    nouns.append(search)

    return histogram(nouns)

def sortedHistogram(hist):
    out = {}
    keys = sorted(hist, key=hist.get)
    for key in keys:
        out[key] = hist[key]
    return out

# Returns the keys of the n frequent elements in a histogram.
def topN(hist, n):
    return sorted(hist, key=hist.get, reverse=True)[:n]

# Matches two people if they a common element in their top [depth] elements.
def match(hist1, hist2, depth):
    top1 = topN(hist1, depth)
    top2 = topN(hist2, depth)

    matches = []
    for item in top1:
        if item in top2:
            matches.append((item, hist1[item], hist2[item]))

    if matches:
        return matches
    else:
        return False