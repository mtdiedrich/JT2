import pandas as pd
import numpy as np
import requests
import sqlite3
import string
import wikipedia
try:
    from src import download, db_interface, NLP, mine_sn, augment, play
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn, augment, play


pd.set_option('display.width', 225)
pd.set_option('display.max_rows', 225)
pd.set_option('display.max_colwidth', 100)


def main():
    conn = sqlite3.connect('./data/JT2')
    df = db_interface.get_table('CORPUS')
    print(df)


if __name__ == "__main__":
    try:
        download.download(download.get_stale_on())
    except pd.io.sql.DatabaseError:
        download.download(download.get_stale_on(full=True))
    except:
        print('Cannot refresh DB')
    main()
