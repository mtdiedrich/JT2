from bs4 import BeautifulSoup
import multiprocessing as mp
import pandas as pd
import requests
import sqlite3
import tqdm
import time
import xml
import re
import os


def download():

    print('Collecting links', flush=True)
    print(flush=True)

    seasons = get_links()
    episodes = [i for j in [get_links(s) for s in tqdm.tqdm(seasons)] for i in j]
    conn = sqlite3.connect('./data/JT2')
    
    try:
        corpus = pd.read_sql('select * from corpus', conn)
        ids = list(set(list(corpus['EpisodeID'].values)))
    except:
        corpus = None
        ids = []

    fresh_episodes = episodes

    fresh_episodes = []
    for episode in episodes:
        try:
            episode_id = re.findall(r'(?<=\#)\d+(?=\,)', str(episode))[0]
        except:
            episode_id = re.findall(r'(?<=\=)\d+(?=\")', str(episode))[0]
        if episode_id not in ids:
            fresh_episodes += [episode]

    print(flush=True)
    print('Parsing episodes', flush=True)
    print(flush=True)

    dfs = []
    incrementer = 0

    for episode in tqdm.tqdm(fresh_episodes):
        episode_soup = soup_for_you(episode)
        episode_df = parse_episode(episode_soup)
        dfs.append(episode_df)
        incrementer += 1

        if incrementer % 10 == 0:
            df = pd.concat([corpus] + dfs)
            df = clean(df)
            df.to_sql('CORPUS', conn, if_exists='replace', index=False)

    df = pd.concat([corpus] + dfs)
    df = clean(df)
    df.to_sql('CORPUS', conn, if_exists='replace', index=False)

    return df


def clean(df):
    df = df.drop_duplicates()
    df = df.sort_values(['EpisodeID','Round', 'Category', 'Value'])
    df = df.reset_index(drop=True)
    return df



def extract_link(link_data):
    base = 'https://www.j-archive.com/'  
    link = re.findall(r'(?<=\")(.*?)(?=\")', str(link_data))[0]
    link = base + link if 'j-archive' not in link else link
    return link


def get_links(link='https://j-archive.com/listseasons.php'):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'lxml')

    if 'listseasons' in link:
        link_data = [l for l in soup.find_all('a') if 'season=' in str(l)]
        link_data = [extract_link(l) for l in link_data]
    else:
        link_data = [l for l in soup.find_all('a') if 'game_id' in str(l)]

    return link_data


def identify_rounds(soup):
    rounds = ['jeopardy_round', 'double_jeopardy_round', 'final_jeopardy_round']
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


def get_answer(clue):
    a_data = clue.find('div', onmouseover=True).get('onmouseover')
    a_soup = BeautifulSoup(a_data, 'lxml')

    try:
        answer = a_soup.find('em', class_='correct_response').text
    except AttributeError:
        answer = a_soup.find('em').text

    return answer.strip()


def parse_episode(soup):
    round_map = {'J': 1, 'DJ': 2, 'FJ': 3, 'TB': 4}
    episode_id = re.findall(r"(?<=\#)\d+(?=\,)", str(soup.title))[0]
    date = re.findall('(?<=aired )(.*?)(?=\<)', str(soup.title))[0]
    extra = soup.find('div', id='game_comments').text.strip()
    categories = [c.text for c in soup.find_all('td', class_='category_name')]

    data = []
    for d in soup.find_all('div', onmouseover=True):
        question_data = d.get('onmouseout').split("', '")
        question = question_data[-1][:-2].replace("\\'", "'")

        if 'j-archive' in question:
            question = re.compile(r'<[^>]+>').sub('<*>', question)

        answer_data = d.get('onmouseover')
        answer_data = answer_data[answer_data.find('correct_response'):]
        answer = answer_data.split('>')[1].split('<')[0]
        coord_data = question_data[1].split('_')
        rnd = coord_data[1]

        if len(coord_data) != 5:
            coord = (1, 1)
        else:
            coord = (int(coord_data[2]), int(coord_data[3]))

        cat = categories[6*(round_map[rnd]-1)+coord[0]-1]
        data.append([date, episode_id, round_map[rnd], 
            cat, coord[1], question, answer, extra])

    columns = ['Date', 'EpisodeID', 'Round', 'Category', 'Value', 'Question', 'Answer', 'Extra']
    df = pd.DataFrame(data, columns=columns)

    return df
