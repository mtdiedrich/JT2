from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import tqdm

def get_tfidf_df(documents, labels, config):
    strp_accnts = config['strip_accents']
    bnry = config['binary']
    sblnr_tf = config['sublinear_tf']
    vct = TfidfVectorizer(strip_accents=strp_accnts, binary=bnry, sublinear_tf=sblnr_tf)
    sparse_X = vct.fit_transform(documents)
    X = sparse_X.todense()
    features = vct.get_feature_names()
    tfidf_df_inv = pd.DataFrame(X, index=labels, columns=features)
    tfidf_df = tfidf_df_inv.T
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
