import requests
import tools
import re
import db
import theaters
from datetime import datetime, timedelta
from pathlib import Path

THEATERS_PICKLE_FILENAME = 'theater_date.pickle'
THEATERS_PICKLE_PATH = Path(THEATERS_PICKLE_FILENAME)

if not THEATERS_PICKLE_PATH.is_file():
    print('Theaters pickle file missing, initializing...')
    tools.pickle_initializer(THEATERS_PICKLE_FILENAME)
    theaters.theater_updater()
else:
    pass

saved_date = tools.unpickler(THEATERS_PICKLE_FILENAME)
current_date = datetime.now()
two_weeks_old_date = current_date - timedelta(weeks=2)

if saved_date <= two_weeks_old_date:
    print('Theater list is over two weeks old. Updating.')
    theaters.theater_updater()
else:
    pass

events_data = []

for ids in tools.configurator('webtic', 'cinema_ids'):
    events_url = f"https://secure.webtic.it/api/wtjsonservices.ashx?localid={ids}&trackid=33&wtid=getFullScheduling"
    responses = requests.get(events_url)
    events_data.append(responses.json())

print("Looking for new events")

for events in events_data:
    for event in events['DS']['Scheduling']['Events']:
        filter_query = {'EventId': event['EventId']}
        update_query = {'$set': event}
        result = db.connect('webtic', 'events').update_one(filter_query, update_query, upsert=True)  # noqa: E501

        if result.upserted_id is not None:
            calendar = {}
            for perfomances in event['Days']:
                for performance in perfomances['Performances']:
                    raw_dates = datetime.strptime(performance['StartTime'], '%Y-%m-%dT%H:%M:%S').strftime('%d/%m %H:%M')  # noqa: E501
                    dates_split = raw_dates.split(" ")
                    event_date = dates_split[0]
                    event_time = dates_split[1]
                    
                    if event_date not in calendar:
                        calendar[event_date] = ""

                    if calendar[event_date]:
                        calendar[event_date] += " - "
                    calendar[event_date] += f"{event_time}"
            eventid = event['EventId']
            title = event['Title']
            duration = event['Duration']
            event_type = event['Type']
            is3d = event['Is3D']
            director = event['Director']
            duration = event['Duration']
            picture = 'https://secure.webtic.it/api/'+event['Picture']
            year = event['Year']
            category = event['Category']
            
            match_ciema_id = re.search(tools.CINEMA_ID_PATTERN, picture)
            
            if match_ciema_id:
                cinema_id = match_ciema_id.group(1)
            else:
                cinema_id = 'could not find cinema id'
            
            movie_date = ''
            
            for key, value in calendar.items():
                movie_date += f'<code>{key}</code>: {value}\n'
            
            if event_type == "CINEMA" or not tools.configurator('general', 'cinema_events_only'):  # noqa: E501
                tools.notifier(
                    body=(
                        f'<b>NEW AVAILABLE MOVIE AT {theaters.theater_finder(int(cinema_id),"Description")}</b>\n'  # noqa: E501
                        f'\n<b>Title:</b> {title}\n'
                        f'<b>Length:</b> {duration}\n'
                        f'<b>Director:</b> {director}\n'
                        f'<b>Year:</b> {year}\n'
                        f'<b>Genre(s):</b> {category}\n'
                        f'<b>Type:</b> {event_type}\n'
                        f'<b>3D:</b> {is3d}\n'
                        f'<b>Cinema:</b> <code>{theaters.theater_finder(int(cinema_id),"Description")}</code>\n'  # noqa: E501                        
                        f'\n{movie_date}\n'
                        f'<a href="https://www.webtic.it/#/shopping?action=loadLocal&localId={cinema_id}">Order tickets here</a>\n'  # noqa: E501
                        f'Debug: <code>{eventid}</code>\n'
                    ),
                    picture=picture
                )
