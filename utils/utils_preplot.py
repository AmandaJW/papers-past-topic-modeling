'''
preplot.py
---
This module provide data wrangling functions using PySpark
'''

import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import *



def argmax(cols, *args):
    return [c for c, v in zip(cols, args) if v == max(args)][0]


def add_domtopic(df):
    """
    find the dominant topic of each sample/row/document
    input: dataframe of weight of each topic
    output: the raw dominant topic number dataframe
    """

    argmax_udf = lambda cols: F.udf(lambda *args: argmax(cols, *args), StringType())
    return (df
            .withColumn('domtopic',
                argmax_udf(df.columns[2:])(*df.columns[2:]))
            .withColumn('weight',
                F.greatest(*[F.col(x) for x in df.columns[2:-1]])))


def load_doctopic(f, n, spark):
    '''
    load raw doc-topic matrix file to dataframe.
    input:
        f: file path with file name
        n: topic number
    output:
        return the raw doc-topic matrix dataframe
    '''
    #print('load_doctopic')

    # generate new column names
    columns = [str(x) for x in list(range(n))]
    columns.insert(0, 'id')
    columns.insert(0, 'index')

    # load data
    df = (
        spark.read.format("com.databricks.spark.csv")
        .option("header", "false")
        .option("inferSchema", "true")
        .option("delimiter", "\t")
        .option("comment", "#")
        .load(f)
    )

    # change columns name and drop # column which is table index and useless
    return df.toDF(*columns)


def add_metadata(df_doctopic, df_meta, kind):
    #print('add_metadata')
    # add the metadata to doc-topic matrix
    if kind == 'year':
        k = 'yyyy'
    elif kind == 'month':
        k = 'yyyy-MM'
    else:
        print('arg kind:{} is unknown.'.format(kind))
        return -1

    return (df_doctopic
            .join(df_meta, df_doctopic.id == df_meta.id_)
            .withColumn('year', F.date_format('date', k))
            .drop('id_')
            .drop('date')
            .orderBy('index'))


def gen_docdomtopic(df_doctopic, df_topics):
    '''
    generate dominant topics dataframe,
    add topic words colunm based on df_doctopic.
    input:
        df_doctopic: processed doc-topic matrix dataframe.
        df_topics: raw dataframe from topics words file.
    output:
        return processed dominant topics dataframe
    '''

    return (df_doctopic
            .join(df_topics, df_doctopic.domtopic == df_topics.topic)
            .select(F.col('id'),
                    F.col('region'),
                    F.col('year'),
                    F.col('domtopic'),
                    F.col('weight'),
                    F.col('words')))


def gen_avgweight(df_doctopic):
    '''
    generate dataframe of average weight of topics.
    input:
        df_doctopic: processed doc-topic matrix dataframe.
    output:
        return year average weight topics dataframe
    '''
    #print('gen_avgweight')

    return (df_doctopic
            .drop('index')
            .drop('id')
            .drop('domtopic')
            .drop('region')
            .drop('weight')
            .groupBy('year')
            .avg()
            .orderBy('year'))



def preplot(df_doctopic, df_meta, df_topics, kind):
    '''
    generate dataframes to plot
    input:
        df_doctopic: doc topic matrix
        df_meta:  metadata from dataset dataframe.
        df_topics: topic words dataframe.
    return:
        dominant topics dataframe
        year average weight topics dataframe
    '''
    #print('preplot')

    topic_number = df_topics.count()

    #df_doctopic = load_doctopic(f, n, spark)

    df_doctopic = add_domtopic(df_doctopic)

    df_doctopic = add_metadata(df_doctopic, df_meta, kind)

    df_docdomtopic = gen_docdomtopic(df_doctopic, df_topics)

    df_avgweight = gen_avgweight(df_doctopic)

    return df_docdomtopic, df_avgweight
