import pandas as pd
import numpy as np
try:
    from src import download, db_interface, NLP, mine_sn
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn 


def show_distribution(mean, std, att='Coryat'):
    '''For given mean, std, display normal distribution'''
    if att = 'Knowledge':
        pass
    elif att = 'Batting Average':
        pass
    else:
        pass


def show_performance_over_time(att='Coryat'):
    '''Display line graph of performance over time'''
    # Really needs RESULTS table to include submission time
    # For now, can operate based on order in DB, but this isn't robust
    # Can this function and show_distribution be written in such a way that if-else is a function that takes operation as its own function?
    # Hence, both call same function for if-else logic, but use diff function as argument for operation
     if att = 'Knowledge':
        pass
    elif att = 'Batting Average':
        pass
    else:


def by_corpus():
    res = db_interface.get_table('RESULTS')
    corpus = db_interface.get_table('CORPUS')
    df = res.merge(corpus, on='ID')
    ids = df[['EpisodeID', 'Round']].drop_duplicates()
    know = df['Result'].sum()/len(df)
    df = df[df['Attempt'].astype(bool)]
    df['Calc'] = df['Value'] * (df['Result'] * 2 - 1)
    coryat = df['Calc'].sum() * 600 / len(ids)
    batting_average = df['Result'].sum()/len(df)
    data = {'Coryat': coryat, 'Knowledge': know, 'Batting Average': batting_average}
    return data


def by_episode():
    # Really, this function should calculate call the above function to return analysis on each individual episode
    # Then perform analysis on corpus
    # And return all data together
    # renamed to something like performance_metrics()
    res = db_interface.get_table('RESULTS')
    corpus = db_interface.get_table('CORPUS')
    df = res.merge(corpus, on='ID')
    ids = list(set(list(df['EpisodeID'].values)))
    dfs = [df[df['EpisodeID']==i] for i in ids]
    data = []
    for i in ids:
        temp = df[df['EpisodeID']==i].copy()
        know = temp['Result'].sum()/len(temp)
        temp = temp[temp['Attempt']==1]
        temp['Calc'] = temp['Value'] * (temp['Result'] * 2 - 1)
        coryat = temp['Calc'].sum() * 600
        batting_average = temp['Result'].sum()/len(temp)
        data.append([i, coryat, know, batting_average])
    crp = by_corpus()
    data.append(['CORPUS', crp['Coryat'], crp['Knowledge'], crp['Batting Average']])
    df = pd.DataFrame(data, columns=['ID', 'Proj Coryat', 'Knowledge', 'Batting Average'])
    return df


def perform_analysis():
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
