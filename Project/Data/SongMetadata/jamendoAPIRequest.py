"""
Get metadata for tracks in db -> save pkl file of results and write to free tier mongo cluster
"""
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
    id_list = dbg.take(50)
    if len(id_list) > 0:
        time.sleep(0.05)
        request_params = {"client_id":os.environ['JAMENDO_CLIENT_ID'],"limit":50,"id":id_list,"include":"musicinfo"}
        r = requests.get("https://api.jamendo.com/v3.0/tracks/",params=request_params)
        res += r.json()['results']
    else:
        break
    # 99960 docs in collection - with 50 docs/request, should expect just short of 2000 requests 
    if i > 2000:
        print("Call number exceeds expected value - i = " + i)
    i += 1

print("Time elapsed: " + str(time.time()-st))

# Save pkl file with results
with open("Project/Data/SongMetadada/jamendo_api_scrape_test.pkl","wb+") as filename:
    pickle.dump(res,filename)

# Write to free mongo cluster
client_write = MongoClient(f"mongodb+srv://jamapi:{os.environ['MSC_MONGO_PERSONAL']}@msc.5jje5.gcp.mongodb.net/MSC?retryWrites=true&w=majority")

db_write = client_write['jamendo']

with open("Project/Data/SongMetadata/jamendo_api_scrape.pkl","rb") as filename:
    res = pickle.load(filename)

col = db_write['songMetadata']
col.insert_many(res)