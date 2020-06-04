from sklearn.feature_extraction.text import TfidfVectorizer
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

def foo(df):
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



