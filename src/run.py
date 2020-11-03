import pandas as pd
import numpy as np

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_colwidth', 100)


LOC = './data/chally.csv'



class Team:
    def __init__(self, name):
        self.name = name


class Game:
    def __init__(self, **kwargs):
        self.match_day = kwargs['match_day']
        self.weekday = kwargs['weekday']
        self.home = kwargs['home']
        self.away = kwargs['away']
        self.result = kwargs['result']


def create_teams(df):
    """Create the team objects.

    Args:
        df: pandas DataFrame from which team data is derived.
    
    Returns:
        Dict of team objects for which the team names are the keys.
    """
    team_names = sorted(list(set(list(df['Home'].values))))
    teams = {t: Team(t) for t in team_names} 
    return teams


def main():
    df = pd.read_csv(LOC)
    teams = create_teams(df)



if __name__ == "__main__":
    main()
