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

    if year > current_year or (year == current_year and month > current_month):
        return jsonify({"error": "Invalid date value"}), 400

    conn = database.create_connection()
    rows = database.get_data_by_month_and_year(conn, month, year, table_name)

    if not rows:
        data = scraper.scrape_imdb(year, month, title_type=table_name)
        database.insert_data(conn, data, year, month, table_name)
        rows = database.get_data_by_month_and_year(conn, month, year, table_name)

    conn.close()

    result = [dict(zip(('id', 'title', 'rating', 'description', 'poster_url', 'detail_url', 'votes', 'runtime', 'pub_year', 'genre', 'certificate', 'metascore', 'year', 'month'), row)) for row in rows]

    return jsonify(result)

@app.route("/series", methods=["GET"])
@require_api_key
def get_series():
    return get_data("series")

@app.route("/movies", methods=["GET"])
@require_api_key
def get_movies():
    return get_data("movies")

if __name__ == "__main__":
    # Crear la conexión a la base de datos y la tabla
    conn = database.create_connection()
    database.create_table(conn, "series")
    database.create_table(conn, "movies")

    # Realizar web scraping y guardar los datos en la base de datos
    current_year, current_month = datetime.now().year, datetime.now().month
    series = scraper.scrape_imdb(current_year, current_month, title_type="tv_series")
    movies = scraper.scrape_imdb(current_year, current_month, title_type="movies")
    database.insert_data(conn, series, current_year, current_month, "series")
    database.insert_data(conn, movies, current_year, current_month, "movies")

    # Programar la actualización para ejecarse cada mes
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    schedule.every(days_in_month).days.at("00:00").do(update_data, table_name="series")
    schedule.every(days_in_month).days.at("00:00").do(update_data, table_name="movies")
    scheduler_thread = threading.Thread(target=run_schedule)
    scheduler_thread.start()

    app.run(debug=True)