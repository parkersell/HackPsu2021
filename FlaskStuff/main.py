from flask import Flask
from flask import request
from firebase import firebase
from zipfile import ZipFile 
import json
import pandas as pd
import string
import math
import gdown
import urllib.parse
import html
from textblob import TextBlob
# from firebase_admin import credentials, initialize_app, storage
from google_drive_downloader import GoogleDriveDownloader as gdd


firebase = firebase.FirebaseApplication('https://learned-aria-308200-default-rtdb.firebaseio.com/', None)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    name1 = firebase.get('/link/', '')['name1']
    print(name1)
    name2 = "Parker"
    print(1)
    bhlist1, ytlist1 = getbh(name1)
    print(2)
    bhlist2, ytlist2 = getbh(name2)
    print(3)
    if firebase.get('/userINFO/', '')[name1].get("BHMatches") ==-1: # run it if BHMatches doesnt exist
        bhmatch = matchfunc(bhlist1, bhlist2)
        bhmatchlocation1 = 'userINFO/'+name1+'/BHMatches/'+name2+'/'
        bhmatchlocation2 = 'userINFO/'+name2+'/BHMatches/'+name1+'/'
        firebase.post(bhmatchlocation1,bhmatch, {'print': 'silent'}, {'X_FANCY_HEADER': 'VERY FANCY'}) #outputs to firebase
        firebase.post(bhmatchlocation2,bhmatch, {'print': 'silent'}, {'X_FANCY_HEADER': 'VERY FANCY'}) #outputs to firebase
    print(4)
    if firebase.get('/userINFO/', '')[name1].get("YTMatches") ==-1: # run it if BHMatches doesnt exist
        ytmatch = matchfunc(ytlist1, ytlist2)    
        ytmatchlocation1 = 'userINFO/'+name1+'/YTMatches/'+name2+'/'
        ytmatchlocation2 = 'userINFO/'+name2+'/YTMatches/'+name1+'/' 
        firebase.post(ytmatchlocation1,ytmatch, {'print': 'silent'}, {'X_FANCY_HEADER': 'VERY FANCY'}) #outputs to firebase
    
        firebase.post(ytmatchlocation2,ytmatch, {'print': 'silent'}, {'X_FANCY_HEADER': 'VERY FANCY'}) #outputs to firebase
    print(5)
    return "Check App, "+ name1 +" matched with " + name2 + " has loaded! "

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


def histogram(l):
#    """
#        >>> histogram(["test", "test", "test", "test", "Never", "gonna", "give", "you", "up", "never", "gonna", "let", "you", "down", "test"])
#        {'test': 5, 'Never': 1, 'gonna': 2, 'give': 1, 'you': 2, 'up': 1, 'never': 1, 'let': 1, 'down': 1}
#        >>> histogram(["test", "According to all known laws of aviation,", "there is no way a bee should be able to fly.", "test"])
#        {'test': 2, 'According to all known laws of aviation,': 1, 'there is no way a bee should be able to fly.': 1}
#        >>> histogram(["test", ""])
#        {'test': 1, '': 1}
#        >>> histogram([])
#        {}
#    """
    hist = {}
    for s in l:
        if s in hist:
            hist[s] += 1
        else:
            hist[s] = 1
    return hist

# Same as histogram() but with each individual noun in a string.
def nounHistogram(l):
    phrases = []
    for s in l:
        if type(s) == str:
            #s = s.translate(str.maketrans('', '', string.punctuation))
            #.strip().lower()
            phrases += TextBlob(s).noun_phrases

    with open("Excluded.txt") as file:
        remove = list(map(str.strip, file.readlines()))
        file.close()

    return histogram([phrase for phrase in phrases if phrase not in remove])

def sortedHistogram(hist):
    out = {}
    keys = sorted(hist, key=hist.get, reverse=True)
    rank = 1
    for key in keys:
        out[key] = (rank, hist[key])
        rank += 1
    return out

# Returns the keys of the n frequent elements in a histogram.
def topN(hist, n):
    return sorted(hist, key=hist.get, reverse=True)[:n]

# Matches two people if they a common element in their top [depth] elements.
def isMatch(hist1, hist2, depth):
 #   """
 #       >>> parker = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/chrome_history.csv")
 #       >>> tej = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/tej_history.csv")
 #       >>> parker = nounHistogram(parker)
 #       >>> tej = nounHistogram(tej)
 #       >>> isMatch(parker, tej, 20)
 #       [('youtube', 341, 586), ('stack overflow', 138, 144)]
 #       >>> isMatch(parker, tej, 50)
 #       [('youtube', 341, 586), ('zoom', 159, 83), ('stack overflow', 138, 144), ('homework', 108, 59)]
 #   """
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

# Find the top [number] matches.
def match(hist1, hist2, number):
    # """
    #     >>> parker = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/chrome_history.csv")
    #     >>> tej = csvList("C:/Users/danrs/Documents/GitHub/HackPsu2021/tej_history.csv")
    #     >>> parker = sortedHistogram(nounHistogram(parker))
    #     >>> tej = sortedHistogram(nounHistogram(tej))
    #     >>> match(parker, tej, 100)
    #     ['youtube', 'stack overflow', 'zoom', 'homework', 'amazon.com', 'onedrive', 'google photos', 'agar.io', 'devpost', 'linkedin', 'steam', 'inbox', 'video', 'edition', 'wikipedia', 'geeksforgeeks', 'google docs', 'exam', 'submission', 'find', 'outlook', 'probability', 'hackpsu', 'fandom', 'microsoft', 'penn', 'free', 'solved', 'pennsylvania', 'jbtv', 'determine', 'midterm', 'quora', 'overview', 'welcome', 'event', '’ s', 'profile', 'starve wiki', 'groupme', 'paypal', 'build', 'github', 'create', 'share', 'symbolab', 'netflix', 'working', 'python', 'modules', 'project', 'photos', 'settings', 'electronics', 'online', 'java', 'engineering', 'learn', 'software portfolio |', 'discussions', 'consider', 'edit', 'photo', 'schedule', 'hacking', 'c++', 'black', 'dc', 'data', 'towards data', 'google takeout', 'mathematics stack', 'page', 'videos', 'tixr', 'log', 'pa', 'discord', 'computer engineering', 'songkick', 'google calendar', 'agar.yt', 'chegg.com', 'windows', 'code', 'hw', 'examples', 'grades', 'dell usa', 'hero', 'keshav majithia', 'calendar', 'twitter', 'tickets', 'announcements', 'guide', 'computers', 'checkout', 'tutorialspoint', 'hackpsu opening ceremony']
    # """
    matches = []
    shorter, longer = (hist1, hist2) if len(hist1) < len(hist2) else (hist2, hist1)
    for key in shorter:
        if key in longer:
            matches.append((key, hist1[key], hist2[key]))

    matches = sorted(matches, key=lambda x: x[1][0] + x[2][0])[:number]
    return ", ".join([x[0] + " (" + str(x[2][0]) + ")" for x in matches])
    # return matches 
def matchfunc(bhlist1, bhlist2):
    sh1 = sortedHistogram(nounHistogram(bhlist1))
    sh2 = sortedHistogram(nounHistogram(bhlist2))
    return match(sh1, sh2, 10)

def getbh(name):
    
    result = firebase.get('/zip/', '')
    # print(result)
    # person = 
    # age = str(list(person.keys())[0])
    # phone = str(list(person[age].keys())[0])
    realfilename = result[name]
    # print(realfilename)
    # Init firebase with your credentials

    #### Put your local file path 
    ####bucket = storage.bucket()
    ####blob = bucket.blob(realfilename)
    ####my_blob = Blob.from_string("gs://learned-aria-308200.appspot.com/zip/"+realfilename)
    ####print(my_blob)
    realfilename = realfilename.replace("\\", "")
    # print(realfilename)
    dindex = realfilename.index('/d/')+3
    viewindex = realfilename.index('/view')
    driveid = realfilename[dindex: viewindex]
    # print(driveid)
    gdd.download_file_from_google_drive(file_id=driveid,
                                    dest_path=''+name+'/Takeout/Chrome/BrowserHistory.json',
                                    unzip=True)
    bhf = open(name+"/Takeout/Chrome/Takeout/Chrome/BrowserHistory.json", encoding="utf8")
    ytsearch = searchHistory(name+"/Takeout/Chrome/Takeout/YouTube and YouTube Music/history/search-history.html")
    ytwatch = watchHistory(name+"/Takeout/Chrome/Takeout/YouTube and YouTube Music/history/watch-history.html")
    yttotal = ytsearch + ytwatch
    bhjson =json.load(bhf) #json file
    dataframe = pd.DataFrame.from_dict(bhjson["Browser History"])
    bhlist = dataframe["title"].tolist() ## turns into list
    return bhlist, yttotal

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)


