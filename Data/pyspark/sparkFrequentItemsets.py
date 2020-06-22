import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType,StringType
from pyspark.ml.fpm import FPGrowth

class SparkFrequentItemsets:
    def __init__(self,spark,limit,params={"minSupport":0.2, "minConfidence":0.5}):
        self.limit = limit
        self.spark = spark
        self.params = params
        self.df = self._loadData(self.spark)
        self.model = self._runFPGrowth(self.df)

    def _loadData(self,spark):
        # Load data from mongodb source
        if self.limit:
            df = spark.read.format("mongo").option('database', 'jamendo').option('collection', 'chords').load().limit(self.limit)
        else:
            df = spark.read.format("mongo").option('database', 'jamendo').option('collection', 'chords').load()

        df = df.sample(withReplacement=False,fraction=1.0)

        # User defined function to get key values (chords) from nested structure in dataframe
        getKeysUDF = F.udf(lambda x: list({k for k,v in x.asDict().items() if type(v) is float}),ArrayType(StringType()))

        # Apply UDF and select only chord and id cols
        return df.withColumn("chordItems",getKeysUDF(df['chordRatio'])).select("_id","chordItems")

    def _runFPGrowth(self,df):
        # Apply spark ml libs FP-growth algorithm for frequent itemset mining
        fpGrowth = FPGrowth(itemsCol="chordItems", minSupport = self.params["minSupport"], minConfidence=self.params["minConfidence"])
        model = fpGrowth.fit(df)
        return model

    def getItemsets(self):
        return self.model.freqItemsets.toPandas()