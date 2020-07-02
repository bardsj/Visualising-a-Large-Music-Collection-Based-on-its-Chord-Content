import findspark
import pyspark
from sparkFrequentItemsets import SparkFrequentItemsetsSON
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

params={"minSupport":0.05, "minConfidence":1}
items = SparkFrequentItemsetsSON(spark,10000,params)
itemsets = items.get_itemsets()

from pprint import pprint

pprint(itemsets)