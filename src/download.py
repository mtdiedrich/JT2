from bs4 import BeautifulSoup
import multiprocessing as mp
import pandas as pd
import requests
import sqlite3
import uuid
import tqdm
import time
import lxml
import re
import os

try:
    from src import db_interface
except:
    import db_interface


def download():
    '''Download data from website.'''
    print('Collecting links', flush=True)
    seasons = get_links()
    episodes_arr = [get_links(s) for s in tqdm.tqdm(seasons)]
    episodes = [i for j in episodes_arr for i in j]
    fresh_episodes = get_fresh_episodes(episodes)
    print('Parsing episodes', flush=True)
    parse_all_episodes(fresh_episodes)
    return None


def parse_all_episodes(fresh_episodes, individual=True):
    '''Parse all given episodes and write to DB.'''
    dfs = []
    conn = sqlite3.connect('./data/JT2')
    for episode in enumerate(tqdm.tqdm(fresh_episodes)):
        episode_soup = soup_for_you(episode[1])
        episode_df = parse_episode(episode_soup)
        if individual:
            df = clean(episode_df)
            df.to_sql('CORPUS', conn, if_exists='append', index=False)
        else:
            dfs.append(df)
    if not individual:
        df = pd.concat(dfs)
        df = clean(df)
        df.to_sql('CORPUS', conn, if_exists='append', index=False)
    return None


def get_corpus_and_ids():
    '''Return J! corpus and episode IDs.'''
    try:
        corpus = db_interface.get_table('CORPUS')
        ids = list(set(list(corpus['EpisodeID'].values)))
    except:
        #Need exception
        ids = []
    return ids


def get_fresh_episodes(episodes):
    '''Return list of episodes not in DB.'''
    ids = get_corpus_and_ids()
    fresh_episodes = []
    for episode in episodes:
        try:
            episode_id = re.findall(r'(?<=\#)\d+(?=\,)', str(episode))[0]
        except:
            episode_id = re.findall(r'(?<=\=)\d+(?=\")', str(episode))[0]
        if episode_id not in ids:
            fresh_episodes += [episode]
    return fresh_episodes


def clean(df):
    '''Clean data before inserting into DB.'''
    df = df.drop_duplicates()
    df = df.sort_values(['EpisodeID','Round', 'Category', 'Value'])
    df = df.reset_index(drop=True)
    return df


def extract_link(link_data):
    '''Extract link from link data.'''
    base = 'https://www.j-archive.com/'  
    link = re.findall(r'(?<=\")(.*?)(?=\")', str(link_data))[0]
    link = base + link if 'j-archive' not in link else link
    return link


def get_links(link='https://j-archive.com/listseasons.php'):
    '''Return links from given link.'''
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'lxml')
    if 'listseasons' in link:
        link_data = [l for l in soup.find_all('a') if 'season=' in str(l)]
        link_data = [extract_link(l) for l in link_data]
    else:
        link_data = [l for l in soup.find_all('a') if 'game_id' in str(l)]
    return link_data


def identify_rounds(soup):
    rounds = [r + 'jeopardy_round' for r in ['', 'double', 'final']]
    round_exists = {r: soup.find(id=r) != None for r in rounds}
    round_exists['tie_breaker'] = len(soup.find_all(class_='final_round')) > 1
    return round_exists


def soup_for_you(episode_data):
    link = extract_link(str(episode_data))
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'lxml')
    return soup


def get_round_data(soup):
    round_exists = identify_rounds(soup)
    round_data = []

    if round_exists['jeopardy_round']:
        round_data.append(soup.find(id='jeopardy_round'))
    if round_exists['double_jeopardy_round']:
        round_data.append(soup.find(id='double_jeopardy_round'))
    if round_exists['final_jeopardy_round']:
        round_data.append(soup.find(id='final_jeopardy_round'))

    return round_data


def get_coord(clue):

    try:
        clue_data = clue.find('td', class_='clue_text').get('id')
    except AttributeError:
        return (0, 0)

    pre_coord = re.findall(r'(\d)_(\d)', clue_data)

    if len(pre_coord) > 0:
        coord = tuple([int(p) for p in pre_coord[0]])
    else:
        coord = (1, 1)

    return coord


def if_none(cat):
    if cat != None:
        return [c.text for c in cat.find_all('td', class_='category_name')]
    return None


def get_question_coord(div):
    question_data = div.get('onmouseout').split("', '")
    question = question_data[-1][:-2].replace("\\'", "'")
    coord_data = question_data[1].split('_')
    if 'j-archive' in question:
        question = re.compile(r'<[^>]+>').sub('<*>', question)
    return question, coord_data


def get_answer(div):
    soup = BeautifulSoup(div.get('onmouseover'), 'lxml')
    try:
        answer = soup.find('em', class_='correct_response').text
    except AttributeError:
        answer = soup.find('em').text
    answer = answer.replace("\\'", "'")
    return answer


def parse_episode(soup):
    round_map = {'J': 1, 'DJ': 2, 'FJ': 3, 'TB': 4}
    episode_id = re.findall(r"(?<=\#)\d+(?=\,)", str(soup.title))[0]
    date = re.findall('(?<=aired )(.*?)(?=\<)', str(soup.title))[0]
    extra = soup.find('div', id='game_comments').text.strip()

    j_cat = soup.find(id='jeopardy_round')
    dj_cat = soup.find(id='double_jeopardy_round')
    fj_cat = soup.find(id='final_jeopardy_round')
    c_map = {'J': if_none(j_cat), 'DJ': if_none(dj_cat), 'FJ': if_none(fj_cat)}

    data = []
    for d in soup.find_all('div', onmouseover=True):
        ques, coord_data = get_question_coord(d)
        answer = get_answer(d)
        rnd = round_map[coord_data[1]]
        if len(coord_data) != 5:
            coord = (1, 1)
        else:
            coord = (int(coord_data[2]), int(coord_data[3]))

        if rnd == 4:
            cs = [c.text for c in soup.find_all('td', class_='category_name')]
            cat = cs[-1]
        else:
            cat = c_map[coord_data[1]][coord[0]-1]
        row = [date, episode_id, rnd, cat, coord[1], ques, answer, extra]
        uid = uuid.uuid3(uuid.NAMESPACE_DNS, '|'.join(str(i) for i in row))
        row = [str(uid)] + row
        data.append(row)
    columns = ['ID', 'Date', 'EpisodeID', 'Round', 'Category', 
            'Value', 'Question', 'Answer', 'Extra']
    df = pd.DataFrame(data, columns=columns)
    return df
