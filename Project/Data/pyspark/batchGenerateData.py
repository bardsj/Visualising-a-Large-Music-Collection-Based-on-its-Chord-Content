"""
Load and filter data for different genre tags, 

"""
from pprint import pprint
import findspark
import pyspark
from sparkFrequentItemsets import SparkFrequentItemsetsFPG,SparkFrequentItemsetsPrefixSpan
import os
import pickle
import time
import sys
sys.path.append(os.getcwd())
from Project.Data.Optimisation.CircularGraphLogic import AVSDF
import json
from itertools import chain

os.environ['PYSPARK_SUBMIT_ARGS'] = '"--packages" "org.mongodb.spark:mongo-spark-connector_2.11:2.4.1" "--driver-memory" "4g" "pyspark-shell"'
findspark.init()
# Spark context
sc = pyspark.SparkContext.getOrCreate()
spark = pyspark.sql.SparkSession.builder \
    .config("spark.mongodb.input.uri", os.environ['MSC_CHORD_DB_URI'])\
    .config("spark.executor.heartbeatInterval","3600s")\
    .getOrCreate()

params = {"minSupport": 0.01, "minConfidence": 1,"filterRatio":0.05,"filterConfidence":0.6}

st = time.time()

write_results = []

#for i,genre in enumerate(['pop','rock','electronic','hiphop','jazz','indie','filmscore','classical','chillout','ambient','folk','metal','latin','rnb','reggae','punk','country','house','blues',None]):
for i,genre in enumerate(['pop','rock','electronic','hiphop','jazz','classical','ambient','folk','metal','latin','rnb','reggae','house','blues',None]):
    if genre:
        tag_filt = {"tag_name":"genres","tag_val":genre}
    else:
        tag_filt = None

    for majmin_agg in [False,True]:
        items = SparkFrequentItemsetsFPG(spark,limit=None,params=params,tag_filter=tag_filt,majmin_agg=majmin_agg)
        itemsets = items.get_itemsets()
        count = items.getDataframeCount()
        # Convert to dict for storage
        itemsets = itemsets.to_dict()

        write_results.append({
            "_id":str(i).zfill(4)+"-"+str(params['minSupport'])+"-"+str(params['filterRatio'])+"-"+str(params['filterConfidence'])+"-"+str(majmin_agg)+"f",
            "filter_params":params,
            "tag_params":tag_filt,
            "itemsets":itemsets,
            "majmin_agg":majmin_agg,
            "dfCount":count,
            "fi_type":'frequent'
        })


with open("Project/Data/pyspark/itemsets.json","w+") as filename:
    json.dump(write_results,filename)

print("Total time: " + str(time.time()-st))