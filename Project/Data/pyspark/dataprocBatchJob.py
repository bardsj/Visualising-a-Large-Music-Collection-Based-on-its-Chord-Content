import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType,StringType
from pyspark.ml.fpm import FPGrowth, PrefixSpan
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
    def __init__(self,spark,meta_db_uri,params,limit,tag_filter,majmin_agg=False,type_fi='frequent'):
        self.limit = limit
        self.spark = spark
        self.params = params
        self.tag_filter = tag_filter
        self.majmin_agg = majmin_agg
        self.type_fi = type_fi
        self.meta_db_uri = meta_db_uri
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
            with MongoClient(self.meta_db_uri) as client:
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

    def __init__(self,spark,meta_db_uri,limit=None,params={"minSupport":0.2, "minConfidence":0.5,"filterRatio":None,"filterConfidence":None},tag_filter=None,majmin_agg=False):
        ChordLoader.__init__(self,spark,meta_db_uri,params=params,limit=limit,tag_filter=tag_filter,majmin_agg=majmin_agg,type_fi='frequent')

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


class SparkFrequentItemsetsPrefixSpan(ChordLoader):
    """
        Run spark implementation of PrefixSpan algorithm to generate frequent sequences
    """

    def __init__(self,spark,meta_db_uri,params={"minSupport":0.2,"filterRatio":None,"filterConfidence":None},limit=None,tag_filter=None,majmin_agg=False):
        ChordLoader.__init__(self,spark,meta_db_uri,params=params,limit=limit,tag_filter=tag_filter,majmin_agg=majmin_agg,type_fi='sequential')

    def get_itemsets(self):
        n_items = self.df.count()
        prefixSpan = PrefixSpan(minSupport=self.params["minSupport"],maxPatternLength=5,maxLocalProjDBSize=10000,sequenceCol="chordSequence")
        freq_sequence = prefixSpan.findFrequentSequentialPatterns(self.df)
        # Add support % val
        itemsets = freq_sequence.withColumn("supportPc",freq_sequence['freq']/n_items)
        return itemsets.toPandas()

##########################################


import pyspark
import pickle
import time
import sys
import json
from itertools import chain
import argparse


def run_pattern(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--chord_db_uri',metavar='chord_db_uri',required=True)
    parser.add_argument('--meta_db_uri',metavar='meta_db_uri',required=True)

    args = parser.parse_args(argv)

    # Spark context
    sc = pyspark.SparkContext.getOrCreate()
    spark = pyspark.sql.SparkSession.builder \
        .config("spark.mongodb.input.uri", args.chord_db_uri)\
        .config("spark.executor.heartbeatInterval","3600s")\
        .getOrCreate()

    params_fpg = {"minSupport": 0.01, "minConfidence": 1,"filterRatio":0.05,"filterConfidence":0.6}
    params_ps = {"minSupport": 0.1, "minConfidence": 1,"filterRatio":0.05,"filterConfidence":0.6}

    st = time.time()

    write_results = []

    #for i,genre in enumerate(['pop','rock','electronic','hiphop','jazz','indie','filmscore','classical','chillout','ambient','folk','metal','latin','rnb','reggae','punk','country','house','blues',None]):
    for i,genre in enumerate(['pop','rock','electronic','hiphop','jazz','classical','ambient','folk','metal','latin','rnb','reggae','house','blues',None]):
        if genre:
            tag_filt = {"tag_name":"genres","tag_val":genre}
        else:
            tag_filt = None

        items = SparkFrequentItemsetsPrefixSpan(spark,args.meta_db_uri,limit=None,params=params_ps,tag_filter=tag_filt,majmin_agg=False)
        itemsets = items.get_itemsets()
        count = items.getDataframeCount()
        # Convert to dict for storage
        itemsets['sequence'] = itemsets['sequence'].apply(lambda x: list(chain(*x)))
        itemsets.rename(columns={'sequence':'items'},inplace=True)
        itemsets = itemsets.to_dict()

        write_results.append({
            "_id":str(i).zfill(4)+"-"+str(params_ps['minSupport'])+"-"+str(params_ps['filterRatio'])+"-"+str(params_ps['filterConfidence'])+"-"+str(False)+"s",
            "filter_params":params_ps,
            "tag_params":tag_filt,
            "itemsets":itemsets,
            "majmin_agg":False,
            "dfCount":count,
            "fi_type":'sequential'
        })


        for majmin_agg in [False,True]:
            items = SparkFrequentItemsetsFPG(spark,args.meta_db_uri,limit=None,params=params_fpg,tag_filter=tag_filt,majmin_agg=majmin_agg)
            itemsets = items.get_itemsets()
            count = items.getDataframeCount()
            # Convert to dict for storage
            itemsets = itemsets.to_dict()

            write_results.append({
                "_id":str(i).zfill(4)+"-"+str(params_fpg['minSupport'])+"-"+str(params_fpg['filterRatio'])+"-"+str(params_fpg['filterConfidence'])+"-"+str(majmin_agg)+"f",
                "filter_params":params_fpg,
                "tag_params":tag_filt,
                "itemsets":itemsets,
                "majmin_agg":majmin_agg,
                "dfCount":count,
                "fi_type":'frequent'
            })

    try:
        with open("itemsets.json","w+") as filename:
            json.dump(write_results,filename)
        
        from subprocess import call
        call(["gsutil","cp","itemsets.json","gs://fi_results"])
    except:
        pass

    try:
        with open("gs://fi_results/itemsets.json","w+") as filename:
            json.dump(write_results,filename)
    except:
        pass



    print("Total time: " + str(time.time()-st))


if __name__ == "__main__":
    run_pattern(sys.argv[1:])