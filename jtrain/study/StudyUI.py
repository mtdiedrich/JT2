from PyQt5.QtWidgets import (
        QWidget, QLabel, QPushButton, QButtonGroup, QMainWindow, QLineEdit,
        QRadioButton, QGridLayout, QApplication, QScrollArea, QHBoxLayout, QVBoxLayout
        )

from analysis import analysis, visualization, topics, NLP
from pipeline import download, db_interface
from . import study

from datetime import datetime

import pandas as pd

import wikipedia
import sqlite3
import click
import time
import sys



class App(QWidget):

    def __init__(self):
        super().__init__()
        self.data = db_interface.get_table('STUDYGUIDE')
        df = self.data.sample(frac=1)
        completed_df = db_interface.get_table('STUDY') 
        temp_df = df[~df[['Topic', 'Answer', 'Word']].isin(completed_df)][['Topic', 'Answer', 'Word']]
        df = temp_df.merge(df, how='left')
        df = df[['Topic', 'Answer', 'Word']].drop_duplicates()
        self.length = len(df)

        self.lay = QGridLayout()
        self.setLayout(self.lay)

        answer = df['Answer'].values[0]
        title = answer + ' (' + str(df['Topic'].values[0]).upper() + ')'
        word = df['Word'].values[0]
        data = self.data[self.data['Word']==word]
        data = data[data['Answer']==answer]
        text = ' | '.join(list(set(list(data['Question'].values))))

        self.answer = answer
        self.word = word
        self.topic = df['Topic'].values[0]

        title_label = QLabel(title)
        word_label = QLabel(word.capitalize())
        space_label = QLabel('')
        text_label = QLabel(text)
        text_label.setWordWrap(True)

        self.textbox = QLineEdit(self)
        self.textbox.resize(800,500)

        self.lay.addWidget(title_label, 0, 0)
        self.lay.addWidget(word_label, 2, 0)
        self.lay.addWidget(QLabel(''), 3, 0)
        self.lay.addWidget(text_label, 4, 0)
        self.lay.addWidget(QLabel(''), 5, 0)
        self.lay.addWidget(self.textbox, 6, 0)
        self.lay.addWidget(QLabel(''), 7, 0)

        submit_button = QPushButton('Submit', self)
        cancel_button = QPushButton('Close', self)
        drop_button = QPushButton('Drop', self)
        submit_button.clicked.connect(self.submit)
        drop_button.clicked.connect(self.drop)
        cancel_button.clicked.connect(quit)

        self.lay.addWidget(submit_button, 8, 0)
        self.lay.addWidget(drop_button, 9, 0)
        self.lay.addWidget(cancel_button, 10, 0)


    def submit(self):
        '''Submit responses.'''
        text = self.textbox.text()
        df = pd.DataFrame([[self.topic, self.answer, self.word, text]], columns=['Topic', 'Answer', 'Word', 'Info'])
        conn = sqlite3.connect('./data/JT2')
        df.to_sql('STUDY', conn, if_exists='append', index=False)
        quit()
        return None


    def drop(self):
        df = pd.DataFrame([[self.topic, self.answer, self.word, 'DROP']], columns=['Topic', 'Answer', 'Word', 'Info'])
        conn = sqlite3.connect('./data/JT2')
        df.to_sql('STUDY', conn, if_exists='append', index=False)
        quit()
        return None


def main():
    app = QApplication(sys.argv)
    a = App()
    a.show()
    completed = db_interface.get_table('STUDY')
    print(completed)
    print(a.length)
    print(len(completed)/(a.length))
    sys.exit(app.exec_())


if __name__=="__main__":
    main()
