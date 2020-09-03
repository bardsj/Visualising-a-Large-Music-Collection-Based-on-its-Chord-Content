"""
Batch mine high utility itemsets based on params
"""
from pymongo import MongoClient
import os
import time
from FHM import FHM

url_chord = os.environ['MSC_CHORD_DB_URI']
client_chord = MongoClient(url_chord)
col_chord = client_chord.jamendo.chords

url_meta = os.environ['MSC_MONGO_PERSONAL_URI']
client_meta = MongoClient(url_meta)
col_meta = client_meta.jamendo.songMetadata

items_list = ['A7', 'Ab7', 'Abmaj', 'Abmaj7', 'Abmin', 'Abmin7', 'Amaj', 'Amaj7', 'Amin', 'Amin7', 'B7', 'Bb7', 'Bbmaj', 'Bbmaj7', 'Bbmin', 'Bbmin7', 'Bmaj', 'Bmaj7', 'Bmin', 'Bmin7', 'C7', 'Cmaj', 'Cmaj7', 'Cmin', 'Cmin7', 'D7', 'Db7', 'Dbmaj', 'Dbmaj7', 'Dbmin', 'Dbmin7', 'Dmaj', 'Dmaj7', 'Dmin', 'Dmin7', 'E7', 'Eb7', 'Ebmaj', 'Ebmaj7', 'Ebmin', 'Ebmin7', 'Emaj', 'Emaj7', 'Emin', 'Emin7', 'F7', 'Fmaj', 'Fmaj7', 'Fmin', 'Fmin7', 'G7', 'Gb7', 'Gbmaj', 'Gbmaj7', 'Gbmin', 'Gbmin7', 'Gmaj', 'Gmaj7', 'Gmin', 'Gmin7']
# Create external utility table but set all to one for now
external_utilities = {k:1 for k in items_list}

params = {"minUtil": 0.01,"filterRatio":0.05,"filterConfidence":0.6}

st = time.time()

write_results = []

for i,genre in enumerate(['pop','rock','electronic','hiphop','jazz','classical','ambient','folk','metal','latin','rnb','reggae','house','blues',None]):
    # Get valid ids based on metadata params
    if not genre:
        valid_ids = [int(d['_id']) for d in col_meta.find({})]
    else:
        valid_ids = [int(d['_id']) for d in col_meta.find({'musicinfo.tags.genres':genre})]
    # Get tracks based on 
    transactions = [(x['_id'],[y for y in x['chordRatio'].items() if y[1] > params['filterRatio']]) for x in col_chord.find({'_id':{'$in':valid_ids}}) if float(x['confidence']) > params['filterConfidence']]
    print(transactions[0])
    # Mine itemsets
    itemsets = FHM(transactions,external_utilities,minutil=params['minUtil']).run_FHM()
    count = len(transactions)
    # Convert to dict for storage
    itemsets = [{"itemset":i[0],"minutil":i[1]} for i in itemsets]

    write_results.append({
        "_id":str(i).zfill(4)+"-"+str(params['minutil'])+"-"+str(params['filterRatio'])+"-"+str(params['filterConfidence'])+"-"+str(majmin_agg)+"hui",
        "filter_params":params,
        "tag_params":tag_filt,
        "itemsets":itemsets,
        "majmin_agg":False,
        "dfCount":count,
        "fi_type":'hui'
    })


with open("Project/Data/pyspark/itemsets_hui.json","w+") as filename:
    json.dump(write_results,filename)

print("Total time: " + str(time.time()-st))