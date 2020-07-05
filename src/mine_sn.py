from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import sys
import sqlite3

# NOTE PSYCHOLOGY HAD MAJOR FIGURES (/characters/) TO BE PARSED
# Obv needs refactored to reduce code duplication
# Need method for checking duplicity (can be called in each get_fn())


def get_govt_df():
    link = 'https://www.sparknotes.com/'
    key = 'us-government-and-politics/'
    request = requests.get(link + key)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if key in str(l) and 'a href' in str(l)]
    econs = [parse_govt(p) for p in page_links]
    df = pd.concat(econs)
    df['Info'] = [d.replace('\n', ' ').replace('  ', ' ') for d in df['Info'].values]
    write_to_db(df, 'GOVERNMENT')
    return df


def parse_govt(econ_data):
    data = econ_data.split('"')
    link_data = data[1]
    link = 'https://www.sparknotes.com' + link_data + 'terms/'
    topic = data[-1].strip().replace('</a>', '').replace('>', '').replace('\n', '')
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    li_links = [l for l in soup.findAll('li')]
    cards = []
    for l in li_links:
        h_links = [h for h in l.findAll('h3')]
        if len(h_links) > 0:
            subject = h_links[0].get_text().strip()
            info = l.get_text().replace(subject, '').strip()
            while '  ' in info:
                info = info.replace('  ', ' ')
            cards.append(['Government', topic, subject, info])
    df = pd.DataFrame(cards, columns = ['Topic', 'Subtopic', 'Subject', 'Info'])
    return df


def get_sociology_df():
    link = 'https://www.sparknotes.com/'
    key = 'sociology/'
    request = requests.get(link + key)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if key in str(l) and 'a href' in str(l)]
    econs = [parse_sociology(p) for p in page_links]
    df = pd.concat(econs)
    df['Info'] = [d.replace('\n', ' ').replace('  ', ' ') for d in df['Info'].values]
    write_to_db(df, 'SOCIOLOGY')
    return df


def parse_sociology(econ_data):
    data = econ_data.split('"')
    link_data = data[1]
    link = 'https://www.sparknotes.com' + link_data + 'terms/'
    topic = data[-1].strip().replace('</a>', '').replace('>', '').replace('\n', '')
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    li_links = [l for l in soup.findAll('li')]
    cards = []
    for l in li_links:
        h_links = [h for h in l.findAll('h3')]
        if len(h_links) > 0:
            subject = h_links[0].get_text().strip()
            info = l.get_text().replace(subject, '').strip()
            while '  ' in info:
                info = info.replace('  ', ' ')
            cards.append(['Sociology', topic, subject, info])
    df = pd.DataFrame(cards, columns = ['Topic', 'Subtopic', 'Subject', 'Info'])
    return df


def get_psychology_df():
    link = 'https://www.sparknotes.com/'
    key = 'sociology/'
    request = requests.get(link + key)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if key in str(l) and 'a href' in str(l)]
    econs = [parse_psychology(p) for p in page_links]
    df = pd.concat(econs)
    df['Info'] = [d.replace('\n', ' ').replace('  ', ' ') for d in df['Info'].values]
    write_to_db(df, 'PSYCHOLOGY')
    return df


def parse_psychology(econ_data):
    data = econ_data.split('"')
    link_data = data[1]
    link = 'https://www.sparknotes.com' + link_data + 'terms/'
    topic = data[-1].strip().replace('</a>', '').replace('>', '').replace('\n', '')
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    li_links = [l for l in soup.findAll('li')]
    cards = []
    for l in li_links:
        h_links = [h for h in l.findAll('h3')]
        if len(h_links) > 0:
            subject = h_links[0].get_text().strip()
            info = l.get_text().replace(subject, '').strip()
            cards.append(['Psychology', topic, subject, info])
    df = pd.DataFrame(cards, columns = ['Topic', 'Subtopic', 'Subject', 'Info'])
    return df


def get_philosophy_df():
    link = 'https://www.sparknotes.com/'
    key = 'philosophy/'
    request = requests.get(link + key)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if key in str(l) and 'a href' in str(l)]
    econs = [parse_philosophy(p) for p in page_links]
    df = pd.concat(econs)
    df['Info'] = [d.replace('\n', ' ').replace('  ', ' ') for d in df['Info'].values]
    write_to_db(df, 'PHILOSOPHY')
    return df


def parse_philosophy(econ_data):
    data = econ_data.split('"')
    link_data = data[1]
    link = 'https://www.sparknotes.com' + link_data + 'terms/'
    topic = data[-1].strip().replace('</a>', '').replace('>', '').replace('\n', '')
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    li_links = [l for l in soup.findAll('li')]
    cards = []
    for l in li_links:
        h_links = [h for h in l.findAll('h3')]
        if len(h_links) > 0:
            subject = h_links[0].get_text().strip()
            info = l.get_text().replace(subject, '').strip()
            cards.append(['Philosophy', topic, subject, info])
    df = pd.DataFrame(cards, columns = ['Topic', 'Subtopic', 'Subject', 'Info'])
    return df


def get_econ_df():
    link = 'https://www.sparknotes.com/'
    key = 'economics/'
    request = requests.get(link + key)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if key in str(l)]
    econs = [parse_econ(p) for p in page_links]
    df = pd.concat(econs)
    df['Info'] = [d.replace('\n', ' ').replace('  ', ' ') for d in df['Info'].values]
    write_to_db(df, 'ECONOMICS')
    return df


def parse_econ(econ_data):
    data = econ_data.split('"')
    link_data = data[1]
    link = 'https://www.sparknotes.com' + link_data + 'terms/'
    topic = data[-1].strip().replace('</a>', '').replace('>', '')
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    li_links = [l for l in soup.findAll('li')]
    cards = []
    for l in li_links:
        h_links = [h for h in l.findAll('h3')]
        if len(h_links) > 0:
            subject = h_links[0].get_text().strip()
            info = l.get_text().replace(subject, '').strip()
            cards.append(['Economics', topic, subject, info])
    df = pd.DataFrame(cards, columns = ['Topic', 'Subtopic', 'Subject', 'Info'])
    return df

def get_biography_df():
    bio = 'https://www.sparknotes.com/biography/'
    request = requests.get(bio)
    soup = BeautifulSoup(request.text, 'html.parser')
    page_links = [str(l) for l in soup.findAll('a') if 'biography' in str(l)]
    bios = [parse_biography(p) for p in page_links]
    df = pd.concat(bios)
    df['Info'] = [d.replace('\n', ' ').replace('  ', ' ') for d in df['Info'].values]
    write_to_db(df, 'BIOGRAPHY')
    return df


def get_science_df():
    term_links = [
            'https://www.sparknotes.com/biology/',
            'https://www.sparknotes.com/chemistry/',
            'https://www.sparknotes.com/cs/',
            'https://www.sparknotes.com/health/',
            'https://www.sparknotes.com/math/',
            'https://www.sparknotes.com/physics/',
            ]
    loc_terms = []
    for t in term_links:
        print(t)
        temp = t.replace('https://www.sparknotes.com', '')
        request = requests.get(t)
        soup = BeautifulSoup(request.text, 'html.parser')
        page_links = [make_link(t, str(l)) for l in soup.findAll('a') if temp in str(l)]
        for p in page_links:
            request = requests.get(p)
            soup = BeautifulSoup(request.text, 'html.parser')
            if '/terms/' in str(soup.body):
                loc_terms.append(p + 'terms/')
    data = [parse_science_terms(t) for t in loc_terms]
    df = pd.concat(data)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    write_to_db(df, 'SCIENCE')
    return df


def get_history_df():
    topic_links = [get_topic_links(l) for l in get_all_links()]
    data = []
    for t in topic_links:
        topic = get_topic(t[0])
        people = parse_people(t[0])
        try:
            terms = parse_history_terms(t[1])
            df = pd.concat([people, terms])
        except IndexError:
            df = people
        df['Subtopic'] = topic
        df['Topic'] = 'History'
        data.append(df)
    df = pd.concat(data)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    df = df[['Topic', 'Subtopic', 'Subject', 'Info']]
    df = df.replace('Sextus Pompei', 'Sextus Pompey')
    write_to_db(df, 'HISTORY')
    return df


def parse_history_terms(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    h3_list = [h.get_text().replace('\n', ' ').strip().replace('  ', ' ') for h in soup.findAll('h3')]
    h3_list = [h for h in h3_list if h not in ['Terms', 'Events']]
    if 'Popular pages' in h3_list[0]:
        h3_list = [h.get_text().replace('\n', ' ').strip().replace('  ', ' ') for h in soup.findAll('h4')]
    p_list = [p.get_text().replace('\n', ' ').strip().replace('  ', ' ') for p in soup.findAll('p')]
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


def parse_science_terms(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    split_link = link.split('/')
    topic = split_link[-5].capitalize()
    if len(topic) < 3:
        topic = topic.upper()
    subtopic = split_link[-4].capitalize()
    subtopic = [h.get_text().replace('\n', ' ').strip().replace('  ', ' ') for h in soup.findAll('h1')][0]
    subtopic = subtopic.split(':')[0]
    if topic == 'Www.sparknotes.com':
        topic = split_link[-3].capitalize()
        subtopic = topic
    h3_list = [h.get_text().replace('\n', ' ').strip().replace('  ', ' ') for h in soup.findAll('h3')]
    drops = ['Formulae', 'Important Formulae', 'Terms', 'Take a Study Break', 'Imortant Formulae', 'Formulas']
    h3_list = [h for h in h3_list if h not in drops and 'Popular pages' not in h]
    p_list = [p.get_text().replace('\n', ' ').strip().replace('  ', ' ') for p in soup.findAll('p')]
    p_list = [p for p in p_list if 'Barnes & Noble' not in p]
    p_list = [p for p in p_list if 'SparkNotes LLC' not in p]
    p_list = [p for p in p_list if p != '']
    cards = []
    for h, p in zip(h3_list, p_list):
        cards.append([topic, subtopic, h, p])
    df = pd.DataFrame(cards, columns=['Topic', 'Subtopic', 'Subject', 'Info'])
    return df

def parse_biography(bio_data):
    data = bio_data.split('\n')
    data = [d for d in data]
    link_data = data[0].strip().replace('<a href="', '').replace('">', '')
    link = 'https://www.sparknotes.com' + link_data + 'terms/'
    topic = data[-1].strip().replace('</a>', '')
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    li_links = [l for l in soup.findAll('li')]

    cards = []
    for l in li_links:
        h_links = [h for h in l.findAll('h3')]
        if len(h_links) > 0:
            subject = h_links[0].get_text().strip()
            info = l.get_text().replace(subject, '').strip()
            cards.append(['Biography', topic, subject, info])
    df = pd.DataFrame(cards, columns = ['Topic', 'Subtopic', 'Subject', 'Info'])
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
                clue = l.get_text()[len(answer)+2:]
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


def get_topic(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    h1_list = [h.get_text().replace('\n', ' ').strip().replace('  ', ' ') for h in soup.findAll('h1')]
    return h1_list[0]


def dedup_spaces_in_list(data):
    return_data = []
    for d in data:
        temp = d
        while '  ' in temp:
            temp = temp.replace('  ', ' ')
        return_data.append(temp)
    return return_data


def write_to_db(df, name):
    #ought to be in db_interface
    conn = sqlite3.connect('./data/JT2')
    df.to_sql(name, conn, if_exists='replace')


def load_cards_data():
    df = get_history_df()
    conn = sqlite3.connect('./data/JT2')
    df.to_sql('CARDS_DATA', conn, if_exists='replace')
    return


def replace_html(line):
    line = line.replace('&quot;', '"')
    line = line.replace('&lt;', '<')
    line = line.replace('&gt;', '>')
    line = line.replace('&amp;', '&')
    return replace_slash(line)


def replace_slash(data):
    return data.replace(r"\'", "'")


def make_link(base, link):
    base_data = base.split('/')
    base_link = '/'.join(base_data[:-1])
    branch = base_data[-1]
    temp = link.split('a href="')[1]
    temp = temp.split('">')[0]
    temp = '/'.join(temp.split('/')[2:])
    return base+temp
