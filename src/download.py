from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import sys


class Page:

    def __init__(self, url, base='https://j-archive.com'):
        self.url = url
        sys.stdout.write('\033[F')
        print(int(url.split('=')[1])/6670, flush=True)
        self.page = self.get_page(url)
        self.head = self.page.head
        self.body = str(self.page.body)

        interest = [l for l in self.body.splitlines() if 'div onclick' in l]
        category_names = [l.split('>')[2].split('<')[0] for l in self.body.splitlines() if 'category_name' in l]
        rows = []
        if len(category_names) > 0:
            sj_cat = category_names[:6]
            dj_cat = category_names[6:-1]
            fj_cat = category_names[-1]
            for i in interest:
                try:
                    onmouseout = i.split('onmouseout')
                    onmouseover = onmouseout[1].split('onmouseover')
                    clue_id = onmouseout[0].split('togglestick')[1]
                    clue = onmouseover[0].split("_stuck', '")[1]
                    if 'j-archive' not in clue:
                        clue = clue.replace("')"+'"', '')
                        clue = clue.replace("\\'", "'")
                        clue = clue.replace('&quot;', '"')
                        clue = clue.replace('&amp;', '&')
                        s = onmouseover[1].replace('\\', '')
                        s = s.split('correct_response&quot;')[1]
                        s = s.replace('i&gt;', '')
                        s = s.replace('&lt;/', '')
                        s = s.replace('em&gt;', '')
                        s = s.replace("')" + '">', '')
                        s = s.replace('&gt;', '')
                        s = ''.join([f for f in s.split('&lt;') if f != ''])
                        s = s.split('br /')[0]
                        s = s.replace('&amp;', '&')
                        cat_data = clue_id.split('_')
                        if cat_data[1] == 'J':
                            category = sj_cat[int(cat_data[2])-1]
                            order = cat_data[3]
                        elif cat_data[1] == 'DJ':
                            category = dj_cat[int(cat_data[2])-1]
                            order = cat_data[3]
                        else:
                            category = fj_cat
                            order = 0
                        rows.append([category, order, clue, s])
                except:
                    pass
        self.rows = rows


    def get_page(self, url):
        r  = requests.get(url)
        data = BeautifulSoup(r.text, 'html.parser')
        return data

    def save_page(self):
        title = self.url.split('/')[-1].replace('.', '_')
        loc = './data/' + title + '.txt'
        with open(loc, "w", encoding="utf-8") as f:
            f.write(str(self.page))
            f.close()


def get_seasons_list():
    base = 'https://j-archive.com'
    seasons_url = base + '/listseasons.php'
    links = [l.get('href') for l in Page(seasons_url).links]
    link_urls = [base + '/' + l for l in links if '/' not in l]
    return link_urls


def parse_page():
    return page


def get_data_from_page():
    return data


def get_episodes_list():
    return episodes


def main():
    base = 'https://j-archive.com'
    seasons_url = base + '/listseasons.php'
    base = 'http://www.j-archive.com/showgame.php?game_id='
    urls = [base + str(i) for i in range(1,6670)]
    pages = [Page(u) for u in urls]

    data = []
    for page in pages:
        for row in page.rows:
            if len(row) > 0:
                data.append(row)
    df = pd.DataFrame(data, columns=['CATEGORY', 'ORDER', 'CLUE', 'ANSWER'])
    df.to_csv('./data/questions.csv')
    print(df)



if __name__ == "__main__":
    
    main()


