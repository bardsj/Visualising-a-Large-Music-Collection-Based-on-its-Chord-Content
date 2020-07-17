from flask import Flask,jsonify,request
from flask_cors import CORS
import sys
import os
sys.path.append(os.getcwd())
from Project.Data.Optimisation.AVSDF import AVSDF
from pymongo import MongoClient
import numpy as np

# Create instance of Flask app with
app = Flask(__name__)
# Enable CORS 
CORS(app)
# Pymongo connection
client = MongoClient(os.environ['MSC_MONGO_PERSONAL_URI'])
col = client.jamendo.itemsetData


@app.route('/circular',methods=['GET'])
def returnDataCirc():
    if 'tag_name' and 'tag_val' in request.args:
        # Get tag request
        data = col.find_one({"tag_params":{"tag_name":request.args['tag_name'],"tag_val":request.args['tag_val']}})
    else:
        # If no tags return data for all tracks
        data = col.find_one({"tag_params":None})

    itemsets = data['itemsets']

    # Only return sets of length 2 for circular layout
    itemsets['items'] = [d for d in itemsets['items'].values() if len(d) == 2]

    return jsonify({"sets":[{"labels":i,"values":v} for i,v in zip(itemsets['items'],list(itemsets['supportPc'].values()))],"order":data['AVSDF_order']})

@app.route('/parallel',methods=['GET'])
def returnDataParallel():
    if 'tag_name' and 'tag_val' in request.args:
        # Get tag request
        data = col.find_one({"tag_params":{"tag_name":request.args['tag_name'],"tag_val":request.args['tag_val']}})
    else:
        # If no tags return data for all tracks
        data = col.find_one({"tag_params":None})

    itemsets = data['itemsets']

    # Remove length 1 sets
    set_support = [(s,v) for s,v in zip(itemsets['items'].values(),itemsets['supportPc'].values()) if len(s) > 1]
    # Sort by support value
    order = sorted([(s,v) for s,v in zip(itemsets['items'].values(),itemsets['supportPc'].values()) if len(s) == 1],key=lambda x: x[1],reverse=True)
    order = [x[0][0] for x in order]
    # Split back to sets and support lists
    sets = [s[0] for s in set_support]
    support = [s[1] for s in set_support]
    # Sort order of items within sets based on support value
    sort_map = {k:i for i,k in enumerate(order)}
    sets = [sorted(s,key=lambda x: sort_map[x]) for s in sets]

    return jsonify({"sets":[{"labels":i,"values":v} for i,v in zip(sets,support)],"order":order})


app.run(debug=True)