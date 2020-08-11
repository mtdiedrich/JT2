from sklearn.feature_extraction.text import TfidfVectorizer

from sympy.solvers import solve
from sympy import Symbol

import pandas as pd

import db_interface
import metrics


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
    return df


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
    # Can this function and show_distribution be written in such a way that
    # if-else is a function that takes operation as its own function? Hence
    # both call same function for if-else logic, but use diff function as
    # argument for operation
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
    episode['ResultValues'] = episode['Result'] * episode['Attempt']
    batting_average = sum(episode['ResultValues']) / len(episode)
    return [ep_id, coryat, batting_average]


def by_episode():
    res = db_interface.get_table('RESULTS')
    corpus = db_interface.get_table('CORPUS')
    df = res.merge(corpus, on='ID')
    ids = list(set(list(df['EpisodeID'].values)))
    dfs = [df[df['EpisodeID'] == i] for i in ids]
    dfs.append(df)
    new_columns = ['EpisodeID', 'Cryt', 'BA']
    df = pd.DataFrame([get_episode_stats(d) for d in dfs], columns=new_columns)
    df['Upper Bound BA'] = df['BA']
    df['Upper Bound BA'] += df['BA'] * (1 - df['Upper Bound BA'])
    df['Upper Bound BA'] += df['BA'] * (1 - df['Upper Bound BA'])
    df['Proj BA'] = ((df['BA'] + 1) * (df['Upper Bound BA'] + 1))**.5 - 1
    return df


def comparative_performance():
    df = get_full_results()
    grp = df.groupby(['EpisodeID', 'Round'])
    data = []
    for key, item in grp:
        t_bat = sum(item['Attempt'] * item['Result'])/len(item)
        m_bat = metrics.get_batting_average(item)
        x = Symbol('x')
        i_bat = solve(x**3 - 3*x**2 + 3*x - m_bat, x)[0]
        # proj is based on some back-of-the-napkin math. the first player to
        # buzz-in gets the answer right approx. 4/5 of the time
        prj = m_bat**2
        grade = t_bat / m_bat
        sub = item['SUBMITTED'].values[0]
        ex = item['Extra'].values[0]
        data.append([sub, key[0], key[1], t_bat, m_bat, i_bat, prj, grade, ex])
    cols = ['SUBMITTED', 'EpisodeID', 'Round', 'PERF', 'TEAM BAT', 'IID BAT',
            'PROJ', 'GRADE', 'Extra']
    df = pd.DataFrame(data, columns=cols)
    df = df.sort_values('SUBMITTED', ascending=False)
    return df
