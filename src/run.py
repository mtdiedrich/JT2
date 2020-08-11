from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QButtonGroup, 
        QRadioButton, QGridLayout, QApplication)
from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt, QSize
from PyQt5.QtGui import QIcon

from datetime import datetime

import pandas as pd
import numpy as np

import sqlite3
import click
import uuid
import time
import tqdm
import sys

import download, db_interface, analysis, corpus


pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 225)
pd.set_option('display.max_colwidth', 50)
pd.set_option('display.max_rows', 200)


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.data = self.get_random_data()
        self.lay = QGridLayout()
        self.setLayout(self.lay)
        self.radio_buttons = []

        self.lay.addWidget(QLabel('Category', self), 0, 0)
        self.lay.addWidget(QLabel('Question', self), 0, 1)

        for enum in enumerate(self.data.values):
            category_label = QLabel(enum[1][4] + '   ', self)
            question = enum[1][6]
            if len(question) > 150:
                words = question.split(' ')
                split = len(words)//2
                front = ' '.join(words[:split])
                back = ' '.join(words[split:])
                question = front + '\n\r' + back
            if bool(enum[1][8]):
                question = 'DD: ' + question
            question_label = QLabel(question, self)
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
        self.lay.addWidget(cancel_button, len(self.data)+2, 4)
        self.lay.setVerticalSpacing(0)
        self.setWindowTitle('Basic Grid Layout')
        self.show()

    def get_random_data(self):
        '''Return random board from random episode.'''
        df = db_interface.get_table('CORPUS')
        df = df[df['Round'] < 3]
        df = df.sample(frac=1).head(1)
        episode_id, episode_round = list(df.values[0][2:4])
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
            self.lay.addWidget(QLabel(enum[1][7], self), enum[0]+1, 3)
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
            uid = row[0]
            buttons = grp[0].buttons()
            if buttons[0].isChecked():
                temp = [datetime.now(), uid, grp[2], 1]
            elif buttons[1].isChecked():
                temp = [datetime.now(), uid, grp[2], 0]
            else:
                temp = [datetime.now(), uid, grp[2], -1]
            data.append(temp)
        df = pd.DataFrame(data)
        df.columns = ['SUBMITTED', 'ID', 'Attempt', 'Result'] 
        conn = sqlite3.connect('./data/JT2')
        df.to_sql('RESULTS', conn, if_exists='append', index=False)
        quit()
        return None


def main():
    df = corpus.get_cryt_table()
    print(df)
    print()
    df = corpus.get_yearly_distribution_table()
    print(df)
    print()
    df = corpus.calculate_team_performance(df)
    print(df)
    print()


@click.command()
@click.option('--play', '-p', is_flag=True)
@click.option('--update', '-u', is_flag=True)
@click.option('--drop', '-d', is_flag=True)
@click.option('--create', '-c', is_flag=True)
@click.option('--terminate', '-t', is_flag=True)
@click.option('--new_key', '-n', is_flag=True)
def click_main(play, update, drop, create, terminate, new_key):
    if update or drop:
        if drop:
            conn = sqlite3.connect('./data/JT2')
            conn.execute('DROP TABLE IF EXISTS CORPUS')
            conn.execute('DROP TABLE IF EXISTS RESULTS')
        try:
            download.download()
        except:
            print('Cannot refresh DB')
    if play:
        app = QApplication(sys.argv)
        ex = App()
        sys.exit(app.exec_())
    if create:
        print(manage_instance.run_create_process())
    if terminate:
        print(manage_instance.terminate_all_active_instances())
    if new_key:
        manage_instance.create_key_pair()
    elif not (play or update or drop or create or terminate or new_key):
        main()


if __name__ == "__main__":
    start = time.time()
    click_main()
    print(time.time()-start)
