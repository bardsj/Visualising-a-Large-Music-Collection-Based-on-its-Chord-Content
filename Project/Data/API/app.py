from flask import Flask,jsonify,request,abort
from flask_cors import CORS
import sys
import os
sys.path.append(os.getcwd())
from Project.Data.Optimisation.AVSDF import AVSDF
from pymongo import MongoClient,errors
import numpy as np
from itertools import chain

# Create instance of Flask app with
app = Flask(__name__)
# Enable CORS 
CORS(app)
# Pymongo connection (public user, read only access for this collection)
client = MongoClient("mongodb+srv://publicUser:jdACcF7TyiU2Vshj@msc.5jje5.gcp.mongodb.net/jamendo?retryWrites=false&w=majority")
col = client.jamendo.itemsetData

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
    order = AVSDF([s['labels'] for s in sets],local_adjusting=False).run_AVSDF()

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

    return jsonify({"sets":sets,"order":order})

@app.route('/circHier',methods=['GET'])
def returnDataCHier():
    sets = getData(request)
    sets = [s for s in sets if len(s['labels']) == 2]

    order = ['C7','Cmaj','Cmaj7','Cmin','Cmin7','D7','Db7','Dbmaj','Dbmaj7','Dbmin','Dbmin7','Dmaj','Dmaj7','Dmin','Dmin7','E7','Eb7','Ebmaj','Ebmaj7','Ebmin', \
    'Ebmin7','Emaj','Emaj7','Emin','Emin7','F7','Fmaj','Fmaj7','Fmin','Fmin7','G7','Gb7','Gbmaj','Gbmaj7','Gbmin','Gbmin7','Gmaj','Gmaj7','Gmin', 'Gmin7','A7','Ab7', \
     'Abmaj','Abmaj7','Abmin','Abmin7','Amaj','Amaj7','Amin','Amin7','B7','Bb7','Bbmaj','Bbmaj7','Bbmin','Bbmin7','Bmaj','Bmaj7','Bmin','Bmin7']

    return jsonify({"sets":sets,"order":order})


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def not_found(e):
    return jsonify(error=str(e)), 500


app.run(debug=True)