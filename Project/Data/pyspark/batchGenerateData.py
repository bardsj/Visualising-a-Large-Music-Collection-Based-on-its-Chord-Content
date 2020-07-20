"""
Load and filter data for different genre tags, 

"""
from pprint import pprint
import findspark
import pyspark
from sparkFrequentItemsets import SparkFrequentItemsetsFPG
import os
import pickle
import time
import sys
sys.path.append(os.getcwd())
from Project.Data.Optimisation.AVSDF import AVSDF
import json

os.environ['PYSPARK_SUBMIT_ARGS'] = '"--packages" "org.mongodb.spark:mongo-spark-connector_2.11:2.4.1" "--driver-memory" "4g" "pyspark-shell"'
findspark.init()
# Spark context
sc = pyspark.SparkContext.getOrCreate()
spark = pyspark.sql.SparkSession.builder \
    .config("spark.mongodb.input.uri", os.environ['MSC_CHORD_DB_URI'])\
    .getOrCreate()

params = {"minSupport": 0.01, "minConfidence": 1,"filterRatio":0.05}

st = time.time()

write_results = []

for i,genre in enumerate(['jazz','electronic','chillout','ambient','pop','rock','dance','hiphop',None]):
    if genre:
        tag_filt = {"tag_name":"genres","tag_val":genre}
    else:
        tag_filt = None

    items = SparkFrequentItemsetsFPG(spark, None, params,tag_filter=tag_filt)
    itemsets = items.get_itemsets()
    # Get k = 2 length itemsets to calculate circular order
    ksets_circ = itemsets[itemsets['items'].str.len()==2]
    # Convert to dict for storage
    itemsets = itemsets.to_dict()
    order = AVSDF(list(ksets_circ['items'])).run_AVSDF()

    write_results.append({
        "_id":str(i).zfill(4)+"-"+str(params['minSupport'])+"-"+str(params['filterRatio']),
        "filter_params":params,
        "tag_params":tag_filt,
        "itemsets":itemsets,
        "AVSDF_order":order
    })


with open("Project/Data/pyspark/itemsets.json","w+") as filename:
    json.dump(write_results,filename)

print("Total time: " + str(time.time()-st))