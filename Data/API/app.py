from flask import Flask,jsonify
from flask_cors import CORS
import pickle

import sys
import os
sys.path.append(os.getcwd())

from Visualisation.Optimisation.AVSDF import AVSDF

app = Flask(__name__)
CORS(app)


with open("Data/API/chordItemsets.pkl","rb") as filename:
    itemsets = pickle.load(filename)

ksets_circ = itemsets[itemsets['items'].str.len()==2]
ksets_circ = ksets_circ.rename(columns={"items":"labels","freq":"values"})
sets_circ = ksets_circ.to_dict("records")
# Order
avsdf = AVSDF([s['labels'] for s in sets_circ])
order_circ = avsdf.run_AVSDF()


@app.route('/circular',methods=['GET'])
def returnDataCirc():
    return jsonify({"sets":sets_circ,"order":order_circ})

@app.route('/parallel',methods=['GET'])
def returnDataParallel():
    ksets_par = itemsets.rename(columns={"items":"labels","freq":"values"})
    sets_par = ksets_par.to_dict("records")
    order = None
    return jsonify({"sets":sets_par,"order":order})


app.run(debug=True)