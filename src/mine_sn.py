from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import sys
import sqlite3


def replace_html(line):
    line = line.replace('&quot;', '"')
    line = line.replace('&lt;', '<')
    line = line.replace('&gt;', '>')
    line = line.replace('&amp;', '&')
    return replace_slash(line)

def replace_slash(data):
    return data.replace(r"\'", "'")

def get_sn_df():
    topic_links = [get_topic_links(l) for l in get_all_links()]
    data = []
    #topic_links = topic_links[:10]
    for t in topic_links:
        people = parse_people(t[0])
        try:
            terms = parse_terms(t[1])
            df = pd.concat([people, terms])
        except IndexError:
            df = people
        data.append(df)
    df = pd.concat(data)
    df = pd.concat(data)
    df = df.reset_index(drop=True)
    return df


def dedup_spaces_in_list(data):
    return_data = []
    for d in data:
        temp = d
        while '  ' in temp:
            temp = temp.replace('  ', ' ')
        return_data.append(temp)
    return return_data


def parse_terms(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    h3_list = [h.get_text().replace('\n', '').strip() for h in soup.findAll('h3')]
    h3_list = [h for h in h3_list if h not in ['Terms', 'Events']]
    p_list = [p.get_text().replace('\n', '').strip().replace('  ', ' ') for p in soup.findAll('p')]
    p_list = p_list[:-2]
    cards = []
    for h, p in zip(h3_list, p_list):
        cards.append([h, p])
    df = pd.DataFrame(cards, columns=['Subject', 'Info'])
    cards = []
    if len(df)==0:
        for l in soup.findAll('li'):
            key = [k.get_text() for k in l.findAll('h3')]
            if len(key) > 0:
                answer = key[0].strip().replace('\\n', ' ').replace('\n', ' ')
                clue = l.get_text().strip()[len(answer)+1:].strip()
                cards.append([answer, clue])
        df = pd.DataFrame(cards, columns=['Subject', 'Info'])
    return df


def parse_people(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    h3_list = [h.get_text().replace('\n', '').strip() for h in soup.findAll('h3')]
    p_list = [p.get_text().replace('\n', '').strip().replace('  ', ' ') for p in soup.findAll('p')]
    data = zip(h3_list[:-2], p_list[:-2])
    cards = []
    for h, p in data:
        cards.append([h, p])
    df = pd.DataFrame(cards, columns=['Subject', 'Info'])
    cards = []
    if len(df) == 0:
        for l in soup.findAll('li'):
            key = [k.get_text() for k in l.findAll('h3')]
            if len(key) > 0:
                answer = key[0].replace('\\n', ' ').replace('\n', ' ')
                clue = l.get_text()[len(answer)+2:].replace(answer, '[ANSWER]')
                cards.append([answer, clue])
        df = pd.DataFrame(cards, columns=['Subject', 'Info'])
    return df


def get_topic_links(link):
    split = link.split('history')[1]
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if split in str(l)]
    links = []
    for l in page_links:
        link_data = l.split(split)
        if '" id="' in link_data[1]:
            links.append(link + link_data[1].split('" id="')[0])
    return links


def get_all_links():
    url = 'https://www.sparknotes.com/history/'
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if 'history' in str(l)]
    links = []
    for l in page_links:
        link_data = l.split('>')
        links.append(url + link_data[0].split('"')[1].replace('/history/', ''))
    return links

