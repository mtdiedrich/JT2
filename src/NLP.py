from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import tqdm

import topics, db_interface

def get_tfidf_df(documents, labels, config):
    strp_accnts = config['strip_accents']
    bnry = config['binary']
    sblnr_tf = config['sublinear_tf']
    vct = tfidfvectorizer(strip_accents=strp_accnts, binary=bnry, sublinear_tf=sblnr_tf)
    sparse_x = vct.fit_transform(documents)
    x = sparse_x.todense()
    features = vct.get_feature_names()
    tfidf_df_inv = pd.dataframe(x, index=labels, columns=features)
    tfidf_df = tfidf_df_inv.t
    return tfidf_df


def top_tfidf_results(df, count):
    data = []
    for answer in df.columns:
        temp = df[answer].sort_values(ascending=False)
        relevant_data = temp.head(count)
        values = list(relevant_data.index)
        data.append(values)
    df = pd.DataFrame(data, index=df.columns)
    df.columns += 1
    return df


def cluster(to_transform, answers):
    keys = ['strip_accents', 'binary', 'sublinear_tf']
    tfidf_config = {k: v for k, v in zip(keys, [None, False, True])}
    tfidf_df = get_tfidf_df(to_transform, answers, tfidf_config)
    tfidf_df = tfidf_df.T
    km = KMeans(n_clusters=round(len(tfidf_df)))
    data = km.fit_transform(tfidf_df.values)
    df = pd.DataFrame(data, index=tfidf_df.index)
    df['cluster'] = [np.argmax(row) for row in df.values]
    clusters = sorted(list(set(list(df['cluster'].values))))
    grp = df.groupby('cluster')
    for c in clusters:
        temp = grp.get_group(c)[c]
        temp = temp.sort_values()
        print(temp)
        print()

def foo():
    df = db_interface.get_table('CORPUS').head(100)
    vct = TfidfVectorizer(binary=False, sublinear_tf=True)
    sparse_x = vct.fit_transform(df['Question'].values)
    x = sparse_x.todense()
    features = vct.get_feature_names()
    tfidf_df = pd.DataFrame(x, index=df['Question'].values, columns=features)
    tfidf_df['label'] = tfidf_df.index
    row_map = {row[-1]: row[:-1] for row in tfidf_df.values}
    df = df[['Category', 'Question', 'Answer']]
    df['TFIDF'] = [row_map[q] for q in df['Question'].values]

    train_X, test_X, train_Y, test_Y = train_test_split(df['TFIDF'].values, df['Answer'].values)
    train_X = [np.array(i).reshape(1,-1) for i in train_X]
    model = LogisticRegression()
    model.fit(train_X, train_Y)

    for i, j in zip(test_X, test_Y):
        print(j)
        print(model.predict(i))
        print()
