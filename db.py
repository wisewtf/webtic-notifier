from pymongo import MongoClient
import re
import tools
from datetime import datetime,timedelta

def connect(db_name, collection_name):
    mongo_connect = MongoClient(tools.configurator('database', 'host'))
    db = mongo_connect[db_name]
    collection = db[collection_name]
    return collection

EVENTS_DB_CONNECTION = connect('webtic', 'events')
THEATERS_DB_CONNECTION = connect('webtic', 'theaters')

def find_theater_by_province(two_letter_code):
    filter = {
        'ProvinceId': {
            '$regex': re.compile(rf"(?i){two_letter_code}")
        }
    }

    result = []
    if re.match(r'^[a-zA-Z]{2}$', two_letter_code):
        for query in THEATERS_DB_CONNECTION.find( filter = filter ):
            result.append(query)
    else:
        result = "Specificare il codice a due lettere della provincia."  # noqa: E501
    
    return result

def database_cleanup():
    
    tools.logger('Database cleanup started')
    
    for query in EVENTS_DB_CONNECTION.find(({})):
        saved_date = datetime.strptime(query['Days'][-1]['Day'], '%Y-%m-%dT%H:%M:%S')
        month_old_date = datetime.now() - timedelta(weeks=4)

        filter = {"EventId": query['EventId']}

        if saved_date <= month_old_date:
            tools.logger(f"Deleted: {query['Title']} from database.")
            EVENTS_DB_CONNECTION.delete_one(filter=filter)
        else:
            tools.logger(f"No need to delete: {query['Title']} from database.")

def find_movie_by_title(movie_title):

    filter = {
        'Title': {
            '$regex': re.compile(rf"(?i){movie_title}")
        }
    }

    theaters = []

    for query in EVENTS_DB_CONNECTION.find(filter = filter):
        theaters.append(query['Picture'])

    if not theaters:
        return 'No theaters found.'
    else:
        return theaters

def tracking_checker(eventid):
    filter_query = {'EventId': eventid}
    result = EVENTS_DB_CONNECTION.find_one(filter_query)
    
    if result['Tracked']:
        tracking_value = result
    else:
        pass

    return tracking_value

def track_movie(tracking_code: int):
    result = EVENTS_DB_CONNECTION.update_many({"EventId": tracking_code}, {"$set": {"Tracked": True}})
    tools.logger(f'Tracking movie: {tracking_code}')
    return result.modified_count

def untrack_movie(tracking_code: int):
    result = EVENTS_DB_CONNECTION.update_many({"EventId": tracking_code}, {"$set": {"Tracked": False}})
    tools.logger(f'Untracking movie: {tracking_code}')
    return result.modified_count