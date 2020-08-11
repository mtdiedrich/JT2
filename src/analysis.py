from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

from sympy.solvers import solve
from sympy import Symbol

from matplotlib import pyplot as plt

from scipy.stats import norm, gmean

import pandas as pd
import numpy as np
import string
try:
    from src import db_interface, metrics, NLP, topics
except ModuleNotFoundError:
    import db_interface, metrics, NLP, topics


def foo():
    df = db_interface.get_table('CORPUS')
    labels = df['Answer'].values
    docs = df['Question'].values
    config = {
            'strip_accents': None, 
            'binary': True, 
            'sublinear_tf': True
            }
    tfidf_df = NLP.get_tfidf_df(docs, labels, config).T
    Y = tfidf_df.index
    X = tfidf_df.values
    model = LogisticRegression()
    model.fit(X, Y)
    df = df.sample(frac=1)
    cat = df['Category'].values[0]
    epid = df['EpisodeID'].values[0]
    df = df[df['Category']==cat]
    df = df[df['EpisodeID']==epid]
    df.index = df['Answer']
    
    data = df.merge(tfidf_df, left_on=df.index, right_on=tfidf_df.index)
    data.index = data['key_0']
    data = data[data.columns[13:]]
    df['p'] = model.predict(data.values)
    print(df)


def get_full_results():
    res = db_interface.get_table('RESULTS')
    corpus = db_interface.get_table('CORPUS')
    df = res.merge(corpus, on='ID')
    return df 


def tfidf(column='Category'):
    df = get_full_results() 
    right = df[df['Result'].astype(bool)]
    wrong = df[~df['Result'].astype(bool)]
    right_corpus = ' '.join([r.lower() for r in right['Category'].values])
    wrong_corpus = ' '.join([w.lower() for w in wrong['Category'].values])
    vct = TfidfVectorizer(sublinear_tf=True)
    data = vct.fit_transform([wrong_corpus, right_corpus]).todense()
    df = pd.DataFrame(data, columns=vct.get_feature_names()).T
    df['Strength'] = df[1] - df[0]
    df = df.sort_values('Strength', ascending=False)
    return  df


def show_distribution(mean, std, att='Coryat'):
    '''For given mean, std, display normal distribution'''
    if att == 'Knowledge':
        return
    elif att == 'Batting Average':
        return
    else:
        return


def show_performance_over_time(att='Coryat'):
    '''Display line graph of performance over time'''
    # Really needs RESULTS table to include submission time
    # For now, can operate based on order in DB, but this isn't robust
    # Can this function and show_distribution be written in such a way that if-else is a function that takes operation as its own function?
    # Hence, both call same function for if-else logic, but use diff function as argument for operation
    if att == 'Knowledge':
        return
    elif att == 'Batting Average':
        return
    else:
        return


def get_coryat(df, divisor=1):
    temp = df.copy()
    temp = temp[temp['Attempt'].astype(bool)]
    temp['Result'] = temp['DailyDouble'] + temp['Result'] * 2 - 1
    temp['Result'] = temp['Result'].apply(lambda x: 1 if x > 1 else x)
    coryat = sum(temp['Result'] * temp['Value'] * 600)
    return coryat//divisor


def get_episode_stats(episode):
    ids = list(set(list(episode['EpisodeID'].values)))
    if len(ids) > 1:
        ep_id = 'CORPUS'
        coryat = get_coryat(episode, len(ids))
    else:
        ep_id = ids[0]
        coryat = get_coryat(episode)
    batting_average = sum(episode['Result'] * episode['Attempt']) / len(episode)
    return [ep_id, coryat, batting_average]


def by_episode():
    res = db_interface.get_table('RESULTS')
    corpus = db_interface.get_table('CORPUS')
    df = res.merge(corpus, on='ID')
    ids = list(set(list(df['EpisodeID'].values)))
    dfs = [df[df['EpisodeID']==i] for i in ids]
    dfs.append(df)
    df = pd.DataFrame([get_episode_stats(d) for d in dfs], columns = ['EpisodeID', 'Cryt', 'BA'])
    df['Upper Bound BA'] = df['BA']
    df['Upper Bound BA'] += df['BA'] * (1 - df['Upper Bound BA'])
    df['Upper Bound BA'] += df['BA'] * (1 - df['Upper Bound BA'])
    df['Proj BA'] = ((df['BA'] + 1) * (df['Upper Bound BA'] + 1))**.5 - 1
    return df


def tendencies():
    df = db_interface.get_table('RESULTS')
    print(df)
    print()

    indices = {0: 'Incorrect', 1: 'Correct'}
    print('KNOWLEDGE (correct rate)')
    knowledge = df['Result'].value_counts(normalize=True)
    knowledge.index = [indices[i] for i in knowledge.index]
    knowledge_rate = knowledge.to_dict()['Correct']
    print(knowledge_rate)
    print()

    print('SUCCESS (of attempted, correct)')
    att_df = df[df['Attempt']==1]
    att_acc = att_df['Result'].value_counts(normalize=True)
    att_acc.index = [indices[i] for i in att_acc.index]
    att_acc_rate = att_acc.to_dict()['Correct']
    print(att_acc_rate)
    print()
 
    print('WISDOM (of not attempted, not correct)')
    not_att_df = df[df['Attempt']==0]
    not_att_acc = not_att_df['Result'].value_counts(normalize=True)
    not_att_acc.index = [indices[i] for i in not_att_acc.index]
    not_att_acc_rate =  not_att_acc.to_dict()['Incorrect']
    print(not_att_acc_rate)
    print()

    indices = {0: 'Abstained', 1: 'Attempted'}
    print('CONFIDENCE (attempt rate)')
    confidence = df['Attempt'].value_counts(normalize=True)
    confidence.index = [indices[i] for i in confidence.index]
    confidence_rate = 1 - confidence.to_dict()['Attempted']
    print(confidence_rate)
    print()

    print('FEAR (of correct, not attempted)')
    corr_df = df[df['Result']==1]
    corr_att = corr_df['Attempt'].value_counts(normalize=True)
    corr_att.index = [indices[i] for i in corr_att.index]
    corr_att_rate = 1 - corr_att.to_dict()['Attempted']
    print(corr_att_rate)
    print()

    print('HUBRIS (of incorrect, attempted)')
    incorr_df = df[df['Result']==0]
    incorr_att = incorr_df['Attempt'].value_counts(normalize=True)
    incorr_att.index = [indices[i] for i in incorr_att.index]
    incorr_att_rate = incorr_att.to_dict()['Attempted']
    print(incorr_att_rate)
    print()

def comparative_performance():
    df = get_full_results()
    grp = df.groupby(['EpisodeID', 'Round'])
    data = []
    for key, item in grp:
        pers_bat = sum(item['Attempt'] * item['Result'])/len(item)
        play_bat = metrics.get_batting_average(item)
        x = Symbol('x')
        iid_bat = solve(x**3 - 3*x**2 + 3*x - play_bat, x)[0]
        #proj is based on some back-of-the-napkin math
        #essentially, the first player to buzz-in gets the answer right 4/5 of the time
        proj = play_bat**2
        grade = pers_bat / play_bat
        sub = item['SUBMITTED'].values[0]
        ex = item['Extra'].values[0]
        data.append([sub, key[0], key[1], pers_bat, play_bat, iid_bat, proj, grade, ex])
    cols = ['SUBMITTED', 'EpisodeID', 'Round', 'PERF', 'TEAM BAT', 'IID BAT', 'PROJ', 'GRADE', 'Extra']
    df = pd.DataFrame(data, columns=cols)
    df = df.sort_values('SUBMITTED', ascending=False)
    return df
