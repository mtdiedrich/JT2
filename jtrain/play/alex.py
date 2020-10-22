from pipeline import db_interface as db
from run import DB_LOC

import pandas as pd

import sqlite3
import string
import random


class Trebek():
    def __init__(self): 
        conn = sqlite3.connect(DB_LOC)
        df = pd.read_sql('SELECT * FROM CORPUS', conn)
        question = df.sample(frac=1).head(1)

        self.category = question['Category'].values[0]
        self.question = question['Question'].values[0]
        self.answer = question['Answer'].values[0]

        try:
            wrong = self.set_wrong_by_topic()
            if len(wrong) < 3:
                wrong = self.wrong_by_web(df)
        except KeyError:
            wrong = self.set_wrong_by_web(df)

        random.shuffle(wrong)
        self.options = [self.answer] + wrong[:3]
        random.shuffle(self.options)


    def set_wrong_by_topic(self):
        """
        Select wrong answers from answers that share a topic with the correct
        answer.

        Returns:
            List of wrong answers
        """
        table = db.get_table('CLASSIFICATION')
        s = table['classification']
        s.index = table['answer']
        topic_map = s.to_dict()
        answer_topic = topic_map[self.answer]
        options = s[s == answer_topic]
        wrong = list(options.index)
        return wrong


    def set_wrong_by_web(self, df):
        """
        Select wrong answers from answers that share a category with the
        correct answer.

        Returns:
            List of wrong answers
        """
        match_cat = df[df['Category']==self.category]
        answer_space = list(set(list(match_cat['Answer'].values)))
        ans_list = [df[df['Answer']==ans] for ans in answer_space]
        answer_df = pd.concat(ans_list).drop_duplicates('Answer')
        category_space = list(set(list(answer_df['Category'].values)))
        cat_list = [df[df['Category']==cat] for cat in category_space]
        category_df = pd.concat(cat_list).drop_duplicates('Answer')
        category_df = category_df[category_df['Answer']!=self.answer]
        wrong = list(category_df['Answer'].values)
        return wrong
