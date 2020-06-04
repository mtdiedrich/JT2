from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import sys
import sqlite3

# Still really needs mechanism to find most recent episode and download/parse/load all unacquired
# Automatically
# Would alsos be ideal to download each episode, then parse and load

def replace_html(line):
    line = line.replace('&quot;', '"')
    line = line.replace('&lt;', '<')
    line = line.replace('&gt;', '>')
    line = line.replace('&amp;', '&')
    return replace_slash(line)

def replace_slash(data):
    return data.replace(r"\'", "'")


def download(episodes):
    base = 'http://www.j-archive.com/showgame.php?game_id='
    clue_data = []
    if len(episodes) < 2:
        return
    for i in episodes:
        url = base + str(i)
        request = requests.get(url)
        soup = BeautifulSoup(request.text, 'html.parser')
        body = str(soup.body)
        lines = body.splitlines()
        categories = []
        for line in lines:
            if 'div onclick' in line and 'j-archive' not in line:
                clue_line = replace_html(line) 
                onmouseout = clue_line.split('onmouseout')
                clue_id = onmouseout[0].split("'")[1]
                back_end = onmouseout[1]
                clue_text = back_end.split("', '")[2].split("')")[0]
                clue = [clue_id, clue_text]
                answer = back_end.split('correct_response')[1]
                answer = answer.replace('<i>', '')
                answer = answer.split('>')[1].split('<')[0]
                meta = clue_id.split('_')
                rnd = meta[1]
                if rnd in ['FJ', 'TB']:
                    cat_loc = rnd
                    loc = rnd
                else:
                    ctg = int(meta[2])
                    loc = int(meta[3])
                    if rnd == 'DJ':
                        ctg += 6
                try:
                    cat_name = categories[ctg] 
                    clue_row = [i, rnd, cat_name, loc, clue_text,  answer]
                    clue_data += [clue_row]
                except:
                    pass
            elif 'category_name' in line:
                category = replace_html(line) 
                removals = ['<tr><td class="category_name">',  
                        '</td></tr>', '<em class="underline">', '</em>']
                for remove in removals:
                    category = category.replace(remove, '')
                categories += [category]
        sys.stdout.write('\033[F')
        print(i/max(episodes), flush=True)
    df = pd.DataFrame(clue_data)
    df.columns = ['EpisodeID', 'Round', 'Category', 'Order', 'Clue' ,'Answer']
    conn = sqlite3.connect('JT2')
    corpus = pd.read_sql('select * from corpus', conn)
    corpus = corpus[[c for c in corpus.columns if c!='index']]
    df = pd.concat([df, corpus]).drop_duplicates()
    df = df.sort_values('EpisodeID').reset_index(drop=True)
    df.to_sql('corpus', conn, if_exists='replace')

def get_stale_on():
    all_seasons = 'http://www.j-archive.com/listseasons.php'
    request = requests.get(all_seasons)
    soup = BeautifulSoup(request.text, 'html.parser')
    body = str(soup.body)
    curr = [l for l in body.splitlines() if 'current season' in l][0]
    curr = curr.replace(' ', '').split('><')[1].split('http')[1]
    curr = 'http' + curr.split('">')[0]
    current_season = requests.get(curr)
    soup = BeautifulSoup(current_season.text, 'html.parser')
    body = str(soup.body)
    lines = [l for l in body.splitlines() if 'j-archive.com/showgame' in l]
    lines = [l.replace('<a href="http://www.j-archive.com/showgame.php?game_id=', '').split('"')[0] for l in lines]
    episodes = [int(l) for l in lines]
    latest = max(episodes)
    conn = sqlite3.connect('JT2')
    epis = [i[0] for i in pd.read_sql('select distinct episodeid from corpus', conn).values]
    old = max(epis) + 1
    new = latest
    stale_on = list(range(old, new+1))
    print('Current DB is stale from episodes', old, 'to', new)
    return stale_on
