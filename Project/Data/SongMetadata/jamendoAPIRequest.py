from pymongo import MongoClient
import requests
import time
import os
import pickle

client = MongoClient(os.environ['MSC_CHORD_DB_URI'])

db = client.jamendo.chords

class DBGen():
    """
        Generator like class to take n id vals from mongodb and format as string to pass to API request params
    """
    def __init__(self,db):
        self.n = 0
        self.d = db.find()
        self.d_n = db.count_documents({})
        self.finish_flag = True

    def take(self,num):
        vals = []
        if self.n+num < self.d_n:
            for i in range(self.n,self.n+num):
                vals.append(str(self.d[i]['_id']))
        else:
            for i in range(self.n,self.d_n-self.n):
                vals.append(str(self.d[i]['_id']))
                self.finish_flag = False
        vals = " ".join(vals)
        self.n += num
        return vals

dbg = DBGen(db)

res = []

while dbg.finish_flag:
    id_list = dbg.take(50)
    n+= 1
    time.sleep(0.05)
    request_params = {"client_id":os.environ['JAMENDO_CLIENT_ID'],"limit":50,"id":id_list,"include":"musicinfo"}
    r = requests.get("https://api.jamendo.com/v3.0/tracks/",params=request_params)
    res += r.json()['results']

with open("Project/Data/SongMetadata/jamendo_api_scrape.pkl","wb+") as filename:
    pickle.dump(res,filename)