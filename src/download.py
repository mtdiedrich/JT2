from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import sys

# Still really needs mechanism to find most recent episode and download/parse/load all unacquired
# Automatically

def replace_html(line):
    line = line.replace('&quot;', '"')
    line = line.replace('&lt;', '<')
    line = line.replace('&gt;', '>')
    line = line.replace('&amp;', '&')
    return replace_slash(line)

def replace_slash(data):
    return data.replace(r"\'", "'")


def download():
    base = 'http://www.j-archive.com/showgame.php?game_id='
    episodes = range(1, 6700)
    clue_data = []
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
    df.columns = ['Episode ID', 'Round', 'Category', 'Order', 'Clue' ,'Answer']
    df.to_csv('./data/q.csv')
    print(df)
