import sqlite3
import pandas as pd
import string
from itertools import combinations


def write_to_db(df, name):
    conn = sqlite3.connect('./data/JT2')
    df.to_sql(name, conn, if_exists='replace', index=False)

def init_db():
    conn = sqlite3.connect('./data/JT2')
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
    conn = sqlite3.connect('./data/JT2')
    cursor = conn.cursor()
    cursor.execute('SELECT name from sqlite_master where type= "table"')
    return cursor.fetchall()

def write_or_init_db(df):
    conn = init_db()
    df.to_sql('corpus', conn, if_exists='replace')
    

def get_table(table):
    conn = sqlite3.connect('./data/JT2')
    try:
        df = pd.read_sql('SELECT * FROM ' + table.upper(), conn)
        return df
    except pd.io.sql.DatabaseError:
        return None


def make_cards():
    df = get_table('cards_data')
    df = df[[c for c in df.columns if c != 'index']]
    dfs = []
    for v in df.values:
        title = v[1].strip()
        subject = v[1].strip()
        info = v[2]
        info = info.replace('\n', ' ')
        replace = [i + '.' for i in string.ascii_uppercase]
        replace.append('v.')
        for r in replace:
            info = info.replace(r, r[0])
        if '(' in subject:
            subject = subject.split('(')
            sub_1 = subject[0].strip()
            sub_2 = subject[1].split(')')[0].strip()
            subject = [sub_1, sub_2]
            for sub in subject:
                info = info.replace(sub, '  [THIS]  ')
                info = info.replace(sub.lower(), '  [THIS]  ')
                info = info.replace(sub.upper(), '  [THIS]  ')
        else:
            info = info.replace(subject, '  [THIS]  ')
            info = info.replace(subject.lower(), '  [THIS]  ')
            info = info.replace(subject.upper(), '  [THIS]  ')
        while '  ' in info:
            info = info.replace('  ', ' ')
        card_info = [i.strip()+'.' for i in info.split('.') if i !='']
        data = []
        if len(card_info) > 6:
            data += [' '.join(c) for c in list(combinations(card_info, 4))]
        elif len(card_info) > 4:
            data += [' '.join(c) for c in list(combinations(card_info, 3))]
        elif len(card_info) > 2:
            data += [' '.join(c) for c in list(combinations(card_info, 2))]
        else:
            data.append(info)
        pairs = [[title, i] for i in data]
        dfs.append(pd.DataFrame(pairs))
    df = pd.concat(dfs)
    df = df.drop_duplicates()
    df.columns = ['Topic', 'Info']
    df = df.reset_index(drop=True)
    return df

def clean_history():
    df = get_table('HISTORY')
    print(df)

def get_sn_df():
    sn_df = pd.concat([
        get_table('HISTORY'),
        get_table('SCIENCE'),
        get_table('BIOGRAPHY'),
        get_table('ECONOMICS'),
        get_table('PHILOSOPHY'),
        get_table('PSYCHOLOGY'),
        get_table('SOCIOLOGY'),
        get_table('GOVERNMENT'),
        ])
    return sn_df
