from itertools import combinations

import pandas as pd

import sqlite3
import string


DB_LOC = './data/jtrainDW'


def write_to_db(df, name):
    conn = sqlite3.connect(DB_LOC)
    df.to_sql(name, conn, if_exists='replace', index=False)


def init_db():
    conn = sqlite3.connect(DB_LOC)
    try:
        conn.execute('''
                CREATE TABLE corpus (
                    episodeID real, 
                    round text, 
                    category text, 
                    orderID real, 
                    clue text, 
                    answer text)
                    ''')
    except sqlite3.OperationalError:
        pass
    return conn
    

def get_all_tables():
    conn = sqlite3.connect(DB_LOC)
    cursor = conn.cursor()
    cursor.execute('SELECT name from sqlite_master where type= "table"')
    return cursor.fetchall()


def get_table(table):
    conn = sqlite3.connect(DB_LOC)
    try:
        df = pd.read_sql('SELECT * FROM ' + table.upper(), conn)
        return df
    except pd.io.sql.DatabaseError:
        return None
