from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QLabel, QRadioButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

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
        super().__init__()
        self.data = self.get_random_data()
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        grid_layout.addWidget(QLabel('Category', self), 0, 0)
        grid_layout.addWidget(QLabel('Question', self), 0, 1)

        for enum in enumerate(self.data.values):

            category_label = QLabel(enum[1][3] + '   ', self)
            question_label = QLabel(enum[1][5], self)
            answer_button = QPushButton('ANSWER', self)
            answer_button.setToolTip(enum[1][6])
            yes_button = QRadioButton("Yes")
            no_button = QRadioButton("No")
            disinclude_button = QRadioButton("N/A")

            grid_layout.addWidget(category_label, enum[0]+1, 0)
            grid_layout.addWidget(question_label, enum[0]+1, 1)
            grid_layout.addWidget(answer_button, enum[0]+1, 2)
            grid_layout.addWidget(yes_button, enum[0]+1, 3)
            grid_layout.addWidget(no_button, enum[0]+1, 4)
            grid_layout.addWidget(disinclude_button, enum[0]+1, 5)

        self.setWindowTitle('Basic Grid Layout')
        self.show()

    def get_random_data(self):
        df = db_interface.get_table('CORPUS')
        df = df.sample(frac=1).head(1)
        episode_id, episode_round = list(df.values[0][1:3])
        conn = sqlite3.connect('./data/JT2')
        query = "SELECT * FROM CORPUS WHERE EPISODEID = '{}' AND ROUND = '{}'"
        query = query.format(episode_id, episode_round)
        df = pd.read_sql(query, conn)
        return df


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == "__main__":

    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--drop', action='store_true')

    args = parser.parse_args()

    if args.drop:
        conn = sqlite3.connect('./data/JT2')
        conn.execute('DROP TABLE IF EXISTS CORPUS')

    if args.update or args.drop:
        try:
            download.download()
        except:
            print('Cannot refresh DB')
    main()
    print(time.time()-start)
