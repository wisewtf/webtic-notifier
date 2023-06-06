import requests
import apprise
import tomli
from pymongo import MongoClient

with open("config.toml", "rb") as f:
    configuration = tomli.load(f)

notifier = apprise.Apprise()
notifier.add(configuration['apprise'][0]['telegram'])

mongo_connect = MongoClient(configuration['database'][0]['host'])
db = mongo_connect['theaters']
collection = db['bellinzago']

for key, value in configuration.items():
    for item in value:
        if 'cinema_ids' in item:
            cinema_ids = item['cinema_ids']
            for id in cinema_ids:
                cinema_id = id

events_url = f"https://secure.webtic.it/api/wtjsonservices.ashx?localid={cinema_id}&trackid=33&wtid=getFullScheduling"
response = requests.get(events_url)
data = response.json()

raw_events = data['DS']['Scheduling']['Events']

new_events = []

for event in raw_events:
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
    
    notifier.notify(
        title='*NEW EVENT AT ARCADIA BELLINZAGO*',
        body=(
            f'\n*Title:* {title}\n'
            f'*Length:* {duration}\n'
            f'*Director:* {director}\n'
            f'*Year:* {year}\n'
            f'*Genre(s):* {category}\n'
            f'*Type:* {type}\n'
            f'*3D:* {is3d}\n'
            f'[ ]({picture})\n'
            f'[Order tickets here](https://www.webtic.it/#/shopping?action=loadLocal&localId=)\n'
            f'`{eventid}`'
            f'`{cinema_id}`'
        ),
    )