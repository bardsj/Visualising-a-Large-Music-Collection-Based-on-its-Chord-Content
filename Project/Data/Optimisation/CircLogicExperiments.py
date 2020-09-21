from CircularGraphLogic import AVSDF,BaurBrandes,OptimiserBase
from pymongo import MongoClient
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import json

"""

url_chord = os.environ['MSC_CHORD_DB_URI']
client_chord = MongoClient(url_chord)
col_chord = client_chord.jamendo.chords

url_meta = os.environ['MSC_MONGO_PERSONAL_URI']
client_meta = MongoClient(url_meta)
col_meta = client_meta.jamendo.itemsetData

default_order = ["Cmaj","Cmaj7","Cmin","Cmin7","C7", \
        "Dbmaj","Dbmaj7","Dbmin","Dbmin7","Db7",
        "Dmaj","Dmaj7","Dmin","Dmin7","D7",
        "Ebmaj","Ebmaj7","Ebmin","Ebmin7","Eb7",
        "Emaj","Emaj7","Emin","Emin7","E7",
        "Fmaj","Fmaj7","Fmin","Fmin7","F7",
        "Gbmaj","Gbmaj7","Gbmin","Gbmin7","Gb7",
        "Gmaj","Gmaj7","Gmin","Gmin7","G7",
        "Abmaj","Abmaj7","Abmin","Abmin7","Ab7",
        "Amaj","Amaj7","Amin","Amin7","A7",
        "Bbmaj","Bbmaj7","Bbmin","Bbmin7","Bb7",
        "Bmaj","Bmaj7","Bmin","Bmin7","B7"
        ]

# Get itemsets for all genre graph
sets = col_meta.find_one({"tag_params.tag_val":"jazz","fi_type":"frequent"})['itemsets']
# Get length 2 sets for circular graph
doubletons = [x[1] for x in sets['items'].items() if len(x[1]) == 2]

res = []
time_ind = [10,50,100,150,200,250,300,350]

for x in time_ind:
    sample = np.random.randint(0,349,x)

    # Get number of crossings w/ default node order
    ob = OptimiserBase(np.array(doubletons)[sample])
    ob.order = default_order
    default_cross = ob._count_all_crossings(ob.order,ob.edge_list)

    # No local adjusting
    st_1 = time.time()
    av_nola = AVSDF(np.array(doubletons)[sample])
    av_nola.run_AVSDF()
    time_res_no_la = time.time()-st_1
    cross_nola = av_nola._count_all_crossings(av_nola.order,av_nola.edge_list)

    # w/ local adjusting
    st_2 = time.time()
    av_la = AVSDF(np.array(doubletons)[sample],local_adjusting=True)
    av_la.run_AVSDF()
    time_res_la = time.time()-st_2
    cross_la = av_la._count_all_crossings(av_la.order,av_la.edge_list)

    # No local adjusting
    st_3 = time.time()
    bb_nola = BaurBrandes(np.array(doubletons)[sample])
    bb_nola.run_bb()
    time_res_no_la_bb = time.time()-st_3
    cross_nola_bb = bb_nola._count_all_crossings(bb_nola.order,bb_nola.edge_list)

    # w/ local adjusting
    st_4 = time.time()
    bb_la = BaurBrandes(np.array(doubletons)[sample],local_adjusting=True)
    bb_la.run_bb()
    time_res_la_bb = time.time()-st_4
    cross_la_bb = bb_la._count_all_crossings(bb_la.order,bb_la.edge_list)

    res.append({
        "avsdf_time_no_la":time_res_no_la,
        "avsdf_time_la":time_res_la,
        "avsdf_cross_nola":cross_nola,
        "avsdf_cross_la":cross_la,
        "bb_time_no_la":time_res_no_la_bb,
        "bb_time_la":time_res_la_bb,
        "bb_cross_nola":cross_nola_bb,
        "bb_cross_la":cross_la_bb,
        "cross_default":default_cross,
        "n":x
    })

with open("Project/Data/Optimisation/avsdf_results.json","w") as filename:
    json.dump(res,filename)

"""

with open("Project/Data/Optimisation/avsdf_results.json","r") as filename:
    data = json.load(filename)

n = [x['n'] for x in data]
avsdf_time_no_la = [x['avsdf_time_no_la'] for x in data]
avsdf_time_la = [x['avsdf_time_la'] for x in data]
avsdf_cross_nola = [x['avsdf_cross_nola'] for x in data]
avsdf_cross_la = [x['avsdf_cross_la'] for x in data]
bb_time_no_la = [x['bb_time_no_la'] for x in data]
bb_time_la = [x['bb_time_la'] for x in data]
bb_cross_nola = [x['bb_cross_nola'] for x in data]
bb_cross_la = [x['bb_cross_la'] for x in data]
default_cross = [x['cross_default'] for x in data]

plt.figure(figsize=(7,5))
plt.scatter(n,avsdf_time_no_la,marker='s',label='AVSDF')
plt.scatter(n,avsdf_time_la,marker='x',label='AVSDF (with local adjusting)')
plt.scatter(n,bb_time_no_la,marker='^',label='Baur Brandes')
plt.scatter(n,bb_time_la,marker='D',label='Baur Brandes (with local adjusting)')
plt.xlabel("Number of graph edges")
plt.ylabel("Calculation time (seconds)")
plt.legend()
plt.show()

plt.figure(figsize=(7,5))
plt.scatter(n,avsdf_cross_nola,marker='s',label='AVSDF')
plt.scatter(n,avsdf_cross_la,marker='x',label='AVSDF (with local adjusting)')
plt.scatter(n,bb_cross_nola,marker='+',label='Baur Brandes')
plt.scatter(n,bb_cross_la,marker='D',label='Baur Brandes (with local adjusting)')
plt.scatter(n,default_cross,marker='o',label='Root node ordering')
plt.xlabel("Number of graph edges")
plt.ylabel("Total number of edge crossings")
plt.legend()
plt.show()