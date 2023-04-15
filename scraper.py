import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta
import re

def get_start_and_end_dates(year, month):
    start_date = datetime(year, month, 1)
    end_date = start_date + relativedelta(months=1) - timedelta(days=1)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    return start_date_str, end_date_str

def get_url(year, month, title_type="tv_series"):
    start_date, end_date = get_start_and_end_dates(year, month)
    return f"https://www.imdb.com/search/title/?title_type={title_type}&release_date={start_date},{end_date}&start=1&ref_=adv_nxt"

def get_item_data(item):
    title = item.select_one('.lister-item-header a')
    rating = item.select_one('.ratings-imdb-rating')
    description = item.select_one('.lister-item-content p:nth-of-type(2)')
    poster = item.select_one('.lister-item-image img')
    votes = item.select_one('.sort-num_votes-visible span:nth-of-type(2)')
    runtime = item.select_one('.runtime')
    year = item.select_one('.lister-item-year')
    genre = item.select_one('.genre')
    metascore = item.select_one('.metascore')
    certificate = item.select_one('.certificate')
    
    return {
        'title': title.text.strip() if title else "",
        'rating': float(rating['data-value'].strip()) if rating else 0.0,
        'description': description.text.strip() if description else "",
        'poster_url': update_poster_url(poster['loadlate']) if poster else "",
        'detail_url': f"https://www.imdb.com{title['href']}" if title else "",
        'votes': int(votes.text.strip().replace(",", "")) if votes else 0,
        'runtime': int(runtime.text.strip().replace(" min", "")) if runtime else 0,
        'pub_year': year.text.strip() if year else "",
        'genre': genre.text.strip() if genre else "",
        'certificate': certificate.text.strip() if certificate else "",
        'metascore': int(metascore.text.strip()) if metascore else 0
    }

def scrape_imdb(year, month, title_type="tv_series"):
    if title_type == "series":
        title_type = "tv_series"
    elif title_type == "movies":
        title_type = "movie"

    url = get_url(year, month, title_type)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    return [get_item_data(item) for item in soup.select('.lister-item.mode-advanced')]

def update_poster_url(url):
    pattern = r'@._V1_(UX|UY)\d+_(CR\d+,0,)?\d+,\d+(_AL_)?'
    new_suffix = "@._V1_SY1000_CR0,0,674,1000_AL_"
    new_url = re.sub(pattern, new_suffix, url)
    return new_url