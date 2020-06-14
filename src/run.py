import pandas as pd
import numpy as np
import requests
import sqlite3
try:
    from src import download, db_interface, NLP, mine_sn
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn


pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 225)

def get_corpus():
    conn = sqlite3.connect('./data/JT2')
    df = pd.read_sql('SELECT * FROM CORPUS', conn)
    return df

def main():
    df = mine_sn.get_sn_df()
    print(df)


if __name__ == "__main__":
    try:
        download.download(download.get_stale_on())
    except requests.exceptions.ConnectionError:
        print('Cannot refresh DB')
    main()
