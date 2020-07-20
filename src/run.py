from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QGridLayout, QScrollArea
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QLabel, QRadioButton, QButtonGroup
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QCoreApplication
from PyQt5.QtCore import Qt, QSize


import pandas as pd
import numpy as np
import argparse
import sqlite3
import uuid
import time
import sys

try:
    from src import download, db_interface, analysis
except ModuleNotFoundError:
    import download, db_interface, analysis


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
            category_label = QLabel(enum[1][4] + '   ', self)
            question = enum[1][6]
            if len(question) > 100:
                words = question.split(' ')
                split = len(words)//2
                front = ' '.join(words[:split])
                back = ' '.join(words[split:])
                question = front + '\n\r' + back
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
                temp = [uid, grp[2], 1]
            elif buttons[1].isChecked():
                temp = [uid, grp[2], 0]
            else:
                temp = [uid, grp[2], -1]
            data.append(temp)
        df = pd.DataFrame(data)
        df.columns = ['ID', 'Attempt', 'Result'] 
        conn = sqlite3.connect('./data/JT2')
        df.to_sql('RESULTS', conn, if_exists='append', index=False)
        quit()
        return None


def main():
    analysis.foo()
    

if __name__ == "__main__":

    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--drop', action='store_true')
    parser.add_argument('--play', action='store_true')

    args = parser.parse_args()

    if args.update or args.drop:
        if args.drop:
            conn = sqlite3.connect('./data/JT2')
            conn.execute('DROP TABLE IF EXISTS CORPUS')
        download.download()
        try:
            download.download()
        except:
            print('Cannot refresh DB')

    if args.play:
        app = QApplication(sys.argv)
        ex = App()
        sys.exit(app.exec_())
    else:
        main()

    print(time.time()-start)
