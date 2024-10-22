"""
Get metadata for tracks in db -> save pkl file of results and write to free tier mongo cluster
"""
from pymongo import MongoClient
import requests
import time
import os
import pickle
import sys

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
        """
            Take num id values from the db and update the cursor index
        """
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
        try:
            request_params = {"client_id":os.environ['JAMENDO_CLIENT_ID'],"limit":50,"id":id_list,"include":"musicinfo"}
            r = requests.get("https://api.jamendo.com/v3.0/tracks/",params=request_params)
            r.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("Request exception:",err)
            sys.exit(1)
   
        res += r.json()['results']
        time.sleep(0.05)

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

# Rename id field to set mongodb id field
for r in res:
    r['_id'] = r.pop('id')

# Write to free mongo cluster
client_write = MongoClient(os.environ['MSC_MONGO_PERSONAL_URI'])

db_write = client_write['jamendo']

col = db_write['songMetadata']
col.insert_many(res)