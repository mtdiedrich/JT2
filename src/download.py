from bs4 import BeautifulSoup
import requests

class Page:

    def __init__(self, url):
        self.url = url
        self.page = self.get_page(url)
        self.head = self.page.head
        self.body = self.page.body
        self.title = self.page.title
        self.links =  self.page.find_all('a')

    def get_page(self, url):
        r  = requests.get(url)
        data = BeautifulSoup(r.text, 'html.parser')
        return data


def get_seasons_list():
    base = 'https://j-archive.com'
    seasons_url = base + '/listseasons.php'
    links = [l.get('href') for l in Page(seasons_url).links]
    seasons = [base + '/' + l for l in links if '/' not in l]
    return seasons


def parse_page():
    return page


def get_data_from_page():
    return data


def get_episodes_list():
    return episodes


seasons = get_seasons_list()
for s in seasons:
    print(s)
    page = Page(s)
    print(page.head)
    print(flush=True)
