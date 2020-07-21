import pandas as pd
import numpy as np
import tqdm

try:
    from src import download, db_interface, analysis, metrics
except ModuleNotFoundError:
    import download, db_interface, analysis, metrics

def get_years_change():
    df = corpus_performance()
    df = split_dates(df)
    years = sorted(list(set(list(df['Y'].values))))
    data = [[y] + corpus_distribution(df[df['Y']==y]) for y in years]
    df = pd.DataFrame(data, columns=['Year', 'Cryt M', 'Cryt S', 'Bat M', 'Bat S'])
    return df


def split_dates(df):
    df['Y'] = df['Date'].apply(lambda x: x.split('-')[0])
    df['M'] = df['Date'].apply(lambda x: x.split('-')[1])
    df['D'] = df['Date'].apply(lambda x: x.split('-')[2])
    return df


def corpus_distribution(df):
    cryt_mean = df['Cryt'].mean()
    cyt_std = df['Cryt'].std()
    bat_mean = df['Bat'].mean()
    bat_std = df['Bat'].std()
    return [cryt_mean, cyt_std, bat_mean, bat_std]


def corpus_performance(df=db_interface.get_table('CORPUS')):
    dfs = [df[df['EpisodeID']==e] for e in tqdm.tqdm(list(set(list(df['EpisodeID'].values))))]
    performances = [calculate_team_performance(e) for e in tqdm.tqdm(dfs)]
    df = pd.DataFrame(performances, columns=['Date', 'EpisodeID', 'Cryt', 'Bat'])
    return df


def calculate_team_performance(df):
    date = list(set(list(df['Date'].values)))[0]
    episode = list(set(list(df['EpisodeID'].values)))[0]
    cryt, bat = metrics.get_episode_measure(df)
    return [date, episode, cryt, bat]
