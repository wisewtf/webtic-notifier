import requests
import apprise
import tools
import re
import db
import theaters
import schedule
import time

def webtic_notifier():

    notifier = apprise.Apprise()
    notifier.add(tools.configurator('apprise', 'telegram')) 

    events_data = []

    for ids in tools.configurator('webtic', 'cinema_ids'):
        events_url = f"https://secure.webtic.it/api/wtjsonservices.ashx?localid={ids}&trackid=33&wtid=getFullScheduling"
        responses = requests.get(events_url)
        events_data.append(responses.json())

    new_events = []

    print("Looking for new events")

    for events in events_data:
        for event in events['DS']['Scheduling']['Events']:
            filter_query = {'EventId': event['EventId']}
            update_query = {'$set': event}
            result = db.connect('webtic', 'events').update_one(filter_query, update_query, upsert=True)  # noqa: E501

            if result.upserted_id is not None:
                new_events.append(event)

    for new_event in new_events:
        
        eventid = new_event['EventId']
        title = new_event['Title']
        duration = new_event['Duration']
        type = new_event['Type']
        is3d = new_event['Is3D']
        director = new_event['Director']
        duration = new_event['Duration']
        picture = 'https://secure.webtic.it/api/'+new_event['Picture']
        year = new_event['Year']
        category = new_event['Category']
        
        match_ciema_id = re.search(tools.CINEMA_ID_PATTERN, picture)
        
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
                f'*Cinema:* `{theaters.theater_finder(int(cinema_id),"Description")}`\n'
                f'[ ]({picture})\n'
                f'[Order tickets here](https://www.webtic.it/#/shopping?action=loadLocal&localId={cinema_id})\n'
                f'Debug: `{eventid}`\n'
            ),
        )

if tools.configurator('webtic','timer') >= 15:
    timer_value = tools.configurator('webtic','timer')
else:
    print("Timer value must not be less than 15 minutes.")
    exit()

eventSchedule = schedule.Scheduler()
theaterSchedule = schedule.Scheduler()

eventSchedule.every(timer_value).minutes.do(webtic_notifier)
theaterSchedule.every(1).weeks.do(theaters.theater_updater)

while True:
    eventSchedule.run_pending()
    theaterSchedule.run_pending()
    time.sleep(1)