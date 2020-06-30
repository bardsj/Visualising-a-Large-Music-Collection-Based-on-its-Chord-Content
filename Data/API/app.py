from flask import Flask,jsonify
from flask_cors import CORS
import pickle
from itertools import chain
import sys
import os
sys.path.append(os.getcwd())

from Visualisation.Optimisation.AVSDF import AVSDF

app = Flask(__name__)
CORS(app)


with open("Data\API\chordItemsetsNoLimit5pcSupportwpc.pkl","rb") as filename:
    itemsets = pickle.load(filename)

itemsets = itemsets.drop(columns=["freq"])

@app.route('/circular/<int:thresh>',methods=['GET'])
def returnDataCirc(thresh):

    ksets_circ = itemsets[itemsets['items'].str.len()==2]
    ksets_circ = ksets_circ[ksets_circ['supportPc']>thresh/100]

    if len(ksets_circ) > 0:
        ksets_circ = ksets_circ.rename(columns={"items":"labels","supportPc":"values"})
        sets_circ = ksets_circ.to_dict("records")
        # Order
        avsdf = AVSDF([s['labels'] for s in sets_circ])
        order_circ = avsdf.run_AVSDF()
    else:
        order_circ = []
        sets_circ = []

    return jsonify({"sets":sets_circ,"order":order_circ})

@app.route('/parallel/<int:thresh>',methods=['GET'])
def returnDataParallel(thresh):

    ksets_par_filt = itemsets[itemsets['supportPc']>thresh/100]
    if len(ksets_par_filt) > 0:
        ksets_par = ksets_par_filt[ksets_par_filt['items'].str.len()>1]
        order = list(ksets_par_filt[ksets_par_filt['items'].str.len()==1].sort_values(by='supportPc')[::-1]['items'].apply(lambda x: x[0]))
        ksets_par = ksets_par.rename(columns={"items":"labels","supportPc":"values"})
        ksets_par['labels'] = ksets_par['labels'].apply(lambda x: sorted(x))
        sets_par = ksets_par.to_dict("records")
    else:
        sets_par = []
        order = []

    return jsonify({"sets":sets_par,"order":order})


app.run(debug=True)