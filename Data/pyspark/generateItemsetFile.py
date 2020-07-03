"""
Create temp file that can be served by the API.
Generates pickled dataframe of results from running the spark FPGrowth algorithm 
and saves this in the API folder so that it can be accessed by the Flask app.

"""
from pprint import pprint
import findspark
import pyspark
from sparkFrequentItemsets import SparkFrequentItemsetsFPG
import os
import pickle
import time

os.environ['PYSPARK_SUBMIT_ARGS'] = '"--packages" "org.mongodb.spark:mongo-spark-connector_2.11:2.4.1" "--driver-memory" "4g" "pyspark-shell"'
findspark.init()
# Spark context
sc = pyspark.SparkContext.getOrCreate()
spark = pyspark.sql.SparkSession.builder \
    .config("spark.mongodb.input.uri", os.environ['MSC_CHORD_DB_URI'])\
    .getOrCreate()

params = {"minSupport": 0.05, "minConfidence": 1}
items = SparkFrequentItemsetsFPG(spark, None, params)
itemsets = items.get_itemsets()

with open("Data/API/chordItemsets"+time.strftime("%Y-%m-%d-%H-%M-%S")+".pkl","wb") as filename:
        pickle.dump(itemsets,filename)
