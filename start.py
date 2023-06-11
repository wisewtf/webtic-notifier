import requests
import apprise
import tomli
import re
from pymongo import MongoClient

with open("config.toml", "rb") as f:
    configuration = tomli.load(f)

mongo_connect = MongoClient(configuration['database']['host'])
db = mongo_connect['webtic']
collection = db['events']

notifier = apprise.Apprise()
notifier.add(configuration['apprise']['telegram'])

cinema_id_pattern = r"idcinema=(\d+)"


events_data = []

for ids in configuration['webtic']['cinema_ids']:
    events_url = f"https://secure.webtic.it/api/wtjsonservices.ashx?localid={ids}&trackid=33&wtid=getFullScheduling"
    responses = requests.get(events_url)
    events_data.append(responses.json())

new_events = []

for events in events_data:
    for event in events['DS']['Scheduling']['Events']:
        filter_query = {'EventId': event['EventId']}
        update_query = {'$set': event}
        result = collection.update_one(filter_query, update_query, upsert=True)

        if result.upserted_id or result.modified_count > 0:
            new_events.append(event)

for new_event in new_events:
    
    eventid = new_event['EventId']
    title = new_event['Title']
    description = new_event['Description']
    duration = new_event['Duration']
    type = new_event['Type']
    is3d = new_event['Is3D']
    director = new_event['Director']
    duration = new_event['Duration']
    picture = 'https://secure.webtic.it/api/'+new_event['Picture']
    year = new_event['Year']
    category = new_event['Category']
    
    match_ciema_id = re.search(cinema_id_pattern, picture)
    
    if match_ciema_id:
        cinema_id = match_ciema_id.group(1)
    else:
        cinema_id = 'could not find cinema id'
    
    notifier.notify(
        title='*NEW EVENT AT THEATERS YOU FOLLOW*',
        body=(
            f'\n*Title:* {title}\n'
            f'*Length:* {duration}\n'
            f'*Director:* {director}\n'
            f'*Year:* {year}\n'
            f'*Genre(s):* {category}\n'
            f'*Type:* {type}\n'
            f'*3D:* {is3d}\n'
            f'[ ]({picture})\n'
            # f'[Order tickets here](https://www.webtic.it/#/shopping?action=loadLocal&localId=)\n'
            f'Debug: `{eventid}`\n'
            f'Cinema ID: `{cinema_id}`'
        ),
    )