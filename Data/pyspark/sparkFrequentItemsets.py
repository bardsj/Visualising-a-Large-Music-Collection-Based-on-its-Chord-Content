import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType,StringType
from pyspark.ml.fpm import FPGrowth

class SparkFrequentItemsetsFPG:
    """
        Apply the FP Growth frequent itemset mining algorithm from the spark ml lib to the chord data

        Parameters
        ----------
        spark : SparkSession
            The spark session object
        limit : int, optional
            Limit the number of documents loaded from mongodb source
        params : dict, optional
            Parameter key/value pairs for minSupport (the algorithms support threshold) and 
            minConfidence (for generating association rules, can ignore here as we are only 
            interested in generating frequent itemsets)
    """

    def __init__(self,spark,limit=None,params={"minSupport":0.2, "minConfidence":0.5}):
        self.limit = limit
        self.spark = spark
        self.params = params
        self.df = self._load_data(self.spark)
        self.model = self._run_FPGrowth(self.df)

    def _load_data(self):
        # Load data from mongodb source
        if self.limit:
            df = self.spark.read.format("mongo").option('database', 'jamendo').option('collection', 'chords').load().limit(self.limit)
        else:
            df = self.spark.read.format("mongo").option('database', 'jamendo').option('collection', 'chords').load()

        df = df.sample(withReplacement=False,fraction=1.0)

        # User defined function to get key values (chords) from nested structure in dataframe
        getKeysUDF = F.udf(lambda x: list({k for k,v in x.asDict().items() if type(v) is float}),ArrayType(StringType()))

        # Apply UDF and select only chord and id cols
        return df.withColumn("chordItems",getKeysUDF(df['chordRatio'])).select("_id","chordItems")

    def _run_FPGrowth(self):
        # Apply spark ml libs FP-growth algorithm for frequent itemset mining
        fpGrowth = FPGrowth(itemsCol="chordItems", minSupport = self.params["minSupport"], minConfidence=self.params["minConfidence"])
        model = fpGrowth.fit(self.df)
        return model

    def get_itemsets(self):
        n_items = self.df.count()
        itemsets = self.model.freqItemsets.withColumn("supportPc",self.model.freqItemsets['freq']/n_items)
        return itemsets.toPandas()