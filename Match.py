# Generates histograms of the frequency of noun phrases.
# Then compares histograms from two people to identify common elements.

import pandas as pd
from textblob import TextBlob

# Gets a list of strings from a CSV of search history data.
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
        >>> histogram(["test", ""])
        {'test': 1, '': 1}
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

# Same as histogram() but with each individual noun-phrase in a string.
def nounHistogram(l):
    phrases = []
    for s in l:
        if type(s) == str:
            phrases += TextBlob(s).noun_phrases

    # Some noun-phrase fragments or phrases with no personal meaning are not included.
    # i.e. "gmail" or "july"
    with open("/Users/danrs/Documents/Excluded.txt") as file:
        remove = list(map(str.strip, file.readlines()))
        file.close()

    return histogram([phrase for phrase in phrases if phrase not in remove])

# Sorts a dictionary histogram from highest frequency to lowest frequency. Also tracks the rank of the key.
def sortedHistogram(hist):
    out = {}
    keys = sorted(hist, key=hist.get, reverse=True)
    rank = 1
    for key in keys:
        out[key] = (rank, hist[key])
        rank += 1
    return out

# Returns the keys of the n most frequent elements in a histogram. Histogram does not need to be sorted.
def topN(hist, n):
    return sorted(hist, key=hist.get, reverse=True)[:n]

# Matches two people if they a common element in their top [depth] elements.
def isMatch(hist1, hist2, depth):
    """
        >>> parker = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/chrome_history.csv")
        >>> tej = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/tej_history.csv")
        >>> parker = nounHistogram(parker)
        >>> tej = nounHistogram(tej)
        >>> isMatch(parker, tej, 20)
        [('youtube', 341, 586), ('stack overflow', 138, 144)]
        >>> isMatch(parker, tej, 50)
        [('youtube', 341, 586), ('zoom', 159, 83), ('stack overflow', 138, 144), ('homework', 108, 59)]
    """
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

# Find the top [number] matches between two people, or less if there aren't enough matches.
# If hist1 is the current user and hist2 is the other user, the output is a string of each match's title and rank
# in the other user's history.
def match(hist1, hist2, number):
    """
        >>> parker = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/chrome_history.csv")
        >>> tej = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/tej_history.csv")
        >>> parker = sortedHistogram(nounHistogram(parker))
        >>> tej = sortedHistogram(nounHistogram(tej))
        >>> match(parker, tej, 10)
        'youtube (2), stack overflow (18), zoom (37), homework (45), amazon.com (65), onedrive (70), google photos (55), agar.io (46), devpost (62), linkedin (19)'
    """
    matches = []
    shorter, longer = (hist1, hist2) if len(hist1) < len(hist2) else (hist2, hist1)
    for key in shorter:
        if key in longer:
            matches.append((key, hist1[key], hist2[key]))

    matches = sorted(matches, key=lambda x: x[1][0] + x[2][0])[:number]
    return ", ".join([x[0] + " (" + str(x[2][0]) + ")" for x in matches])
