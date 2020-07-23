from sympy.solvers import solve
from sympy import Symbol

import pandas as pd
import numpy as np
import tqdm

try:
    from src import download, db_interface, analysis, metrics
except ModuleNotFoundError:
    import download, db_interface, analysis, metrics


def get_cryt_table():
    df = db_interface.get_table('CORPUS')
    grp = df.groupby('Date')
    print('Calculating CRYT')
    data = [calculate_team_performance(item) for key, item in tqdm.tqdm(grp)]
    df = pd.DataFrame(data, columns=['Date', 'EpisodeID', 'Cryt', 'Bat'])
    return df

def calculate_team_performance(df):
    date = list(set(list(df['Date'].values)))[0]
    episode = list(set(list(df['EpisodeID'].values)))[0]
    cryt = metrics.get_cryt(df)
    bat = metrics.get_batting_average(df)
    return [date, episode, cryt, bat]

def get_yearly_distribution_table():
    df = get_cryt_table()
    df['Year'] = [d.split('-')[0] for d in df['Date'].values]
    grp = df.groupby('Year')
    print(grp.mean())
    print(grp.std())

def get_all_round_batting_averages():
    df = db_interface.get_table('CORPUS')
    grp = df.groupby('Date')
    print('Calculating Batting Averages')
    data = [metrics.get_batting_average_by_round(item) for key, item in tqdm.tqdm(grp)]
    data = [i for j in data for i in j]
    return data

def get_batting_average_chart():
    data = get_all_round_batting_averages()
    s = pd.Series(data).sort_values()
    x = Symbol('x')
    data = []
    print('Calculating IID Batting Averages')
    for i in tqdm.tqdm(s.values):
        data.append(solve(x**3 - 3*x**2 + 3*x - i, x)[0])
    df = pd.DataFrame([list(s.values), data]).T
    df.columns = ['TM BAT', 'IID BAT']
    df['PROJ BAT'] = ((df['TM BAT'] + 1) * (df['IID BAT'] + 1))**.5 - 1
    df['PCT'] = df.index / len(df)
    return df
