from pipeline import download, db_interface

import pandas as pd

import wikipedia
import sqlite3
import click
import time
import sys

import analysis
import visualization
import topics
import NLP

def get_study_df_for_worst_topic():
    corpus = db_interface.get_table('CORPUS')
    classifications = NLP.get_classifications(corpus)
    comparison = analysis.correct_topic_comparison()
    worst = comparison['DIFF'].index[-1]

    relevant = classifications[classifications['Classification']==worst]
    df = corpus[corpus['Answer'].isin(relevant['Key'].values)]

    answer_map = {a: a for a in df['Answer'].values}
    answer_map['Mozart'] = 'Wolfgang Amadeus Mozart'
    answer_map['Wolfgang A. Mozart'] = 'Wolfgang Amadeus Mozart'
    answer_map['W.A. Mozart'] = 'Wolfgang Amadeus Mozart'
    answer_map['(Richard) Wagner'] = 'Richard Wagner'
    answer_map['Wagner'] = 'Richard Wagner'
    answer_map['Tchaikovsky'] = 'Pyotr Tchaikovsky'
    answer_map['(Giuseppe) Verdi'] = 'Giuseppe Verdi'
    answer_map['Verdi'] = 'Giuseppe Verdi'
    answer_map['Chopin'] = 'Frederic Chopin'
    answer_map['(Johann Sebastian) Bach'] = 'Johann Sebastian Bach'
    answer_map['(Aaron) Copland'] = 'Aaron Copland'
    answer_map['(Franz) Schubert'] = 'Franz Schubert'
    answer_map['(Felix) Mendelssohn'] = 'Felix Mendelssohn'
    answer_map['(Robert) Schumann'] = 'Robert Schumann'
    answer_map['(Stephen) Foster'] = 'Stephen Foster'
    answer_map['Handel'] = 'George Frideric Handel'
    answer_map['Rossini'] = 'Gioachino Rossini'

    df = df.copy()
    df['Answer'] = [answer_map[a] for a in df['Answer'].values]

    df = df.sort_values('Answer')
    docs = []
    labels = []
    for k, i in df.groupby('Answer'):
        labels.append(k)
        docs.append(' '.join(i['Question'].values))
    sub_tfidf_df = NLP.get_tfidf_df(docs, labels, sublinear_tf=True)
    context_dfs = []
    for l in labels:
        label_words = sub_tfidf_df[l].sort_values()**4
        temp_df = pd.DataFrame([label_words, label_words.cumsum()/label_words.sum()]).T
        temp_df.columns = ['SIG', 'CUMUL']
        temp_df = temp_df[temp_df['CUMUL'] > .5]
        use_df = df[df['Answer']==l]
        dfs = []
        for i in temp_df.index:
            word_df = use_df[use_df['Question'].str.lower().str.contains(i)]
            word_df = word_df.copy()
            word_df['Word'] = i
            dfs.append(word_df)
        context_df = pd.concat(dfs)
        context_df['Topic'] = worst
        context_df = context_df[['Topic', 'Question', 'Answer', 'Word']]
        context_dfs.append(context_df)
    full_df = pd.concat(context_dfs)
    return full_df
