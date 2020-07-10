from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QLabel, QRadioButton, QButtonGroup
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QCoreApplication

import pandas as pd
import numpy as np
import argparse
import sqlite3
import time
import sys

try:
    from src import download, db_interface, NLP, mine_sn
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn 


pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 235)
pd.set_option('display.max_colwidth', 65)
pd.set_option('display.max_rows', 100)


class App(QWidget):

    def __init__(self):
        '''init App'''
        super().__init__()
        self.data = self.get_random_data()
        self.lay = QGridLayout()
        self.setLayout(self.lay)
        self.radio_buttons = []

        self.lay.addWidget(QLabel('Category', self), 0, 0)
        self.lay.addWidget(QLabel('Question', self), 0, 1)

        for enum in enumerate(self.data.values):
            category_label = QLabel(enum[1][3] + '   ', self)
            question_label = QLabel(enum[1][5], self)
            att_button = QPushButton("Attempt")
            abs_button = QPushButton("Abstain")
            buttons = [att_button, abs_button]
            att_button.clicked.connect(self.make_att_abs(buttons, enum, 1))
            abs_button.clicked.connect(self.make_att_abs(buttons, enum, 0))

            self.lay.addWidget(category_label, enum[0]+1, 0)
            self.lay.addWidget(question_label, enum[0]+1, 1)
            self.lay.addWidget(att_button, enum[0]+1, 3)
            self.lay.addWidget(abs_button, enum[0]+1, 4)

        submit_button = QPushButton('Submit', self)
        cancel_button = QPushButton('Close', self)
        submit_button.clicked.connect(self.submit)
        cancel_button.clicked.connect(quit)

        self.lay.addWidget(submit_button, len(self.data)+2, 3)
        self.lay.addWidget(cancel_button, len(self.data)+2, 5)
        self.setWindowTitle('Basic Grid Layout')
        self.show()

    def get_random_data(self):
        '''Return random board from random episode.'''
        df = db_interface.get_table('CORPUS')
        df = df[df['Round'] < 3]
        df = df.sample(frac=1).head(1)
        episode_id, episode_round = list(df.values[0][1:3])
        conn = sqlite3.connect('./data/JT2')
        query = "SELECT * FROM CORPUS WHERE EPISODEID = '{}' AND ROUND = '{}'"
        query = query.format(episode_id, episode_round)
        df = pd.read_sql(query, conn)
        return df

    def make_att_abs(self, btns, enum, att):
        '''Return att_abs with parameters.'''
        def att_abs():
            '''Click functionality for buttons.'''
            for btn in btns:
                btn.hide()
            self.lay.addWidget(QLabel(enum[1][6], self), enum[0]+1, 3)
            yes_button = QRadioButton("Correct")
            no_button = QRadioButton("Incorrect")
            corr_group = QButtonGroup(self)
            corr_group.addButton(yes_button)
            corr_group.addButton(no_button)
            self.lay.addWidget(yes_button, enum[0]+1, 4)
            self.lay.addWidget(no_button, enum[0]+1, 5)
            self.radio_buttons.append([corr_group, enum, att])
        return att_abs

    def submit(self):
        '''Submit responses.'''
        data = []
        for grp in self.radio_buttons:
            row = list(grp[1][1])
            row.append(grp[2])
            buttons = grp[0].buttons()
            if buttons[0].isChecked():
                row.append(1)
            elif buttons[1].isChecked():
                row.append(0)
            else:
                row.append(-1)
            data.append(row)
        df = pd.DataFrame(data)
        df.columns = list(self.data.columns) + ['Attempt', 'Result'] 
        conn = sqlite3.connect('./data/JT2')
        df.to_sql('RESULTS', conn, if_exists='append', index=False)
        quit()
        return None


def main():
    df = db_interface.get_table('RESULTS')
    indices = {0: 'Incorrect', 1: 'Correct'}

    knowledge = df['Result'].value_counts(normalize=True) * 100
    knowledge.index = [indices[i] for i in knowledge.index]

    att_df = df[df['Attempt']==1]
    hit_rate = att_df['Result'].value_counts(normalize=True) * 100
    hit_rate.index = [indices[i] for i in hit_rate.index]

    abs_df = df[df['Attempt']==0]
    aggression = abs_df['Result'].value_counts(normalize=True) * 100
    aggression.index = [indices[i] for i in aggression.index]

    print()
    print(df)
    print('KNOWLEDGE')
    print(knowledge)
    print()
    print('HIT RATE')
    print(hit_rate)
    print()
    print('AGGRESSION')
    print(aggression)
    print()


if __name__ == "__main__":

    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--drop', action='store_true')
    parser.add_argument('--main', action='store_true')

    args = parser.parse_args()

    if args.drop:
        conn = sqlite3.connect('./data/JT2')
        conn.execute('DROP TABLE IF EXISTS CORPUS')

    if args.update or args.drop:
        try:
            download.download()
        except:
            print('Cannot refresh DB')

    if args.main:
        main()
    else:
        app = QApplication(sys.argv)
        ex = App()
        sys.exit(app.exec_())

    print(time.time()-start)
