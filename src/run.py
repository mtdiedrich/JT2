from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import pandas as pd
import numpy as np
import argparse
import sqlite3
import time
import sys

try:
    from src import download, db_interface, NLP, mine_sn, play
except ModuleNotFoundError:
    import download, db_interface, NLP, mine_sn, play


pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 235)
pd.set_option('display.max_colwidth', 65)
pd.set_option('display.max_rows', 100)


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 button - pythonspot.com'
        self.centralwidget = QWidget()
        self.lay = QVBoxLayout(self.centralwidget)
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        for i in range(6):
            button = QPushButton(str(i), self)
            button.setToolTip('This is an example button')
            button.clicked.connect(self.on_click)
            self.lay.addWidget(button)
        self.show()

    @pyqtSlot()
    def on_click(self):
        print('PyQt5 button click')


def main():
    df = mine_sn.get_history_df()
    print(df)

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

    if args.update:
        try:
            download.download()
        except:
            print('Cannot refresh DB')

    if args.main:
        main()
        print(time.time()-start)
    else:
        app = QApplication(sys.argv)
        ex = App()
        sys.exit( app.exec_() )
