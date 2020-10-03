from PyQt5.QtWidgets import (
        QWidget, QLabel, QPushButton, QButtonGroup,
        QRadioButton, QGridLayout, QApplication, QScrollArea, QHBoxLayout, QVBoxLayout
        )

from datetime import datetime

import pandas as pd

import wikipedia
import sqlite3
import click
import time
import sys

import download
import db_interface
import analysis
import visualization
import topics
import study
import StudyUI
import NLP


pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 225)
pd.set_option('display.max_colwidth', 140)
pd.set_option('display.max_rows', 200)


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.data = self.get_random_data()
        self.scroll = QScrollArea() 

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
    comparison = analysis.correct_topic_comparison()
    study_df = study.get_study_df_for_worst_topic()
    print(db_interface.get_table('STUDYGUIDE'))

@click.command()
@click.option('--play', '-p', is_flag=True)
@click.option('--update', is_flag=True)
@click.option('--drop', is_flag=True)
@click.option('--visualize', '-v', is_flag=True)
@click.option('--study', '-s', is_flag=True)
def click_main(play, update, drop, visualize, study):
    start = time.time()
    if update or drop:
        if drop:
            conn = sqlite3.connect('./data/JT2')
            conn.execute('DROP TABLE IF EXISTS CORPUS')
            conn.execute('DROP TABLE IF EXISTS RESULTS')
        # This would do well with exception handling
        # Not important until new episodes are coming out
        # Which won't happen until new episodes are being filmed
        # Which won't happen while COVID is active
        # So this can likely stay as-is for 6+ months
        download.download()
    if play:
        app = QApplication(sys.argv)
        App()
        sys.exit(app.exec_())
    if visualize:
        visualization.grade_over_time()
    if study:
        StudyUI.main()
    elif not (play or update or drop or study or visualize):
        main()
    print(time.time()-start)


if __name__ == "__main__":
    click_main()
