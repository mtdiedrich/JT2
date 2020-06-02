import pandas as pd
import sqlite3
try:
    from src import download, db_interface
except ModuleNotFoundError:
    import download, db_interface


def main():
    df = pd.read_csv('./data/q.csv')
    db_interface.write_or_init_db(df)
    conn = sqlite3.connect('JT2')
    df = pd.read_sql('select * from corpus', conn)
    print(df)


if __name__ == "__main__":
    main()
