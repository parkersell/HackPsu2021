from flask import Flask
from flask import request
from firebase import firebase
from zipfile import ZipFile 
import json
import pandas as pd


firebase = firebase.FirebaseApplication('https://learned-aria-308200-default-rtdb.firebaseio.com/', None)

app = Flask(__name__)

@app.route("/")
def index():
    # get this using parameters aka ?test1
    # have a value called recent in firebase and access that is the name
    # need to know users name to get out of result
    name = "test1"
    
    result = firebase.get('/userINFO/', '')
    
    
    person = result[name]
    age = str(list(person.keys())[0])
    phone = str(list(person[age].keys())[0])
    zipfilename = str(list(person[age][phone].keys())[0])
    file_name = "takeout-20210320T182524Z-001.zip"
    realfilename = person[age][phone][zipfilename]

    file_name = "takeout-20210320T182524Z-001.zip"
    zip = ZipFile(file_name)
    zip.extractall()
    f = open("Takeout/Chrome/BrowserHistory.json" , encoding="utf8")
    hi =json.load(f)
    dataframe = pd.DataFrame.from_dict(hi["Browser History"])
    bhlist = dataframe["title"].tolist() ## feed to daniels code
    match = bhlist[0]
    matchlocation = '/userINFO/'+name+'/'
    result = firebase.post(matchlocation,match)
    return matchlocation

# Returns a dictionary with string keys and integer values, the number of times the string appeared in the list.
 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)


