import tools
import db

def findnew(date):
    
    tools.logger("Cerco nuovi film al Cinema Anteo")
    
    events = []
    for date in tools.generate_dates(date):
        date = date
        ANTEO_API = f'https://www.spaziocinema.info/cinema/@@get-calendario?dt={date}&cinema=Anteo+palazzo+del+cinema'
        ANTEO_GET_REQUEST = tools.requestor(ANTEO_API).json()

        for anteo_movie in ANTEO_GET_REQUEST:

            movie_dict = {
                'title': anteo_movie['title'],
                'year': anteo_movie['year'],
                'country': anteo_movie['country_name'],
                'order_url': anteo_movie['film_url_for_cinema'],
                'director': anteo_movie['director'],
                'tmdb_id': anteo_movie['tmdb_id'],
                'runtime': anteo_movie['length'],
                'language': anteo_movie['language'],
                'id': anteo_movie['id'],
                'picture': anteo_movie['playbill_path'],
                'plot': anteo_movie['plot'],
                'events': anteo_movie['orari'],
                'genre': anteo_movie['genre']
            }
            
            events.append(movie_dict)

    for new_anteo_movie in events:
        filter_query = {'id': new_anteo_movie['id']}
        update_query = {'$set': new_anteo_movie}
        result = db.connect('anteo', 'events').update_one(filter_query, update_query, upsert=True)

        if result.upserted_id is not None:
            calendar = {}

            for event_date in new_anteo_movie["events"]:
                if event_date['date'] not in calendar:
                    calendar[event_date['date']] = ""

                if calendar[event_date['date']]:
                    calendar[event_date['date']] += " - "
   
                calendar[event_date['date']] += f"{event_date['hour']}"

            dates = ''

            for key, value in calendar.items():
                dates += f'<code>{key}</code>: {value}\n'

            tools.notifier(
                body=(
                        "<b>NUOVO FILM DISPONIBILE ALL'ANTEO DI MILANO</b>\n"
                        f'\n<b>Titolo:</b> {new_anteo_movie["title"]}\n'
                        f'<b>Durata:</b> {new_anteo_movie["runtime"]} minuti\n'
                        f'<b>Regista:</b> {new_anteo_movie["director"]}\n'
                        f'<b>Origine:</b> {new_anteo_movie["country"]}\n'
                        f'<b>Lingua:</b> {new_anteo_movie["language"]}\n'
                        f'<b>Anno:</b> {new_anteo_movie["year"]}\n'
                        f'<b>Genere(i):</b> {new_anteo_movie["genre"]}\n'
                        f'<a href="https://www.themoviedb.org/movie/{new_anteo_movie["tmdb_id"]}">TMDB</a>\n'
                        f'\n{new_anteo_movie["plot"]}\n'
                        f'\nPrima data disponibile:\n'
                        f'{dates}\n'
                        f'<a href="{new_anteo_movie["order_url"]}">Ordina qui!</a>'
                ),
                picture=new_anteo_movie["picture"]
            )
        else:
            pass