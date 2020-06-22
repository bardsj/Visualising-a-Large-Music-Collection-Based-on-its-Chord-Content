from flask import Flask,jsonify
from flask_cors import CORS
import pickle

import sys
sys.path.append("C:\\Users\\jackb\\Documents\\MSc\\Individual Project\\Visualising a Large Music Collection Based on its Chord Content\\")

from Visualisation.Optimisation.AVSDF import AVSDF

app = Flask(__name__)
CORS(app)


with open("Data/API/chordItemsets.pkl","rb") as filename:
    itemsets = pickle.load(filename)

@app.route('/',methods=['GET'])
def returnData():
    ksets = itemsets[itemsets['items'].str.len()==2]
    ksets = ksets.rename(columns={"items":"labels","freq":"values"})
    sets = ksets.to_dict("records")

    # Order
    avsdf = AVSDF([s['labels'] for s in sets])
    order = avsdf.run_AVSDF()
    return jsonify({"sets":sets,"order":order})



app.run(debug=True)