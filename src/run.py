import pandas as pd
import sqlite3
try:
    from src import download, db_interface, NLP
except ModuleNotFoundError:
    import download, db_interface, NLP


pd.set_option('display.max_columns', 25)
pd.set_option('display.width', 225)


def main():
    conn = sqlite3.connect('JT2')
    df = pd.read_sql('select * from corpus', conn)
    NLP.foo(df)


if __name__ == "__main__":
    download.download(download.get_stale_on())
    main()
