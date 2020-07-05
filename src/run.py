from collections import Counter
import pandas as pd
import numpy as np
import wikipedia
import requests
import argparse
import sqlite3
import string
import time
try:
    from src import download, db_interface, NLP, mine_sn, augment, play
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn, augment, play


pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 235)
pd.set_option('display.max_colwidth', 65)
pd.set_option('display.max_rows', 100)


def main():
    conn = sqlite3.connect('./data/JT2')
    df = db_interface.get_table('SCIENCE')
    corpus = df['Info'].values
    joined = ' '.join(list(corpus)).lower()
    no_punc = joined.translate(str.maketrans('', '', string.punctuation))
    words = no_punc.split(' ')
    counts = Counter(words)

    new = pd.DataFrame([list(counts.keys()), list(counts.values())]).T
    new.columns = ['Word', 'Freq']
    new = new.sort_values('Freq', ascending=False)
    
    length = len(new)//4 
    new = new.tail(3*length)
    imp = new['Word'].values
    print(len(imp))

    key = []
    for row in df.values:
        comp = row[-1].lower()
        comp = comp.translate(str.maketrans('', '', string.punctuation))
        comp = ' ' + comp + ' '
        temp = [word for word in imp if ' ' + word + ' ' in comp]
        key.append(temp)
    df['Key'] = key
    print(df)
            





if __name__ == "__main__":

    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('--halt', action='store_true')
    parser.add_argument('--drop', action='store_true')
    args = parser.parse_args()

    if not args.halt:

        if args.drop:
            conn = sqlite3.connect('./data/JT2')
            conn.execute('DROP TABLE IF EXISTS CORPUS')

        try:
            download.download()
        except:
            print('Cannot refresh DB')

    main()

    print(time.time()-start)
