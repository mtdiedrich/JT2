from sklearn.feature_extraction.text import TfidfVectorizer
import rake
import numpy as np
import pandas as pd
import time
import string


def clean(data):
    data = data.replace('-', ' ')
    data = data.translate(str.maketrans('', '', string.punctuation))
    data = data.lower()
    data = data.replace('  ', ' ')
    return data

def category_relevant_text(df):
    pairs = {}
    counts = {}
    for episode in list(set(list(df['EpisodeID'].values))):
        episode_df = df[df['EpisodeID']==episode]
        for category in list(set(list(episode_df['Category'].values))):
            episode_category_df = episode_df[episode_df['Category']==category]
            combined_text = episode_category_df['Clue'] + ' ' + episode_category_df['Answer']
            raw_text = ' '.join(list(combined_text.values))
            categories = category.split(' ')
            for cat in categories:
                if cat in pairs:
                    pairs[cat] += ' ' + raw_text
                else:
                    pairs[cat] = raw_text
                if cat in counts:
                    counts[cat] += 1
                else:
                    counts[cat] = 1
    s = pd.Series(pairs.values()[0], index=pairs.keys())
    return s

def category_tfidf(df):
    categories = list(set(list(df['Category'].values)))
    tfidf = TfidfVectorizer(
            binary=True,
            strip_accents='ascii', 
            sublinear_tf=True, 
            ngram_range=(1,1)
            )
    tfidf_data = tfidf.fit_transform(categories).toarray()
    df = pd.DataFrame(tfidf_data, index=categories, columns=tfidf.get_feature_names())
    df = df**4
    df = df.sum()
    df = df.sort_values(ascending=False)
    return df

def tf(df):
    cats = category_tfidf(df).head(10).index
    df = category_relevant_text(df)
    print(df)
    """
    df.index = [i.lower() for i in df.index]
    df = df[df.index.isin(cats)]
    text = df['Text'].values
    tfidf = TfidfVectorizer(strip_accents='ascii', sublinear_tf=True, ngram_range=(1,1))
    tfidf.fit(text)
    return df
    """


def bar(df):
    start = time.time()
    text = [clean(s) for s in df['Clue'].values]
    tfidf = TfidfVectorizer(binary=True, strip_accents='ascii', sublinear_tf=True, ngram_range=(1,1))
    tfidf_matrix = tfidf.fit(text)
    tf = []
    sub = text[:10000]
    for line in sub:
        words = line.split(' ')
        data = pd.Series(list(tfidf.transform([line]).toarray()[0]), index=tfidf.get_feature_names())
        data = list(tfidf.transform([line]).toarray()[0])
        div = sum(data)
        data = [d**2/div**2 for d in data]
        tf.append(data)
        """
        data = data[data>0]
        print(line)
        print(data.sort_values(ascending=False))
        print()
        """
    df = pd.DataFrame(tf, columns=tfidf.get_feature_names(), index=sub)
    df = df.sum()

    print(df.sort_values(ascending=False))
    print(time.time()-start)
    """
    corpus = list(set(list(' '.join(list(text)).lower().split(' '))))
    counts = {w: 0 for w in corpus}
    for line in text:
        words = list(set(list(line.lower().split(' '))))
        for word in words:
            counts[word] += 1
    for q in text[10:35]:
        temp = q.lower()
        words = temp.split(' ')
        values = [np.log(1/counts[word]+1) for word in words]
        s = pd.Series(values, index=words)
        print(q)
        print(s.sort_values(ascending=False))
        print()
    """



