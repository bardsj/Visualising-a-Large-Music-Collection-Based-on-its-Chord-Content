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
from collections import OrderedDict
from random import shuffle

# Create instance of Flask app with
app = Flask(__name__)
# Enable CORS 
CORS(app)

# Metadata and itemset results db connection
client_meta = MongoClient(os.environ['MSC_MONGO_PERSONAL_URI'])
col_meta = client_meta.jamendo.songMetadata
col_res = client_meta.jamendo.itemsetData
# Chord db connection
client_chord = MongoClient(os.environ['MSC_CHORD_DB_URI'])
col_chord = client_chord.jamendo.chords

# Default ordering based on root nodes - used in heirarchical bundling
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

default_order_agg = ["Cmaj","Cmin", \
        "Dbmaj","Dbmin",
        "Dmaj","Dmin",
        "Ebmaj","Ebmin",
        "Emaj","Emin",
        "Fmaj","Fmin",
        "Gbmaj","Gbmin",
        "Gmaj","Gmin",
        "Abmaj","Abmin",
        "Amaj","Amin",
        "Bbmaj","Bbmin",
        "Bmaj","Bmin"
        ]


def getData(request):
    """
        Query mongodb for data based on API request params

        Parameters
        ----------
        request: flask.request
            The request recieved by the API containing request parameters in request.args
        Returns
        -------
        sets: list(dict)
            The data retrieved from MongoDB based on request parameters containing:
                - labels: list - the frequent itemset labels e.g ["C7","Abmin"]
                - values: float - the support value as a pecentage of the total dataset
                - tag: str - the value of the tag type requested (e.g. "jazz") 
    """

    # If tag values (i.e. genre) specified in the request, return relevant document of
    # frequent itemsets and relevant metadata
    fi_type = 'frequent'
    if 'fi_type' in request.args:
        if request.args['fi_type'] == 'hui':
            fi_type = 'hui'
        else:
            fi_type = 'frequent'

    if 'tag_name' and 'tag_val' in request.args:
        # Get tag request
        tag_val = request.args['tag_val'].split(",")
        tag_name = request.args['tag_name']
        try:
            # MongoDB query
            # Check if aggregation specified in request
            if 'majmin_agg' in request.args:
                if request.args['majmin_agg'] == "true":
                    # No major/minor aggregation for sequence data at this time
                    if fi_type == 'frequent':
                        agg = True
                    else:
                        agg = False
                else:
                    agg = False
                data_mult = col_res.find({"tag_params.tag_name":tag_name,"tag_params.tag_val":{"$in":tag_val},"majmin_agg":agg,"fi_type":fi_type})
            else:
                data_mult = col_res.find({"tag_params.tag_name":tag_name,"tag_params.tag_val":{"$in":tag_val},"majmin_agg":False,"fi_type":fi_type})
                if not data_mult.count():
                    abort(404,description="Error retrieving data")
            # Parse into suitable format/data structure
            sets = []
            for d in data_mult:
                if fi_type == 'frequent':
                    for i,s in zip(d['itemsets']['items'].values(),d['itemsets']['supportPc'].values()):
                        sets.append({"labels":i, "values":s,"tag":d['tag_params']['tag_val']})
                else:
                    for i in d['itemsets']:
                        sets.append({"labels":i['itemset'], "values":i['minUtil'],"tag":d['tag_params']['tag_val']})
        except errors.PyMongoError as e:
            abort(500,description="Could not connect to the database - " + str(e))
    else:
        # If no tags return data for all tracks
        try:
            # Check if aggregation specified in request
            if 'majmin_agg' in request.args:
                if request.args['majmin_agg'] == "true":
                    # No major/minor aggregation for sequence data at this time
                    if fi_type == 'frequent':
                        agg = True
                    else:
                        agg = False
                else:
                    agg = False
                data = col_res.find_one({"tag_params":None,"majmin_agg":agg,"fi_type":fi_type})
            else:
                data = col_res.find_one({"tag_params":None,"majmin_agg":False,"fi_type":fi_type})
            if not data:
                abort(404,description="Error retrieving data")
            if fi_type == 'frequent':
                sets = [{"labels":l,"values":v,"tag":None} for l,v in zip(data['itemsets']['items'].values(),data['itemsets']['supportPc'].values())]
            else:
                sets = [{"labels":i['itemset'],"values":i['minUtil'],"tag":None} for i in data['itemsets']]
        except errors.PyMongoError as e:
            abort(500,description="Could not connect to the database - " + str(e))
    
    return sets


@app.route('/circular',methods=['GET'])
def returnDataCirc():
    """
        API route - data for the simple circular layout, can apply order optimisation method before returning order
    """

    # Get the data from the db
    sets = getData(request)
    # Filter for only values of length 2 
    # for biconnected graph this is sufficient as all supersets (i.e. orders greater than 2) must contain these subsets
    sets = [s for s in sets if len(s['labels']) == 2]
    # Apply order optimisation
    if "order_opt" in request.args:
        if request.args['order_opt'] == "avsdf":
            order = AVSDF([s['labels'] for s in sets],local_adjusting=False).run_AVSDF()
        elif request.args['order_opt'] == "avsdf_la":
            order = AVSDF([s['labels'] for s in sets],local_adjusting=True).run_AVSDF()
        elif request.args['order_opt'] == "bb":
            order = BaurBrandes([s['labels'] for s in sets],local_adjusting=False).run_bb()
        elif request.args['order_opt'] == "bb_la":
            order = BaurBrandes([s['labels'] for s in sets],local_adjusting=True).run_bb()
        else:
            abort(500,description="Optimisation type not recognised")
    else:
        if 'majmin_agg' in request.args:
            if request.args['majmin_agg']:
                order = default_order_agg
            else:
                order = default_order
        else:
            order = default_order

    return jsonify({"sets":sets,"order":order})


@app.route('/parallel',methods=['GET'])
def returnDataParallel():
    """
        API route - data for the parallel coordinates layout
    """

    # Get data from db
    sets = getData(request)
    # Get singletons
    single_sets = [s for s in sets if len(s['labels']) == 1]
    # Add sets that aren't present as singletons to bottom of the list if 
    # HUI mining selected as downward closure doesn't apply in the same way
    missing = set(default_order).difference(*[x['labels'] for x in single_sets])
    single_sets += [{'labels':[k],'values':0} for k in sorted(missing)]
    # Remove duplicates and keep the highest support val (duplicates occur when more than one genre is selected)
    max_vals = {}
    for s in single_sets:
        if s['labels'][0] not in max_vals.keys():
            max_vals[s['labels'][0]] = s['values']
        else:
            if s['values'] > max_vals[s['labels'][0]]:
                max_vals[s['labels'][0]] = s['values']

    order = default_order
    if 'order_opt' in request.args:
        if request.args['order_opt'] == 'sorder':
            # Sort singletons by support to get order
            order = [s for s in sorted(max_vals,key=lambda s: s[1],reverse=True)]
    if 'majmin_agg' in request.args and order == default_order:
        if request.args['majmin_agg']:
            order = default_order_agg
    #order = list(chain(*order))
    # Remove singletons from sets
    sets = [s for s in sets if len(s['labels']) > 1]
    # Sort set within sets based on support value (order)
    sort_map = {k:i for i,k in enumerate(order)}
    sets = [{'labels':sorted(s['labels'],key=lambda x: sort_map[x]), \
             'tag':s['tag'], \
              'values':s['values']} for s in sets]

    return jsonify({"sets":sets,"order":order})


@app.route('/circHier',methods=['GET'])
def returnDataHier():
    """
        API route - data for circular heirarchical bundling
        Forces default order as this determines bundling nodes
    """

    # Get data from db
    sets = getData(request)
    # Select only doubletons
    sets = [s for s in sets if len(s['labels']) == 2]
    if 'majmin_agg' in request.args:
        if request.args['majmin_agg']:
            order = default_order_agg
        else:
            order = default_order
    else:
        order = default_order

    return jsonify({"sets":sets,"order":order})

import time

@app.route('/circClust',methods=['GET'])
def returnCircClust():
    """
        API route - get data for circular chart with clustered bundling
        Applies transformation and clustering to similar edges based on node positions
        to allow edges to be bundled together
    """
    # Get data from db
    sets = getData(request)
    # Filter for doubletons
    sets = [s for s in sets if len(s['labels']) == 2]

    # Apply order optimisation
    if "order_opt" in request.args:
        if request.args['order_opt'] == "avsdf":
            order = AVSDF([s['labels'] for s in sets],local_adjusting=False).run_AVSDF()
        elif request.args['order_opt'] == "avsdf_la":
            order = AVSDF([s['labels'] for s in sets],local_adjusting=True).run_AVSDF()
        elif request.args['order_opt'] == "bb":
            order = BaurBrandes([s['labels'] for s in sets],local_adjusting=False).run_bb()
        elif request.args['order_opt'] == "bb_la":
            order = BaurBrandes([s['labels'] for s in sets],local_adjusting=True).run_bb()
        else:
            abort(500,description="Optimisation type not recognised")
    else:
        if 'majmin_agg' in request.args:
            if request.args['majmin_agg']:
                order = default_order_agg
            else:
                order = default_order
        else:
            order = default_order

    # Leave only maj/min chords to see what it looks like clutter wise
    #sets = [s for s in sets if "7" not in "".join(s['labels'])]
    #order = [o for o in order if "7" not in o]

    # Map vertex labels to order index
    order_map = {k:i for i,k in enumerate(order)}

    # Dataframe (easier to manipulate/apply clustering)
    df = pd.DataFrame(sets)

    # Sort by order as clustering will be affected by the order of the vertices in edge definitions
    df['labels'] = df['labels'].apply(lambda x: sorted(x,key=lambda x: (np.sin((order_map[x]/len(order_map))*2*np.pi))))
    # Sort set labels in order
    s_labels_ordered = list(df['labels'])
    # Apply sin/cos transformation (takes into account circular nature of data)
    df['sin1'] = df['labels'].apply(lambda x: np.sin((order_map[x[0]]/len(order_map))*2*np.pi))
    df['cos1'] = df['labels'].apply(lambda x: np.cos((order_map[x[0]]/len(order_map))*2*np.pi))
    df['sin2'] = df['labels'].apply(lambda x: np.sin((order_map[x[1]]/len(order_map))*2*np.pi))
    df['cos2'] = df['labels'].apply(lambda x: np.cos((order_map[x[1]]/len(order_map))*2*np.pi))
    
    # Apply clustering to edges based on node values
    #labs = KMeans(n_clusters=40,random_state=44).fit(df[['sin1','cos1','sin2','cos2']]).labels_
    labs = AgglomerativeClustering(n_clusters=None,distance_threshold=1).fit(df[['sin1','cos1','sin2','cos2']]).labels_   

    # Add cluster label to returned JSON
    sets_w_lab = []
    for set_lab,s,lab in zip(s_labels_ordered,sets,labs):
        sets_w_lab.append({"labels":set_lab,"values":s['values'],"tag":s['tag'], "km_label": int(lab)})

    return jsonify({"sets":sets_w_lab,"order":order})


@app.route('/parallelClust',methods=['GET'])
def returnPrallelClust():
    """
        API route - get data for parallel chart with clustered bundling
        Cluster edges based on source/target node positions to allow edges to be bundled together
    """

    # Get data from db
    sets = getData(request)
        # Get singletons
    single_sets = [s for s in sets if len(s['labels']) == 1]
    # Add sets that aren't present as singletons to bottom of the list if 
    # HUI mining selected as downward closure doesn't apply in the same way
    missing = set(default_order).difference(*[x['labels'] for x in single_sets])
    single_sets += [{'labels':[k],'values':0} for k in sorted(missing)]
    # Remove duplicates and keep the highest support val (duplicates occur when more than one genre is selected)
    max_vals = {}
    for s in single_sets:
        if s['labels'][0] not in max_vals.keys():
            max_vals[s['labels'][0]] = s['values']
        else:
            if s['values'] > max_vals[s['labels'][0]]:
                max_vals[s['labels'][0]] = s['values']

    order = default_order
    if 'order_opt' in request.args:
        if request.args['order_opt'] == 'sorder':
            # Sort singletons by support to get order
            order = [s for s in sorted(max_vals,key=lambda s: s[1],reverse=True)]
    # Filter for doubletons
    sets = [s for s in sets if len(s['labels']) > 1]
    if 'majmin_agg' in request.args and order == default_order:
        if request.args['majmin_agg']:
            order = default_order_agg

    # Map vertex labels to order index
    order_map = {k:i for i,k in enumerate(order)}

    # Dataframe (easier to manipulate/apply clustering)
    df = pd.DataFrame(sets)

    # Sort by order as clustering will be affected by the order of the vertices in edge definitions
    df['labels'] = df['labels'].apply(lambda x: sorted(x,key=lambda x: order_map[x]))
    # Sort set labels in order
    s_labels_ordered = list(df['labels'])
    # Struct to hold clustering results
    res = {i:[] for i in range(len(df))}
    # Pop get increasing parallel axes nodes
    for i in range(max(df['labels'].str.len())):
        df = df[df['labels'].str.len() > i+1]
        ag = AgglomerativeClustering(n_clusters=None,distance_threshold=30)
        df["src"] = df['labels'].apply(lambda x: order_map[x[i]])
        df["tgt"] = df['labels'].apply(lambda x: order_map[x[i+1]])
        if len(df) > 10:
            labs = ag.fit(df[["src","tgt"]]).labels_
            for i,l in zip(df.index,labs):
                res[i].append(int(l)) 

    # Add cluster label to returned JSON
    sets_w_lab = []
    for i,set_lab,s in zip(range(len(sets)),s_labels_ordered,sets):
        sets_w_lab.append({"labels":set_lab,"values":s['values'],"tag":s['tag'], "km_label": res[i]})

    return jsonify({"sets":sets_w_lab,"order":order})

import json


@app.route('/queryData',methods=['GET'])
def queryData():
    """
        API route - get sample of data from metadata db based on query params
    """
    # Build query
    qparams = {}

    if 'genre' in request.args:
        qparams['musicinfo.tags.genres'] = {"$all":request.args['genre'].split(",")}

    if 'chordSel' in request.args:
        # Get all tracks for metadata query
        q_docs = [d for d in col_meta.find(qparams)]
        # Get all valid ids
        valid_ids = [int(d['_id']) for d in q_docs]
        # Get chords requested
        rch = request.args['chordSel'].split(",")

        # Generate filter based on selected chords
        #exprs = [{'chordRatio.'+ch:{"$exists":True}} for ch in rch]
        exprs = [{"$and":[{'chordRatio.'+ch:{"$exists":True}},{'chordRatio.'+ch:{"$gt":0.05}}]} for ch in rch]

        # Include valid id based on genre selection
        #exprs.append({'_id':{'$in':valid_ids}})
        # Get tracks ids from chord database
        chord_ids = [x['_id'] for x in col_chord.find({"$and":exprs},{'_id':1})]
        query_ids = set(valid_ids).intersection(set(chord_ids))

        # Filter original query based on new chord info
        q_docs = list(filter(lambda x: int(x['_id']) in chord_ids,q_docs))
        n_docs = len(q_docs)
    else:
        q_docs = col_meta.find(qparams)
        n_docs = q_docs.count()

    # Sample random 5 tracks
    if n_docs > 5:
        results = [q_docs[int(i)] for i in np.random.randint(0,n_docs,5)]
    else:
        results = [d for d in q_docs]

    # Get chord data for selected tracks
    for r in results:
        chord_vals = col_chord.find_one({"_id":int(r['_id'])})['chordRatio']
        chord_vals = OrderedDict(sorted(chord_vals.items(), key=lambda kv: kv[1],reverse=True)).items()
        r['chords'] = [c[0] for c in chord_vals]
        r['chordRVal'] = [c[1] for c in chord_vals]

    return jsonify(results)


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def not_found(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)