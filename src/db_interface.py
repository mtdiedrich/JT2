import sqlite3

def init_db():
    conn = sqlite3.connect('./data/JT2')
    try:
        conn.execute('''
                CREATE TABLE corpus (
                    episodeID real, 
                    round text, 
                    category text, 
                    orderID real, 
                    clue text, 
                    answer text)
                    ''')
    except sqlite3.OperationalError:
        pass
    return conn
    
def write_or_init_db(df):
    conn = init_db()
    df.to_sql('corpus', conn, if_exists='replace')
