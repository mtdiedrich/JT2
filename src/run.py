import pandas as pd
import numpy as np
import wikipedia
import requests
import sqlite3
import string
import time
try:
    from src import download, db_interface, NLP, mine_sn, augment, play
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn, augment, play


pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 235)
pd.set_option('display.max_colwidth', 50)
pd.set_option('display.max_rows', 20)


def main():
    df = db_interface.get_table('CORPUS')
    print(flush=True)
    print(df)


if __name__ == "__main__":
    conn = sqlite3.connect('./data/JT2')
    conn.execute('DROP TABLE IF EXISTS CORPUS')
    start = time.time()
    download.download()
    """
    try:
        download.download()
    except:
        print('Cannot refresh DB')
    """
    main()
    print(time.time()-start)
