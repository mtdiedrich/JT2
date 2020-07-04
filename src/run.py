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


pd.set_option('display.max_columns', 10)


def main():
    df = db_interface.get_table('CORPUS')
    print(flush=True)
    print(df)


if __name__ == "__main__":
    #conn = sqlite3.connect('./data/JT2')
    #conn.execute('DROP TABLE IF EXISTS CORPUS')
    """
    try:
        download.download()
    except:
        print('Cannot refresh DB')
    """
    #download.download()
    main()
