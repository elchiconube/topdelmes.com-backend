import requests
from bs4 import BeautifulSoup
import unicodedata2

import re
from datetime import datetime

def convert_date(text):
    month_names = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    date_parts = re.findall(r'\d+|[a-zA-Záéíóúüñ]+', text)
    if len(date_parts) != 3:
        raise ValueError("La cadena de texto debe contener una fecha válida en el formato 'DD de MM de YYYY'.")

    day, month, year = int(date_parts[0]), month_names[date_parts[1].lower()], int(date_parts[2])

    date = datetime(year, month, day)
    return date.strftime('%d-%m-%Y')

def normalize_text(text):
    return unicodedata2.normalize("NFKD", text)

def get_url(title_type="tv"):
    return f"https://top10.netflix.com/es/spain/{title_type}"

def get_item_data(item, title_type):
    title = item.select_one('b')
    poster = item.select_one('picture img')
    detail = item.select_one('.banner-hours-graf a')
    position = item.select_one('.banner-expanded-negative-margin img')
    
    return {
        'title': normalize_text(title.text.strip()) if title else "",
        'poster_url': poster['src'] if poster else "",
        'detail_url': detail['href'] if detail else "",
        'position': position['alt'] if position else "",
        'title_type': title_type,
    }

def scrape_netflix(title_type="series"):
    if title_type == "series":
        title_type = "tv"
    elif title_type == "movies":
        title_type = "films"

    url = get_url(title_type)
    
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    return [get_item_data(item, title_type) for item in soup.select('.banner-title')]
