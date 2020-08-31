from sklearn.feature_extraction.text import TfidfVectorizer

from collections import Counter

import pandas as pd
import numpy as np

import sqlite3
import tqdm

try:
    from src import db_interface, NLP
except ModuleNotFoundError:
    import db_interface, NLP

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
    
    

    """
    tfidf_config = {k: v for k, v in zip(keys, [None, False, True])}
    tfidf_df = NLP.get_tfidf_df(to_transform, answers, tfidf_config)
    tfidf_results = NLP.top_tfidf_results(tfidf_df, 10)
    tfidf_results['words'] = [' | '.join(list(v)) for v in tfidf_results.values]

    df = categories.join(tfidf_results, how='outer')
    conn = sqlite3.connect('./data/JT2')
    df.to_sql('TFIDF', conn, if_exists='replace', index=True)
    df = db_interface.get_table('TFIDF')
    df.index = df['index']
    df = df.drop('index', axis=1)
    return df
    """


def answer_counts(df = db_interface.get_table('CORPUS')):
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
