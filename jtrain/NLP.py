from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from pipeline import db_interface

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import tqdm

import topics


def get_weakness_words():
    '''Returns DataFrame of answers + relevant words for weakest classified topic'''
    corpus = db_interface.get_table('CORPUS')
    classifications = NLP.get_classifications(corpus)

    relevant = classifications[classifications['Classification']=='composer']
    df = corpus[corpus['Answer'].isin(relevant['Key'].values)]

    docs = []
    labels = []
    for k, i in df.groupby('Answer'):
        labels.append(k)
        docs.append(' '.join(i['Question'].values))

    
    config = {
        'strip_accents': None,
        'binary': False,
        'sublinear_tf': True
        }

    tfidf_df = NLP.get_tfidf_df(docs, labels, config)
    for c in tfidf_df.columns:
        col = tfidf_df[c]
        print(col.sort_values(ascending=False).head(10))
        print()


def get_classifications(df):
    docs_df = df_to_documents(df, 'Answer', 'Question')
    docs_df = docs_df[docs_df['Length'] > 3]
    docs_df = docs_df.sort_values('Length')
    keys = docs_df['Key'].values
    docs = docs_df['Document'].values
    tfidf_df = get_tfidf_df(docs, keys, sublinear_tf=False)
    cs = [tfidf_df[c].sort_values(ascending=False).index[0] for c in keys]
    docs_df['Classification'] = cs
    df = docs_df[['Key', 'Classification', 'Length']]
    return df 


def df_to_documents(df, group_by, join_by):
    grp = df.groupby(group_by)
    data = [[k, ' '.join(i[join_by].values), len(i)] for k, i in grp]
    df = pd.DataFrame(data, columns=['Key', 'Document', 'Length'])
    df = df[df['Key']!='=']
    df = df.sort_values('Length', ascending=False)
    return df


def get_tfidf_df(documents, labels, binary=False, sublinear_tf=False, strip_accents=None):
    vct = TfidfVectorizer(strip_accents=strip_accents, binary=binary, sublinear_tf=sublinear_tf)
    sparse_x = vct.fit_transform(documents)
    x = sparse_x.todense()
    features = vct.get_feature_names()
    tfidf_df_inv = pd.DataFrame(x, index=labels, columns=features)
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
