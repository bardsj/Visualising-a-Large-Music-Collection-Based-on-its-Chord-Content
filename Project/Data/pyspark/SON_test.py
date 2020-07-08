import findspark
import pyspark
from sparkFrequentItemsets import SparkFrequentItemsetsSON, SparkFrequentItemsetsFPG
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

results = []

for s in range(5, 40, 5):

    params = {"minSupport": s/100, "minConfidence": 1,"filterRatio":None}

    st_SON = time.time()
    items = SparkFrequentItemsetsSON(spark, 10000, params).get_itemsets()
    time_elapsed_SON = time.time() - st_SON

    st_FPG = time.time()
    items = SparkFrequentItemsetsFPG(spark, 10000, params).get_itemsets()
    time_elapsed_FPG = time.time() - st_FPG

    results.append({"support": s/100,
                    "time":
                        {
                            "SON": time_elapsed_SON,
                            "FPG": time_elapsed_FPG
                        }
                    })

with open("SON_FPG_timecomp_results.pkl","wb+") as filename:
    pickle.dump(results,filename)