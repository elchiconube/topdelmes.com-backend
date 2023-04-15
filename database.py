import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("data.db")
    except Error as e:
        print(e)

    return conn

def create_table(conn, table_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        rating REAL NOT NULL,
                        description TEXT NOT NULL,
                        poster_url TEXT NOT NULL,
                        detail_url TEXT NOT NULL,
                        votes INTEGER NOT NULL,
                        runtime INTEGER NOT NULL,
                        pub_year TEXT NOT NULL,
                        genre TEXT NOT NULL,
                        certificate TEXT NOT NULL,
                        metascore INTEGER NOT NULL,
                        year INTEGER NOT NULL,
                        month INTEGER NOT NULL)''')
    except Error as e:
        print(e)

def insert_data(conn, data_list, year, month, table_name):
    try:
        cursor = conn.cursor()
        for data in data_list:
            cursor.execute(f'''INSERT INTO {table_name} (title, rating, description, poster_url, detail_url, votes, runtime, pub_year, genre, certificate, metascore, year, month)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (data['title'], data['rating'], data['description'], data['poster_url'], data['detail_url'], data['votes'], data['runtime'], data['pub_year'], data['genre'], data['certificate'], data['metascore'], year, month))
        conn.commit()
    except Error as e:
        print(e)

def get_data_by_month_and_year(conn, month, year, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE year=? AND month=?", (year, month))
    return cursor.fetchall()
