"""
Plot circular logic results
"""
from CircularGraphLogic import AVSDF,BaurBrandes,OptimiserBase
from pymongo import MongoClient
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import json
from scipy.stats import sem
import pandas as pd

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


res = []

url_chord = os.environ['MSC_CHORD_DB_URI']
client_chord = MongoClient(url_chord)
col_chord = client_chord.jamendo.chords

url_meta = os.environ['MSC_MONGO_PERSONAL_URI']
client_meta = MongoClient(url_meta)
col_meta = client_meta.jamendo.itemsetData

genres = [None,'pop', 'rock', 'electronic', 'hiphop', 'jazz', 'classical', 'ambient', 'folk', 'metal', 'latin', 'rnb', 'reggae', 'house', 'blues']
majmin_aggs = [False,True]

for genre in genres:
    for majmin_agg in majmin_aggs:
        # Get itemsets for all genre graph
        if genre:
            sets = col_meta.find_one({"tag_params.tag_val":"pop","fi_type":"frequent","majmin_agg":majmin_agg})['itemsets']
        else:
            sets = col_meta.find_one({"tag_params":None,"fi_type":"frequent","majmin_agg":majmin_agg})['itemsets']
        # Get length 2 sets for circular graph
        doubletons = [x[1] for x in sets['items'].items() if len(x[1]) == 2]
        n = len(doubletons)

        time_ind = [25,50,75,100,125,150,175,200,225,250,275,300,325,350]

        for x in time_ind:
            if x-1 <= n:
                sample = np.random.randint(0,n,x)

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
                    "genre":genre,
                    "majmin_agg":majmin_agg,
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


with open("Project/Data/Optimisation/results_allgenre.json","w") as filename:
    json.dump(res,filename)




with open("Project/Data/Optimisation/results_allgenre.json","r") as filename:
    data = json.load(filename)

print(max([x['n'] for x in data]))



ns = [25,50,75,100,125,150,175,200,225,250,275,300,325,350]

avsdf_time_no_la_mean = []
avsdf_time_la_mean = []
avsdf_cross_nola_mean = []
avsdf_cross_la_mean = []
bb_time_no_la_mean = []
bb_time_la_mean = []
bb_cross_nola_mean = []
bb_cross_la_mean = []
default_cross_mean = []

avsdf_time_no_la_err = []
avsdf_time_la_err = []
avsdf_cross_nola_err = []
avsdf_cross_la_err = []
bb_time_no_la_err = []
bb_time_la_err = []
bb_cross_nola_err = []
bb_cross_la_err = []
default_cross_err = []


for n in ns:

    avsdf_time_no_la = [x['avsdf_time_no_la'] for x in data if x['n'] == n]
    avsdf_time_no_la_mean.append(np.mean(avsdf_time_no_la))
    avsdf_time_no_la_err.append(sem(avsdf_time_no_la))

    avsdf_time_la = [x['avsdf_time_la'] for x in data  if x['n'] == n]
    avsdf_time_la_mean.append(np.mean(avsdf_time_la))
    avsdf_time_la_err.append(sem(avsdf_time_la))

    avsdf_cross_nola = [x['avsdf_cross_nola'] for x in data if x['n'] == n]
    avsdf_cross_nola_mean.append(np.mean(avsdf_cross_nola))
    avsdf_cross_nola_err.append(sem(avsdf_cross_nola))

    avsdf_cross_la = [x['avsdf_cross_la'] for x in data if x['n'] == n]
    avsdf_cross_la_mean.append(np.mean(avsdf_cross_la))
    avsdf_cross_la_err.append(sem(avsdf_cross_la))

    bb_time_no_la = [x['bb_time_no_la'] for x in data if x['n'] == n]
    bb_time_no_la_mean.append(np.mean(bb_time_no_la))
    bb_time_no_la_err.append(sem(bb_time_no_la))

    bb_time_la = [x['bb_time_la'] for x in data if x['n'] == n]
    bb_time_la_mean.append(np.mean(bb_time_la))
    bb_time_la_err.append(sem(bb_time_la))

    bb_cross_nola = [x['bb_cross_nola'] for x in data if x['n'] == n]
    bb_cross_nola_mean.append(np.mean(bb_cross_nola))
    bb_cross_nola_err.append(sem(bb_cross_nola))

    bb_cross_la = [x['bb_cross_la'] for x in data if x['n'] == n]
    bb_cross_la_mean.append(np.mean(bb_cross_la))
    bb_cross_la_err.append(sem(bb_cross_la))

    default_cross = [x['cross_default'] for x in data if x['n'] == n]
    default_cross_mean.append(np.mean(default_cross))
    default_cross_err.append(sem(default_cross))



plt.figure(figsize=(7,5))
plt.errorbar(ns,avsdf_time_no_la_mean,yerr=avsdf_time_no_la_err,fmt='s',label='AVSDF')
plt.errorbar(ns,avsdf_time_la_mean,yerr=avsdf_time_la_err,fmt='x',label='AVSDF (with local adjusting)')
plt.errorbar(ns,bb_time_no_la_mean,yerr=bb_time_no_la_err,fmt='^',label='Baur Brandes')
plt.errorbar(ns,bb_time_la_mean,yerr=bb_time_la_err,fmt='D',label='Baur Brandes (with local adjusting)')
plt.xlabel("Number of graph edges")
plt.ylabel("Calculation time (seconds)")
plt.legend()
plt.show()

plt.figure(figsize=(7,5))
plt.errorbar(ns,avsdf_cross_nola_mean,yerr=avsdf_cross_nola_err,fmt='s',label='AVSDF')
plt.errorbar(ns,avsdf_cross_la_mean,yerr=avsdf_cross_la_err,fmt='x',label='AVSDF (with local adjusting)')
plt.errorbar(ns,bb_cross_nola_mean,yerr=bb_cross_nola_err,fmt='+',label='Baur Brandes')
plt.errorbar(ns,bb_cross_la_mean,yerr=bb_cross_la_err,fmt='D',label='Baur Brandes (with local adjusting)')
plt.errorbar(ns,default_cross_mean,yerr=default_cross_err,fmt='o',label='Root node ordering')
plt.xlabel("Number of graph edges")
plt.ylabel("Total number of edge crossings")
plt.legend()
plt.show()



with open("Project/Data/Optimisation/results_allgenre.json","r") as filename:
    data = json.load(filename)

print(pd.DataFrame(data).to_csv())