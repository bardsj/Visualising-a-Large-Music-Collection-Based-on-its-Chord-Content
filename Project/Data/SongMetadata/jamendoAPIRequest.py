from pymongo import MongoClient
import requests
import time
import os
import pickle

# Cursor to collection of chords documents
client = MongoClient(os.environ['MSC_CHORD_DB_URI'])
db = client.jamendo.chords

class DBGen():
    """
        Generator like class to take n id vals from mongodb and format as string to pass to API request params
    """
    def __init__(self,db):
        # Current cursor position
        self.n = 0
        # db cursor
        self.d = db.find()
        # total n documents in collection
        self.d_n = db.count_documents({})
        # set to false when end of collection reached
        self._finish_flag = True

    def take(self,num):
        vals = []
        if self.n+num <= self.d_n:
            for i in range(self.n,self.n+num):
                vals.append(str(self.d[i]['_id']))
        else:
            for i in range(self.n,self.d_n-self.n):
                vals.append(str(self.d[i]['_id']))
        vals = " ".join(vals)
        self.n += num
        return vals

dbg = DBGen(db)

res = []

st = time.time()

i = 0

while True:
    i += 1
    id_list = dbg.take(50)
    if len(id_list) > 0:
        time.sleep(0.05)
        request_params = {"client_id":os.environ['JAMENDO_CLIENT_ID'],"limit":50,"id":id_list,"include":"musicinfo"}
        r = requests.get("https://api.jamendo.com/v3.0/tracks/",params=request_params)
        res += r.json()['results']
    else:
        break
    if i > 2000:
        print("Call number exceeds expected value - i = " + i)

print(time.time()-st)

with open("jamendo_api_scrape_test.pkl","wb+") as filename:
    pickle.dump(res,filename)