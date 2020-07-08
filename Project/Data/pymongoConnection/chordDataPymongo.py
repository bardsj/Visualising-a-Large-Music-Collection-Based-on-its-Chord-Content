from pymongo import MongoClient
import os
import matplotlib.pyplot as plt

client = MongoClient(os.environ['MSC_CHORD_DB_URI'])

db = client.jamendo.chords

dist_sample = []

for doc in db.find({}).limit(10000):
    dist_sample += list(doc['chordRatio'].values())


plt.hist(dist_sample,bins=100)
plt.show()