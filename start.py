import requests
import apprise
import tools
import re
import db
import theaters
from datetime import datetime

theaters.theater_updater()

notifier = apprise.Apprise()
notifier.add(tools.configurator('apprise', 'telegram'))

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
            type = event['Type']
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
                movie_date += f'`{key}`: {value}\n'
            
            notifier.notify(
                title=f'*NEW AVAILABLE MOVIE AT {theaters.theater_finder(int(cinema_id),"Description")}*',  # noqa: E501
                body=(
                    f'\n*Title:* {title}\n'
                    f'*Length:* {duration}\n'
                    f'*Director:* {director}\n'
                    f'*Year:* {year}\n'
                    f'*Genre(s):* {category}\n'
                    f'*Type:* {type}\n'
                    f'*3D:* {is3d}\n'
                    f'*Cinema:* `{theaters.theater_finder(int(cinema_id),"Description")}`\n'  # noqa: E501                        
                    f'\n{movie_date}\n'
                    f'[ ]({picture})\n'
                    f'[Order tickets here](https://www.webtic.it/#/shopping?action=loadLocal&localId={cinema_id})\n'
                    f'Debug: `{eventid}`\n'
                ),