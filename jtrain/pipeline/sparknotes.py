from bs4 import BeautifulSoup
from pipeline import db_interface

import pandas as pd
import requests
import sqlite3
import tqdm
import time
import re


BASE = 'https://www.sparknotes.com'
HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def build_sublink_list():
    other_subject_links = get_other_subject_links() 
    sublink_lists = [parse_other_subject(l) for l in tqdm.tqdm(other_subject_links)]
    sublinks = [el for sub in sublink_lists for el in sub]
    subject_links = [parse_greater_subject(s) for s in tqdm.tqdm(sublinks)]
    subjects = [el for sub in subject_links for el in sub if len(sub) > 0]
    return subjects


def get_other_subject_links(link='https://www.sparknotes.com/othersubjects/'):
    page = requests.get(link)
    time.sleep(1)
    soup = BeautifulSoup(page.text, 'lxml')
    h_data = soup.find_all('a')
    link_candidates = [h for h in h_data if 'other-subjects' in str(h)]
    split_links = [str(l).split('/')[1].split('/')[0] for l in link_candidates]
    full_links = ['/'.join([BASE, s]) for s in split_links]
    return full_links


def parse_other_subject(link):
    page = requests.get(link, headers=HEADER)
    time.sleep(1)
    soup = BeautifulSoup(page.text, 'lxml')
    a_data = soup.find_all('a')
    link_lines = [a for a in a_data if 'AZ-list' in str(a)]
    link_data = [str(l).split("href=")[1].split('"')[1] for l in link_lines]
    links = [BASE + l for l in link_data]
    return links


def parse_greater_subject(link):
    page = requests.get(link, headers=HEADER)
    time.sleep(1)
    soup = BeautifulSoup(page.text, 'lxml')
    a_data = soup.find_all('a')
    sub_data = [a for a in a_data if 'umbrella' in str(a)]
    keepers = ['themes', 'motifs', 'symbols', 'key-people', 'terms']
    sublink_lines = [s for s in sub_data if any(x in str(s) for x in keepers)]
    link_ends = [str(s).split('href=')[1].split('"')[1] for s in sublink_lines]
    links = ['/'.join([BASE, l[1:]]) for l in link_ends]
    return links


def parse_lesser_topics(link):
    page = requests.get(link, headers=HEADER)
    time.sleep(1)
    soup = BeautifulSoup(page.text, 'lxml')
    li_data = soup.find_all('li')
    topic_data = []
    for li in li_data:
        h3_data = li.find_all('h3') 
        if len(h3_data) > 0:
            try:
                p_data = li.find_all('p')
                title = h3_data[0].text.strip()
                text = p_data[0].text.replace('\n', ' ').strip().replace('  ', ' ')
            except:
                try:
                    title = h3_data[0].text.strip()
                    text = li.text.replace('\n', ' ').strip().replace('  ', ' ')
                except:
                    print('Broken link!')
                    print(link)
                    print()
            text = text.replace(title, '[THIS]')
            topic_data.append([title, text])
    return topic_data
