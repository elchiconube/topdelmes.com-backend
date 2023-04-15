from flask import Flask, jsonify, request
from functools import wraps
from datetime import datetime
import scraper
import database
import schedule
import time
import threading
import calendar
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
def update_data(table_name):
    print(f"Actualizando datos de {table_name}...")
    current_year, current_month = datetime.now().year, datetime.now().month
    data = scraper.scrape_imdb(current_year, current_month, title_type=table_name)
    conn = database.create_connection()
    database.insert_data(conn, data, current_year, current_month, table_name=table_name)
    conn.close()
    print(f"Datos de {table_name} actualizados")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args.get("api_key") != API_KEY:
            return jsonify({"error": "Invalid API Key"}), 403
        return f(*args, **kwargs)
    return decorated_function

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route("/series", methods=["GET"])
@require_api_key
def get_series():
    return get_data("series")

@app.route("/movies", methods=["GET"])
@require_api_key
def get_movies():
    return get_data("movies")

def get_data(table_name):
    month = request.args.get("month")
    year = request.args.get("year")
    current_year, current_month = datetime.now().year, datetime.now().month

    if not month:
        month = current_month
    else:
        month = int(month)

    if not year:
        year = current_year
    else:
        year = int(year)

    if year > current_year or year < 1900:
        return jsonify({"error": "Invalid year value"}), 400

    if month < 1 or month > 12:
        return jsonify({"error": "Invalid month value"}), 400

    conn = database.create_connection()
    if table_name == "series":
        rows = database.get_series_by_month_and_year(conn, month, year)
    elif table_name == "movies":
        rows = database.get_movies_by_month_and_year(conn, month, year)

    if not rows:
        data = scraper.scrape_imdb(year, month, title_type=table_name)
        if table_name == "series":
            database.insert_series(conn, data, year, month)
            rows = database.get_series_by_month_and_year(conn, month, year)
        elif table_name == "movies":
            database.insert_movies(conn, data, year, month)
            rows = database.get_movies_by_month_and_year(conn, month, year)

    conn.close()

    result = []
    for row in rows:
        obj = {
            "id": row[0],
            "title": row[1],
            "rating": row[2],
            "description": row[3],
            "image_url": row[4],
            "imdb_url": row[5],
            "year": row[6],
            "month": row[7]
        }
        result.append(obj)

    return jsonify(result)


if __name__ == "__main__":
    # Crear la conexión a la base de datos y la tabla
    conn = database.create_connection()
    database.create_series_table(conn)
    database.create_movies_table(conn)

    # Realizar web scraping y guardar los datos en la base de datos
    current_year, current_month = datetime.now().year, datetime.now().month
    series = scraper.scrape_imdb(current_year, current_month, title_type="tv_series")
    movies = scraper.scrape_imdb(current_year, current_month, title_type="movies")
    database.insert_series(conn, series, current_year, current_month)
    database.insert_movies(conn, movies, current_year, current_month)

    # Programar la actualización para ejecutarse cada mes
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    schedule.every(days_in_month).days.at("00:00").do(update_data, table_name="series")
    schedule.every(days_in_month).days.at("00:00").do(update_data, table_name="movies")

    scheduler_thread = threading.Thread(target=run_schedule)
    scheduler_thread.start()

    app.run(debug=True)
