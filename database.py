import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("data.db")
    except Error as e:
        print(e)

    return conn

def create_series_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS series
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

def create_movies_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS movies
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

def insert_series(conn, series_list, year, month, table_name="series"):
    try:
        cursor = conn.cursor()
        for series in series_list:
            cursor.execute('''INSERT INTO series (title, rating, description, poster_url, detail_url, votes, runtime, pub_year, genre, certificate, metascore, year, month)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (series['title'], series['rating'], series['description'], series['poster_url'], series['detail_url'], series['votes'], series['runtime'], series['pub_year'], series['genre'], series['certificate'], series['metascore'], year, month))
        conn.commit()
    except Error as e:
        print(e)

def insert_movies(conn, movies_list, year, month, table_name="movies"):
    try:
        cursor = conn.cursor()
        for movies in movies_list:
            cursor.execute('''INSERT INTO movies (title, rating, description, poster_url, detail_url, votes, runtime, pub_year, genre, certificate, metascore, year, month)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (movies['title'], movies['rating'], movies['description'], movies['poster_url'], movies['detail_url'], movies['votes'], movies['runtime'], movies['pub_year'], movies['genre'], movies['certificate'], movies['metascore'], year, month))
        conn.commit()
    except Error as e:
        print(e)


def get_series_by_month_and_year(conn, month, year):  # Agrega esta función
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM series WHERE year=? AND month=?", (year, month))
    return cursor.fetchall()


def get_movies_by_month_and_year(conn, month, year):  # Agrega esta función
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE year=? AND month=?", (year, month))
    return cursor.fetchall()

def insert_data(conn, data, year, month, table_name):
    if table_name == "series":
        insert_series(conn, data, year, month)
    elif table_name == "movies":
        insert_movies(conn, data, year, month)

def get_data_by_month_and_year(conn, month, year, table_name):
    if table_name == "series":
        return get_series_by_month_and_year(conn, month, year)
    elif table_name == "movies":
        return get_movies_by_month_and_year(conn, month, year)

