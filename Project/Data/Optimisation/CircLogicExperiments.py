from CircularGraphLogic import AVSDF,BaurBrandes
from pymongo import MongoClient
import os
import time
import matplotlib.pyplot as plt
import numpy as np

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

time_res_no_la = []
time_res_la = []
time_ind = [10,50,100,150,200,250,300,350]

for x in time_ind:
    sample = np.random.randint(0,349,x)
    st_1 = time.time()
    AVSDF(np.array(doubletons)[sample]).run_AVSDF()
    time_res_no_la.append(time.time()-st_1)

    st_2 = time.time()
    AVSDF(np.array(doubletons)[sample],local_adjusting=True).run_AVSDF()
    time_res_la.append(time.time()-st_2)

plt.scatter(time_ind,time_res_no_la)
plt.scatter(time_ind,time_res_la)
plt.show()
