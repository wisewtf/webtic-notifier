import requests
import tools
import re
import db
import theaters
from datetime import datetime

events_data = []
updated_events = []

def findnew():
    for ids in tools.configurator('webtic', 'cinema_ids'):
        events_url = f"https://secure.webtic.it/api/wtjsonservices.ashx?localid={ids}&trackid=33&wtid=getFullScheduling"
        responses = requests.get(events_url)
        events_data.append(responses.json())

    tools.logger("Looking for new events")

    for events in events_data:
        for event in events['DS']['Scheduling']['Events']:
            filter_query = {'EventId': event['EventId']}
            update_query = {'$set': event}
            result = db.connect('webtic', 'events').update_one(filter_query, update_query, upsert=True)

            if result.modified_count >= 1:
                updated_events.append(event)

            if result.upserted_id is not None:
                calendar = {}
                for perfomances in event['Days']:
                    for performance in perfomances['Performances']:
                        raw_dates = datetime.strptime(performance['StartTime'], '%Y-%m-%dT%H:%M:%S').strftime('%d/%m %H:%M')
                        dates_split = raw_dates.split(" ")
                        event_date = dates_split[0]
                        event_time = dates_split[1]
                        
                        if event_date not in calendar:
                            calendar[event_date] = ""

                        if calendar[event_date]:
                            calendar[event_date] += " - "
                        calendar[event_date] += f"{event_time}"
                bad_title = event['Title']
                eventid = event['EventId']
                event_type = event['Type']
                is3d = event['Is3D']
                director = event['Director']
                id = event['Picture']
                
                match_ciema_id = re.search(tools.CINEMA_ID_PATTERN, id)
                
                if match_ciema_id:
                    cinema_id = match_ciema_id.group(1)
                else:
                    cinema_id = 'could not find cinema id'
                
                movie_date = ''
                
                for key, value in calendar.items():
                    movie_date += f'<code>{key}</code>: {value}\n'
                    
                movie_data = tools.find_movie_info(bad_title)
                
                print(movie_data)
                
                if event_type == "CINEMA":
                    tools.notifier(
                        body=(
                                f'<b>NEW AVAILABLE MOVIE AT {theaters.theater_finder(int(cinema_id),"Description")}</b>\n'
                                f'\n<b>Title:</b> {movie_data["title"]}\n'
                                f'<b>Original Title:</b> {movie_data["original_title"]}\n'
                                f'<b>Length:</b> {movie_data["runtime"]}\n'
                                f'<b>Director:</b> {director}\n'
                                f'<b>Origin:</b> {movie_data["origin"]}\n'
                                f'<b>Original Language:</b> {movie_data["original_language"]}\n'
                                f'<b>Release:</b> {movie_data["release_date"]}\n'
                                f'<b>Genre(s):</b> {movie_data["genre_names"]}\n'
                                f'<b>Production:</b> {movie_data["production"]}\n'
                                f'<b>Type:</b> {event_type}\n'
                                f'<b>3D:</b> {is3d}\n'
                                f'{movie_data["website"]}, {movie_data["imdb"]}, {movie_data["tmdb"]}'
                                f'<b>Cinema:</b> <code>{theaters.theater_finder(int(cinema_id),"Description")}</code>\n'                       
                                f'\n{movie_date}\n'
                                f'<a href="https://www.webtic.it/#/shopping?action=loadLocal&localId={cinema_id}">Order tickets here</a>\n'
                                f'Tracking code: <code>{eventid}</code>\n'
                        ),
                        picture={movie_data["picture"]}
                    )
                else:
                    pass

# def findupdated():
#     for updated_event in updated_events:
#         print(updated_event['EventId'])
#         updated_movie = db.tracking_checker(updated_event['EventId'])
#         if updated_movie:
#             calendar = {}
#             for perfomances in updated_movie['Days']:
#                 for performance in perfomances['Performances']:
#                     raw_dates = datetime.strptime(performance['StartTime'], '%Y-%m-%dT%H:%M:%S').strftime('%d/%m %H:%M')
#                     dates_split = raw_dates.split(" ")
#                     event_date = dates_split[0]
#                     event_time = dates_split[1]
                    
#                     if event_date not in calendar:
#                         calendar[event_date] = ""

#                     if calendar[event_date]:
#                         calendar[event_date] += " - "
#                     calendar[event_date] += f"{event_time}"

#             eventid = updated_movie['EventId']
#             title = updated_movie['Title']
#             picture = 'https://secure.webtic.it/api/'+updated_movie['Picture']
            
#             match_ciema_id = re.search(tools.CINEMA_ID_PATTERN, picture)
            
#             if match_ciema_id:
#                 cinema_id = match_ciema_id.group(1)
#             else:
#                 cinema_id = 'could not find cinema id'
            
#             movie_date = ''
            
#             for key, value in calendar.items():
#                 movie_date += f'<code>{key}</code>: {value}\n'

#             tools.notifier(
#                 body=(
#                     f'<b>A MOVIE YOU TRACK HAS BEEN UPDATED</b>\n'
#                     f'\n<b>Title:</b> {title}\n'
#                     f'<b>Cinema:</b> <code>{theaters.theater_finder(int(cinema_id),"Description")}</code>\n'                       
#                     f'\n{movie_date}\n'
#                     f'<a href="https://www.webtic.it/#/shopping?action=loadLocal&localId={cinema_id}">Order tickets here</a>\n'
#                     f'Tracking code: <code>{eventid}</code>\n'
#                 ),
#                 picture=picture
#             )
#         else:
#             pass