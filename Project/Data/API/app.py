from flask import Flask,jsonify,request,abort
from flask_cors import CORS
import sys
import os
sys.path.append(os.getcwd())
from Project.Data.Optimisation.CircularGraphLogic import BaurBrandes,AVSDF
from pymongo import MongoClient,errors
import numpy as np
from itertools import chain
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering

# Create instance of Flask app with
app = Flask(__name__)
# Enable CORS 
CORS(app)
# Pymongo connection (public user, read only access for this collection)
client = MongoClient("mongodb+srv://publicUser:jdACcF7TyiU2Vshj@msc.5jje5.gcp.mongodb.net/jamendo?retryWrites=false&w=majority")
col = client.jamendo.itemsetData

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

def getData(request):
    if 'tag_name' and 'tag_val' in request.args:
        # Get tag request
        tag_val = request.args['tag_val'].split(",")
        tag_name = request.args['tag_name']
        try:
            data_mult = col.find({"tag_params.tag_name":tag_name,"tag_params.tag_val":{"$in":tag_val}})
            sets = []
            for d in data_mult:
                for i,s in zip(d['itemsets']['items'].values(),d['itemsets']['supportPc'].values()):
                    sets.append({"labels":i, \
                                    "values":s,\
                                    "tag":d['tag_params']['tag_val']})
        except errors.PyMongoError as e:
            abort(500,description="Could not connect to the database - " + str(e))
        if not data_mult:
            abort(404,description="Error retrieving data")
    else:
        # If no tags return data for all tracks
        try:
            data = col.find_one({"tag_params":None})
            sets = [{"labels":l,"values":v,"tag":None} for l,v in zip(data['itemsets']['items'].values(),data['itemsets']['supportPc'].values())]
        except errors.PyMongoError as e:
            abort(500,description="Could not connect to the database - " + str(e))
        if not data:
            abort(404,description="Error retrieving data")
    
    return sets


@app.route('/circular',methods=['GET'])
def returnDataCirc():
    sets = getData(request)
    sets = [s for s in sets if len(s['labels']) == 2]
    #order = AVSDF([s['labels'] for s in sets],local_adjusting=True).run_AVSDF()
    order = BaurBrandes([s['labels'] for s in sets]).run_bb()

    return jsonify({"sets":sets,"order":order})

@app.route('/parallel',methods=['GET'])
def returnDataParallel():
    sets = getData(request)
    # Get singletons
    single_sets = [s for s in sets if len(s['labels']) == 1]
    # Remove duplicates and keep the highest support val (duplicates occur when more than one genre is selected)
    max_vals = {}
    for s in single_sets:
        if s['labels'][0] not in max_vals.keys():
            max_vals[s['labels'][0]] = s['values']
        else:
            if s['values'] > max_vals[s['labels'][0]]:
                max_vals[s['labels'][0]] = s['values']

    # Sort singletons by support to get order
    order = [s for s in sorted(max_vals,key=lambda s: s[1],reverse=True)]
    #order = list(chain(*order))
    # Remove singletons from sets
    sets = [s for s in sets if len(s['labels']) > 1]
    # Sort set within sets based on support value (order)
    sort_map = {k:i for i,k in enumerate(order)}
    sets = [{'labels':sorted(s['labels'],key=lambda x: sort_map[x]), \
             'tag':s['tag'], \
              'values':s['values']} for s in sets]

    return jsonify({"sets":sets,"order":default_order})

@app.route('/circHier',methods=['GET'])
def returnDataHier():
    sets = getData(request)
    sets = [s for s in sets if len(s['labels']) == 2]
    order = default_order

    return jsonify({"sets":sets,"order":order})

@app.route('/circKMeans',methods=['GET'])
def returnKMeans():
    sets = getData(request)
    sets = [s for s in sets if len(s['labels']) == 2]
    order = AVSDF([s['labels'] for s in sets],local_adjusting=False).run_AVSDF()
    #order = BaurBrandes([s['labels'] for s in sets]).run_bb()
    #order = default_order

    order_map = {k:i for i,k in enumerate(order)}

    df = pd.DataFrame(sets)
    df = df[df['labels'].map(len) == 2]

    # Sort by order as clustering will be affected by the order of the vertices in edge definitions
    df['labels'] = df['labels'].apply(lambda x: sorted(x,key=lambda x: order_map[x]))
    # Sort set labels in order
    s_labels_ordered = list(df['labels'])

    df['sin1'] = df['labels'].apply(lambda x: np.sin((order_map[x[0]]/len(order_map))*2*np.pi))
    df['cos1'] = df['labels'].apply(lambda x: np.cos((order_map[x[0]]/len(order_map))*2*np.pi))
    df['sin2'] = df['labels'].apply(lambda x: np.sin((order_map[x[1]]/len(order_map))*2*np.pi))
    df['cos2'] = df['labels'].apply(lambda x: np.cos((order_map[x[1]]/len(order_map))*2*np.pi))
    #labs = KMeans(n_clusters=20,random_state=44).fit(df[['sin1','cos1','sin2','cos2']]).labels_
    labs = AgglomerativeClustering(n_clusters=None,distance_threshold=1).fit(df[['sin1','cos1','sin2','cos2']]).labels_   

    sets_w_lab = []

    for set_lab,s,lab in zip(s_labels_ordered,sets,labs):
        sets_w_lab.append({"labels":set_lab, \
                    "values":s['values'],\
                    "tag":s['tag'], \
                    "km_label": int(lab)})

    return jsonify({"sets":sets_w_lab,"order":order})

@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def not_found(e):
    return jsonify(error=str(e)), 500


app.run(debug=True)