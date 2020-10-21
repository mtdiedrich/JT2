from sklearn.feature_extraction.text import TfidfVectorizer
from pipeline import db_interface
from analysis import NLP

from collections import Counter

import pandas as pd
import numpy as np

import sqlite3
import tqdm


def topic_distances():
    df = answer_counts()
    df = df[df['Length'] > 100]
    to_transform = df['Doc'].values
    answers = df['Answer'].values
    keys = ['strip_accents', 'binary', 'sublinear_tf']
    tfidf_config = {k: v for k, v in zip(keys, [None, False, True])}
    tfidf_df = NLP.get_tfidf_df(to_transform, answers, tfidf_config)
    corr = tfidf_df.corr()
    print(corr)


def analyze_topics():
    df = answer_counts()
    to_transform = df['Doc'].values
    answers = df['Answer'].values
    keys = ['strip_accents', 'binary', 'sublinear_tf']

    base_config = {k: v for k, v in zip(keys, [None, False, False])}
    base_tfidf_df = NLP.get_tfidf_df(to_transform, answers, base_config)
    categories = NLP.top_tfidf_results(base_tfidf_df, 1)
    categories.columns = ['category']
    print(categories)
    

def answer_counts(df):
    df = db_interface.get_table('CORPUS')
    df = df[df['Answer']!='=']
    grp = df.groupby('Answer')
    data = []
    for key, item in tqdm.tqdm(grp):
        idx = key
        length = len(item)
        txt = ' '.join(list(item['Question'].values))
        data.append([idx, length, txt])
    df = pd.DataFrame(data, columns=['Answer', 'Length', 'Doc'])
    df = df.sort_values('Length', ascending=False)
    return df
