"""
    Simple Flask app to serve pre-generated frequent itemset data for circular layout and parallel coordinates
"""

from flask import Flask,jsonify
from flask_cors import CORS
import pickle
from itertools import chain
import sys
import os
sys.path.append(os.getcwd())
from Visualisation.Optimisation.AVSDF import AVSDF

# Create instance of Flask app with
app = Flask(__name__)
# Enable CORS 
CORS(app)

# Load frequent itemsets dataframe
with open("Data\API\chordItemsetsNoLimit5pcSupportwpc.pkl","rb") as filename:
    itemsets = pickle.load(filename)

# Drop raw frequency column
itemsets = itemsets.drop(columns=["freq"])

@app.route('/circular/<int:thresh>',methods=['GET'])
def returnDataCirc(thresh):
    """
        Return data structure and order for circular layout.
        Consists of only doubletons (frequent itemsets of k=2) and applies optimisation to node ordering.

        Parameters
        ----------
        thresh : int
            Percentage threshold for support values calculated based on size of data set from Spark script.
            Filter returned data above this threshold (range = 5%-30%) 
    """
    # Filter only sets of length 2
    ksets_circ = itemsets[itemsets['items'].str.len()==2]
    # Filter based on support threshold value
    ksets_circ = ksets_circ[ksets_circ['supportPc']>thresh/100]

    if len(ksets_circ) > 0:
        # Rename columns to match visualisation implementation
        ksets_circ = ksets_circ.rename(columns={"items":"labels","supportPc":"values"})
        # Convert to "record" style dictionary to be parsed by visualisation framework 
        sets_circ = ksets_circ.to_dict("records")
        # Pass list of edges to AVSDF to apply node reordering
        avsdf = AVSDF([s['labels'] for s in sets_circ])
        order_circ = avsdf.run_AVSDF()
    else:
        order_circ = []
        sets_circ = []
    # Return JSON
    return jsonify({"sets":sets_circ,"order":order_circ})

@app.route('/parallel/<int:thresh>',methods=['GET'])
def returnDataParallel(thresh):
    """
        Return data structure and order for parallel coordinates layout.

        Parameters
        ----------
        thresh : int
            Percentage threshold for support values calculated based on size of data set from Spark script.
            Filter returned data above this threshold (range = 5%-30%) 
    """
    # Filter based on support threshold value
    ksets_par_filt = itemsets[itemsets['supportPc']>thresh/100]

    if len(ksets_par_filt) > 0:
        # Filter out singletons (frequent itemsets of k=1)
        ksets_par = ksets_par_filt[ksets_par_filt['items'].str.len()>1]
        # Generate list of singletons and order by support value to generate initial axes ordering
        order = list(ksets_par_filt[ksets_par_filt['items'].str.len()==1].sort_values(by='supportPc')[::-1]['items'].apply(lambda x: x[0]))
        # Rename columns to match visualisation implementation
        ksets_par = ksets_par.rename(columns={"items":"labels","supportPc":"values"})
        # Sort nodes in list of edges
        ksets_par['labels'] = ksets_par['labels'].apply(lambda x: sorted(x))
        # Convert to "record" style dictionary to be parsed by visualisation framework
        sets_par = ksets_par.to_dict("records")
    else:
        sets_par = []
        order = []
    # Return JSON
    return jsonify({"sets":sets_par,"order":order})


app.run(debug=True)