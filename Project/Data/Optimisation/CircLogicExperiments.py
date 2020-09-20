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

    res.append({
        "time_no_la":time_res_no_la,
        "time_la":time_res_la,
        "cross_nola":cross_nola,
        "cross_la":cross_la,
        "cross_default":default_cross,
        "n":x
    })

with open("Project/Data/Optimisation/avsdf_results.json","w") as filename:
    json.dump(res,filename)

"""

with open("Project/Data/Optimisation/avsdf_results.json","r") as filename:
    data = json.load(filename)

n = [x['n'] for x in data]
time_no_la = [x['time_no_la'] for x in data]
time_la = [x['time_la'] for x in data]
cross_nola = [x['cross_nola'] for x in data]
cross_la = [x['cross_la'] for x in data]
default_cross = [x['cross_default'] for x in data]

plt.scatter(n,time_no_la,marker='s',label='AVSDF')
plt.scatter(n,time_la,marker='x',label='AVSDF (with local adjusting)')
plt.xlabel("Number of graph edges")
plt.ylabel("Calculation time (seconds)")
plt.legend()
plt.show()


plt.scatter(n,cross_nola,marker='s',label='AVSDF')
plt.scatter(n,cross_la,marker='x',label='AVSDF (with local adjusting)')
plt.scatter(n,default_cross,marker='o',label='Root node ordering')
plt.xlabel("Number of graph edges")
plt.ylabel("Total number of edge crossings")
plt.legend()
plt.show()