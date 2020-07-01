import pandas as pd
import sqlite3
try:
    from src import download, db_interface, NLP, mine_sn, augment
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn, augment

pd.set_option('display.width', 225)
pd.set_option('display.max_rows', 225)
pd.set_option('display.max_colwidth', 100)


def get_category():
    df = db_interface.get_table('CORPUS').head(100)
    print(df)
    """
    df = db_interface.get_table('CORPUS').sample(frac=1).copy()
    select = df.head(1)[['EpisodeID', 'Category']].values[0]
    episode_df = df[df['EpisodeID']==select[0]]
    select_df = episode_df[episode_df['Category']==select[1]]
    print(select_df)
    """

