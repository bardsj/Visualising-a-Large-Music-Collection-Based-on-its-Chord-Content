import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '"--packages" "org.mongodb.spark:mongo-spark-connector_2.11:2.4.1" "pyspark-shell"'
import findspark
findspark.init()

import pyspark

sc = pyspark.SparkContext.getOrCreate()
spark = pyspark.sql.SparkSession.builder \
    .config("spark.mongodb.input.uri", os.environ['MSC_CHORD_DB_URI'])\
    .getOrCreate()

df = spark.read.format("mongo").option('database', 'jamendo').option('collection', 'chords').load()


import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType,StringType,DataType


getKeysUDF = F.udf(lambda x: list({k for k,v in x.asDict().items() if type(v) is float}),ArrayType(StringType()))

df_chord_items = df.withColumn("chordItems",getKeysUDF(df['chordRatio'])).select("_id","chordItems")



from pyspark.ml.fpm import FPGrowth
from time import time

startTime = time()

fpGrowth = FPGrowth(itemsCol="chordItems", minSupport=0.2, minConfidence=1)
model = fpGrowth.fit(df_chord_items)

# Display frequent itemsets.
print(model.freqItemsets.show())
print(f"Time elapsed: {startTime-time()}")

