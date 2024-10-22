import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType,StringType
from pyspark.ml.fpm import FPGrowth, PrefixSpan
from collections import Counter
from itertools import combinations,chain
from operator import add
from pymongo import MongoClient
import os

class ChordLoader:
    """
    Load chord data into a spark dataframe and apply some preprocessing to extract chord values
    
    Parameters
    ----------
    spark : SparkSession
        The spark session object
    limit : int, optional
        Limit the number of documents loaded from mongodb source
    tag_filter : dict, optional
        Filter the dataframe by metadata tags - in the form {'tag_name':'genres','tag_val':'jazz'}
    majmin_agg : bool
        Aggregate by maj/min chords

    """
    def __init__(self,spark,params,limit,tag_filter,majmin_agg=False,type_fi='frequent'):
        self.limit = limit
        self.spark = spark
        self.params = params
        self.tag_filter = tag_filter
        self.majmin_agg = majmin_agg
        self.type_fi = type_fi
        self.df = self._load_data()

    def getDataframeCount(self):
        return self.df.count()

    def _load_data(self):
        """
        Loads data from mongodb source and extracts non zero chord values

        Returns
        -------
        pyspark.sql.DataFrame
            In the form:
                +---+--------------------+
                |_id|          chordItems|
                +---+--------------------+
                |214|[Bbmin7, Emin7, B...|
                |215|[Emaj, A7, Gmin, ...|
                |216|[Emaj, Dbmin7, Gb...|
                |217|[Ab7, F7, Abmaj, ...|
                |218|[Emaj, Dbmin7, Ab...|
                |219|[Emaj, Bbmin7, Em...|
                |220|[Emin7, Bmaj, Dbm...|

        """
        # Load data from mongodb source
        if self.limit:
            df = self.spark.read.format("mongo").option('database', 'jamendo').option('collection', 'chords').load().limit(self.limit)
        else:
            df = self.spark.read.format("mongo").option('database', 'jamendo').option('collection', 'chords').load()

        # Times out without this? 
        df = df.sample(withReplacement=False,fraction=1.0)
        f_ratio = self.params['filterRatio']

        # Filter by confidence value
        if self.params['filterConfidence']:
            df = df.filter(df["confidence"] > self.params['filterConfidence'])

        # If major/minor chord aggregation selected
        if self.majmin_agg:
            chord_map = {"Cmaj":"Cmaj","Cmaj7":"Cmaj","Cmin":"Cmin","Cmin7":"Cmin","C7":"Cmaj", \
                        "Dbmaj":"Dbmaj","Dbmaj7":"Dbmaj","Dbmin":"Dbmin","Dbmin7":"Dbmin","Db7":"Dbmaj",
                        "Dmaj":"Dmaj","Dmaj7":"Dmaj","Dmin":"Dmin","Dmin7":"Dmin","D7":"Dmaj",
                        "Ebmaj":"Ebmaj","Ebmaj7":"Ebmaj","Ebmin":"Ebmin","Ebmin7":"Ebmin","Eb7":"Ebmaj",
                        "Emaj":"Emaj","Emaj7":"Emaj","Emin":"Emin","Emin7":"Emin","E7":"Emaj",
                        "Fmaj":"Fmaj","Fmaj7":"Fmaj","Fmin":"Fmin","Fmin7":"Fmin","F7":"Fmaj",
                        "Gbmaj":"Gbmaj","Gbmaj7":"Gbmaj","Gbmin":"Gbmin","Gbmin7":"Gbmin","Gb7":"Gbmaj",
                        "Gmaj":"Gmaj","Gmaj7":"Gmaj","Gmin":"Gmin","Gmin7":"Gmin","G7":"Gmaj",
                        "Abmaj":"Abmaj","Abmaj7":"Abmaj","Abmin":"Abmin","Abmin7":"Abmin","Ab7":"Abmaj",
                        "Amaj":"Amaj","Amaj7":"Amaj","Amin":"Amin","Amin7":"Amin","A7":"Amaj",
                        "Bbmaj":"Bbmaj","Bbmaj7":"Bbmaj","Bbmin":"Bbmin","Bbmin7":"Bbmin","Bb7":"Bbmaj",
                        "Bmaj":"Bmaj","Bmaj7":"Bmaj","Bmin":"Bmin","Bmin7":"Bmin","B7":"Bmaj"
                        }
            # User defined function to get key values (chords) from nested structure in dataframe, map to chord agg
            getKeysUDF = F.udf(lambda x: list(set({chord_map[k] for k,v in x.asDict().items() if (v != None) and (v > f_ratio)})),ArrayType(StringType()))
            # Apply UDF and select only chord and id cols
            df = df.withColumn("chordItems",getKeysUDF(df['chordRatio'])).select("_id","chordItems")
        else:
            if self.type_fi == 'frequent':
                # User defined function to get key values (chords) from nested structure in dataframe and filter below value
                getKeysUDF = F.udf(lambda x: list({k for k,v in x.asDict().items() if (v != None) and (v > f_ratio)}),ArrayType(StringType()))
                # Apply UDF and select only chord and id cols
                df = df.withColumn("chordItems",getKeysUDF(df['chordRatio'])).select("_id","chordItems")
            if self.type_fi == 'sequential':
                # Chunk data into individual pieces
                def getSeq(items):
                    return [[i['label'] for i in items[n:n+1]] for n in range(len(items))]

                getKeysUDF = F.udf(getSeq,ArrayType(ArrayType(StringType())))
                # Apply UDF and select only chord and id cols
                df = df.withColumn("chordSequence",getKeysUDF(df['chordSequence'])).select("_id","chordSequence")

        # Join metadata
        def getMeta(_id,tag_res):
            """
                Grab metadata from db for particular track id
            """
            # Link with metadata taken from jamendo API for tracks in db stored in seperate mongodb (restricted to my account/network details)
            try:
                r = tag_res[int(_id)]
            except:
                r = None
            return r

        # If filter params specified, join relevant metadata and filter
        if self.tag_filter:
            tag_name = self.tag_filter['tag_name']
            tag_val = self.tag_filter['tag_val']
            # Get metadata for genre tags to pass to udf, saves having to create a new db connection for every row
            # Resulting filtered selection should be small enough to not have to worry
            with MongoClient(os.environ['MSC_MONGO_PERSONAL_URI']) as client:
                col = client.jamendo.songMetadata
                tag_res = col.find({"musicinfo.tags."+tag_name:tag_val},{"musicinfo.tags."+tag_name:1})
            # Set id to dict key for faster indexing
            tag_res = {int(t['_id']):t['musicinfo']['tags'][tag_name] for t in tag_res}
            # Join metadata
            def getMetaUDF(tag_res):
                return F.udf(lambda x: getMeta(x,tag_res),ArrayType(StringType()))
            # Apply UDF
            df = df.withColumn(tag_name,getMetaUDF(tag_res)('_id'))
            # Filter so only rows with filtered genre category is present
            df = df.na.drop()

        #df = df.cache()

        return df


class SparkFrequentItemsetsFPG(ChordLoader):
    """
    Apply FPGrowth frequent itemset mining algorithm from Spark ML lib to chord data

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
    tag_filter : dict, optional
        Filter the dataframe by metadata tags - in the form {'tag_name':'genres','tag_val':'jazz'}
    majmin_agg : bool
        Aggregate by maj/min chords

    """

    def __init__(self,spark,limit=None,params={"minSupport":0.2, "minConfidence":0.5,"filterRatio":None,"filterConfidence":None},tag_filter=None,majmin_agg=False):
        ChordLoader.__init__(self,spark,params=params,limit=limit,tag_filter=tag_filter,majmin_agg=majmin_agg,type_fi='frequent')

    def _run_FPGrowth(self,df):
        # Apply spark ml libs FP-growth algorithm for frequent itemset mining
        fpGrowth = FPGrowth(itemsCol="chordItems", minSupport = self.params["minSupport"], minConfidence=self.params["minConfidence"])
        model = fpGrowth.fit(df)
        return model

    def get_itemsets(self):
        n_items = self.df.count()
        self.model = self._run_FPGrowth(self.df)
        # Add support % val
        itemsets = self.model.freqItemsets.withColumn("supportPc",self.model.freqItemsets['freq']/n_items)
        return itemsets.toPandas()


class SparkFrequentItemsetsSON(ChordLoader):
    """
    Implementation of the SON algorithm - 
    
    "Savasere, A., Omiecinski, E. & Navathe, S. B., 1995. 
    An Efficient Algorithm for Mining Association Rules in Large Databases. s.l., 
    Proceedings of the 21st International Conference on Very Large Data Bases."

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
    tag_filter : dict, optional
        Filter the dataframe by metadata tags - in the form {'tag_name':'genres','tag_val':'jazz'}
    majmin_agg : bool
        Aggregate by maj/min chords

    """
    def __init__(self,spark,params={"minSupport":0.2,"filterRatio":None,"filterConfidence":None},limit=None,tag_filter=None,majmin_agg=False):
        ChordLoader.__init__(self,spark,params=params,limit=limit,tag_filter=tag_filter,majmin_agg=majmin_agg,type_fi='frequent')


    def get_itemsets(self):
        """
            MapReduce calculation of frequent itemsets

            Returns
            -------
            frequent_itemsets : list[tuple]
                Key value pairs of frequent itemsets with support value
        """
        # Apriori algorithm implementation for frequent itemsets
        def apriori(part,support):
            frequent_itemsets = []
            # Init combination length
            n = 1
            # Get chord from spark Row items
            part = [row['chordItems'] for row in part]
            while(True):
                # Init counter
                cnt = Counter()
                # Iterate over items in RDD
                for row in part:
                    # Count combinations
                    for comb in combinations(row,n):
                        cnt[comb] += 1
                # Filter by support value threshold
                k_fi = [(k,v) for k,v in cnt.items() if v > support]
                # Filter data
                # Get keys from filtered k length frequent itemsets
                item_keys = [k[0] for k in k_fi]
                item_set = set(chain(*item_keys))
                # Filter out items not in frequent itemsets
                part = [list(set(row).intersection(item_set)) for row in part]
                # Remove items with length 0
                part = list(filter(lambda x: len(x)>0,part))
                # If frequent sets still present add to fi list else break
                if len(part) > 0:
                    frequent_itemsets += k_fi
                    n += 1
                else:
                    break
            return frequent_itemsets

        # Convert dataframe to rdd
        chord_rdd = self.df.select(self.df['chordItems']).rdd
        print(f"N Partitions: {chord_rdd.getNumPartitions()}")
        # Support threshold determined by no. partitions
        s = self.params['minSupport']*chord_rdd.count()
        ps = s/chord_rdd.getNumPartitions()
        # 1st map function, generate candidate itemsets
        itemset_kv = dict(chord_rdd.mapPartitions(lambda x: apriori(x,ps)).reduceByKey(add).map(lambda x: (x[0],0)).collect())

        def count_sets(part,sets):
            for row in part:
                row = row['chordItems']
                for freq_set in sets:
                    if set(freq_set).issubset(set(row)):
                        sets[freq_set] += 1
            return sets.items()

        # Count the sets present in data from candidate list
        frequent_itemsets = chord_rdd.mapPartitions(lambda x: count_sets(x,itemset_kv)) \
                                     .reduceByKey(add)
        # Filter by min support value
        frequent_itemsets = frequent_itemsets.filter(lambda x: x[1]>s)

        return frequent_itemsets.collect()


class SparkFrequentItemsetsPrefixSpan(ChordLoader):
    """
        Run spark implementation of PrefixSpan algorithm to generate frequent sequences
    """

    def __init__(self,spark,params={"minSupport":0.2,"filterRatio":None,"filterConfidence":None},limit=None,tag_filter=None,majmin_agg=False):
        ChordLoader.__init__(self,spark,params=params,limit=limit,tag_filter=tag_filter,majmin_agg=majmin_agg,type_fi='sequential')

    def get_itemsets(self):
        n_items = self.df.count()
        prefixSpan = PrefixSpan(minSupport=self.params["minSupport"],maxPatternLength=5,maxLocalProjDBSize=32000000,sequenceCol="chordSequence")
        freq_sequence = prefixSpan.findFrequentSequentialPatterns(self.df)
        # Add support % val
        itemsets = freq_sequence.withColumn("supportPc",freq_sequence['freq']/n_items)
        return itemsets.toPandas()