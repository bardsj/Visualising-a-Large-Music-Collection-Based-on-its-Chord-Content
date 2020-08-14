"""
Standalone script to run on cluster

"""
import pyspark
import os
import sys
import json
import argparse
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType,StringType
from pyspark.ml.fpm import FPGrowth
from collections import Counter
from itertools import combinations,chain
from operator import add
from pymongo import MongoClient

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
    def __init__(self,spark,params,limit=None,tag_filter=None,majmin_agg=False):
        self.limit = limit
        self.spark = spark
        self.params = params
        self.tag_filter = tag_filter
        self.majmin_agg = majmin_agg
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
            getKeysUDF = F.udf(lambda x: list(set({chord_map[k] for k,v in x.asDict().items() if type(v) is float})),ArrayType(StringType()))
            # Apply UDF and select only chord and id cols
            df = df.withColumn("chordItems",getKeysUDF(df['chordRatio'])).select("_id","chordItems")
        else:
            # User defined function to get key values (chords) from nested structure in dataframe and filter below value
            getKeysUDF = F.udf(lambda x: list({k for k,v in x.asDict().items() if (v != None) and (v > f_ratio)}),ArrayType(StringType()))
            # Apply UDF and select only chord and id cols
            df = df.withColumn("chordItems",getKeysUDF(df['chordRatio'])).select("_id","chordItems")

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
        ChordLoader.__init__(self,spark,params,limit,tag_filter,majmin_agg)

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

def run_fi_mining(argv):
    
    # Get script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--chord_db_uri",metavar="chord_db_uri",required=True)
    parser.add_argument("--meta_db_uri",metavar="meta_db_uri",required=True)
    args = parser.parse_args(argv)

    # Set environment variables
    os.environ['PYSPARK_SUBMIT_ARGS'] = '"--packages" "org.mongodb.spark:mongo-spark-connector_2.11:2.4.1" "--driver-memory" "4g" "pyspark-shell"'
    os.environ['MSC_CHORD_DB_URI'] = args.chord_db_uri
    os.environ['MSC_MONGO_PERSONAL_URI'] = args.meta_db_uri

    # Spark context
    sc = pyspark.SparkContext.getOrCreate()
    spark = pyspark.sql.SparkSession.builder \
        .config("spark.mongodb.input.uri", os.environ['MSC_CHORD_DB_URI'])\
        .getOrCreate()

    params = {"minSupport": 0.01, "minConfidence": 1,"filterRatio":0.05,"filterConfidence":0.6}

    write_results = []

    for i,genre in enumerate(['pop','rock','electronic','hiphop','jazz','indie','filmscore','classical','chillout','ambient','folk','metal','latin','rnb','reggae','punk','country','house','blues',None]):
        if genre:
            tag_filt = {"tag_name":"genres","tag_val":genre}
        else:
            tag_filt = None

        for majmin_agg in [False,True]:
            items = SparkFrequentItemsetsFPG(spark, None, params,tag_filter=tag_filt,majmin_agg=majmin_agg)
            itemsets = items.get_itemsets()
            count = items.getDataframeCount()
            # Get k = 2 length itemsets to calculate circular order
            ksets_circ = itemsets[itemsets['items'].str.len()==2]
            # Convert to dict for storage
            itemsets = itemsets.to_dict()

            write_results.append({
                "_id":str(i).zfill(4)+"-"+str(params['minSupport'])+"-"+str(params['filterRatio'])+"-"+str(params['filterConfidence'])+"-"+str(majmin_agg),
                "filter_params":params,
                "tag_params":tag_filt,
                "itemsets":itemsets,
                "majmin_agg":majmin_agg,
                "dfCount":count
            })


    with open("itemsets.json","w+") as filename:
        json.dump(write_results,filename)

if __name__ == "__main__":
    run_fi_mining(sys.argv[1:])