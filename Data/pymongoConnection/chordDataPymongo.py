from pymongo import MongoClient
import os

client = MongoClient(os.environ['MSC_CHORD_DB_URI'])

db = client.jamendo.chords