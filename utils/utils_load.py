'''
data.py
---
This module provide data loading functions using PySpark
'''

from pprint import pprint

import findspark
import pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.session import SparkSession


def conf_pyspark():
    """
    configure and initiate PySpark
    input: none
    output: sc, spark
    """
    findspark.init()

    # start a Spark context and session
    conf = SparkConf()
    conf.setAppName('local')
    conf.set('spark.driver.cores', 6) # set processor number
    conf.set('spark.driver.memory', '62g') # set memory size
    conf.set('spark.driver.maxResultSize', '4g')

    # for avoid import error caused by udf in utils files
    myPyFiles = ['../utils/utils_preplot.py']


    try:
        sc.stop()
        sc = SparkContext(conf=conf, pyFiles=myPyFiles)
    except:
        sc = SparkContext(conf=conf, pyFiles=myPyFiles)

    # passing spark context ot sql module
    spark = SparkSession(sc)

    # print configurations
    pprint(spark.sparkContext._conf.getAll())

    return sc, spark


def load_dataset(dataset, spark):
    """
    load dataset to a dataframe and retrun the dataframe.
    input: dataset:
                   'papers_pas' the raw dataset
                   'dataset' the clean dataset
           spark: spark session
    output: dataframe loaded, if dataset is not exist, return -1
    """


    if dataset == 'papers_past':

        path = r'../data/papers_past'

        data_schema = StructType([
            StructField('id', IntegerType()),
            StructField('url', StringType()),
            StructField('publisher', StringType()),
            StructField('time', StringType()),
            StructField('title', StringType()),
            StructField('content', StringType())
        ])

        df = (
            spark.read.format("com.databricks.spark.csv")
            .option("header", "false")
            .option("inferSchema", "false")
            .option("delimiter", "\t")
            .schema(data_schema)
            .load(path)
        )

    elif dataset == 'dataset':

        path = r'../data/dataset'

        data_schema = StructType([
            StructField('id', IntegerType()),
            StructField('publisher', StringType()),
            StructField('region', StringType()),
            StructField('date', DateType()),
            StructField('ads', BooleanType()),
            StructField('title', StringType()),
            StructField('content', StringType())
        ])

        df = (
            spark.read.format("com.databricks.spark.csv")
            .option("header", "false")
            .option("inferSchema", "false")
            .schema(data_schema)
            .load(path)
            .orderBy('id')
        )

    elif dataset == 'dev':

        path = r'../data/dataset_dev'

        data_schema = StructType([
            StructField('id', IntegerType()),
            StructField('publisher', StringType()),
            StructField('region', StringType()),
            StructField('date', DateType()),
            StructField('ads', BooleanType()),
            StructField('title', StringType()),
            StructField('content', StringType())
        ])

        df = (
            spark.read.format("com.databricks.spark.csv")
            .option("header", "false")
            .option("inferSchema", "false")
            .schema(data_schema)
            .load(path)
            .orderBy('id')
        )

    else:

        print('Wrong dataset, only "papers_past" and "dataset" are avalible.')
        df = -1

    return df
