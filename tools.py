import tomli
import argparse
import sys
import requests
import pickle
import db
import re
import theaters
from pathlib import Path
from datetime import datetime, timedelta

argParser = argparse.ArgumentParser(description='The config file path must be specified')  # noqa: E501
argParser.add_argument("-c", "--config", help="Config file absolute path")

if len(sys.argv)==1:
    argParser.print_help(sys.stderr)
    sys.exit(1)

args = argParser.parse_args()

CINEMA_ID_PATTERN = r"idcinema=(\d+)"
THEATERS_URL = "https://www.webtic.it/proxyWsl/Services/BoWtJsonServices.ashx?datasource=CREADW&wtid=webticEventsMc"

def logger(message):
    print(f"[{datetime.today()}]", message)
    
def requestor(url):
    requestor_url = url
    requestor_response = requests.get(requestor_url)
    return requestor_response
    
def configurator(section, value):
    
    with open(f"{args.config}", "rb") as f:
        toml_data = tomli.load(f)

    configuration = toml_data[section][value]
    return configuration

def notifier(body, picture):

    apiToken = configurator('telegram', 'token')
    chatID = configurator('telegram', 'chat_id')
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendPhoto"
    parseMode = 'HTML'
    message = body
 
    try:
        requests.post(apiURL, json={'chat_id': chatID, 'photo': picture, 'caption': message, 'parse_mode': parseMode})  # noqa: E501
    except Exception as e:
        print(e)
        
def pickle_initializer(pickle_name: str):

    CHECK_PATH= Path(pickle_name)
    current_date = datetime.now()
 
    if CHECK_PATH.is_file():
        pass
    else:
        with open(pickle_name, "wb") as file:
            pickle.dump(current_date, file)
            
def unpickler(pickle_name: str):
    
    with open(pickle_name, 'rb') as handle:
        pickle_data = pickle.load(handle)
    
    return pickle_data

def pickler(pickle_name: str, data):
    
    with open(pickle_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def command_argument(chat_message):
    message_parts = chat_message.text.split()
    return message_parts

def remove_duplicates(str: str):
    return "".join(set(str))

def find_movie_info(title, argument):
    
    composed_message = []

    for query_result in db.find_movie_by_title(argument):
        matched_cinema_id = re.search(CINEMA_ID_PATTERN, query_result)
        if matched_cinema_id:
            cinema_id = matched_cinema_id.group(1)
            cinema_name = theaters.theater_finder(int(cinema_id), "Description")
            composed_message.append(f"{cinema_name} (<code>{cinema_id}</code>)\n")
        else:
            continue
    unique_theaters = []
    for found_theater in composed_message:
        if found_theater not in unique_theaters:
            unique_theaters.append(found_theater)
    if unique_theaters:
        unique_theaters_str = ''.join(set(unique_theaters))  # noqa: E501
    else:
        unique_theaters_str = "Non disponibile"

    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {configurator('tmdb', 'bearer_token')}"
}
    tmdb_search_url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=it-IT&page=1"
    search_response = requests.get(tmdb_search_url, headers=headers)
    
    if search_response.json()['total_results'] != 0:
        movie_id = search_response.json()['results'][0]['id']
        tmdb_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=it-IT"
        details_response = requests.get(tmdb_details_url, headers=headers)
        
        movie = details_response.json()
        
        genre_names = ', '.join([genre['name'] for genre in movie['genres']])
        company_name = [company['name'] for company in movie['production_companies']]
        origin_country = [origin['name'] for origin in movie['production_countries']]
        
        notifier(
            body=(
            f'<b>Titolo:</b> {movie["title"]}\n'
            f'<b>Titolo Originale:</b> {movie["original_title"]}\n'
            f'<b>Generi:</b> {genre_names}\n'
            f'<b>Durata:</b> {movie["runtime"]}\"\n'
            f'<b>Data di uscita:</b> {movie["release_date"]}\n'
            f'<b>Produzione:</b> <code>{company_name[0]}</code>\n'
            f'<b>Origine:</b> <code>{origin_country[0]}</code>\n'
            f'<b>Lingua Originale:</b> <code>{movie["original_language"]}</code>\n'
            f'<a href="https://www.imdb.com/title/{movie["imdb_id"]}">IMDB</a>, <a href="https://www.themoviedb.org/movie/{movie["id"]}">TMDB</a>, <a href="{movie["homepage"]}">Sito Ufficiale</a>\n'  # noqa: E501
            f'\n<b>Disponibile nei cinema di:</b>\n{unique_theaters_str}\n'
            ),
            picture=f"https://image.tmdb.org/t/p/original/{movie['poster_path']}"
        )
    else:
        notifier("Oops, non ho trovato nulla, solo questa mucca.", "https://i.pinimg.com/736x/ff/e5/21/ffe521dff8e2c6801e754de090dfaea6.jpg")
        
def generate_dates(date):
    today_date = date
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime(today_date, date_format)
    
    dates = []
    while start_date.month == datetime.strptime(today_date, date_format).month:
        dates.append(start_date.strftime(date_format))
        start_date += timedelta(days=1)

    return dates