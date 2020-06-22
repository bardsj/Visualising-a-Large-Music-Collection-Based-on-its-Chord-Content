## Create temp file that can be served by the API
import findspark
import pyspark
from sparkFrequentItemsets import SparkFrequentItemsets
import os
import pickle

os.environ['PYSPARK_SUBMIT_ARGS'] = '"--packages" "org.mongodb.spark:mongo-spark-connector_2.11:2.4.1" "--driver-memory" "4g" "pyspark-shell"'
findspark.init()
# Spark context
sc = pyspark.SparkContext.getOrCreate()
spark = pyspark.sql.SparkSession.builder \
    .config("spark.mongodb.input.uri", os.environ['MSC_CHORD_DB_URI'])\
    .getOrCreate()

params={"minSupport":0.1, "minConfidence":0.5}
items = SparkFrequentItemsets(spark,10000,params)
itemsets = items.getItemsets()

with open(f"Data/API/chordItemsets.pkl","wb") as filename:
    pickle.dump(itemsets,filename)