from sklearn.feature_extraction.text import TfidfVectorizer

import pandas as pd
import tqdm

try:
    from src import db_interface
except ModuleNotFoundError:
    import db_interface

def analyze_topics():
    df = answer_counts()
    vct = TfidfVectorizer()
    to_transform = df['Doc'].values
    answers = df['Answer'].values
    sparse_X = vct.fit_transform(to_transform)
    X = sparse_X.todense()
    features = vct.get_feature_names()
    tfidf_df_inv = pd.DataFrame(X, index=answers, columns=features)
    tfidf_df = tfidf_df_inv.T
    data = []
    interest = df['Answer'].head(100)
    for col in tqdm.tqdm(interest.values):
        temp = tfidf_df[col].sort_values(ascending=False)
        temp = temp[temp > 0]
        data.append(temp.head(1).index)
    df = pd.DataFrame(data, index=interest.values, columns=['classification'])
    grp = df.groupby('classification')
    for key, item in grp:
        print(key)
        print(item)
        print()
    """
    sizes = grp.size()
    percents = sizes/sizes.sum()
    data = [sizes.values, percents.values]
    idx = ['count', 'percent']
    inv_df = pd.DataFrame(data, index=idx, columns=grp.indices)
    df = inv_df.T
    df['count'] = df['count'].astype(int)
    df = df.sort_values('count', ascending=False)
    df['cumsum'] = df['percent'].cumsum()
    return df
    """

def answer_counts(df = db_interface.get_table('CORPUS')):
    df = df[df['Answer']!='=']
    grp = df.groupby('Answer')
    data = []
    for key, item in tqdm.tqdm(grp):
        idx = key
        length = len(item)
        txt = ' '.join(list(item['Question'].values))
        data.append([idx, length, txt])
    df = pd.DataFrame(data, columns=['Answer', 'Length', 'Doc'])
    df = df.sort_values('Length', ascending=False)
    return df
