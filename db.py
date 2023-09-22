from pymongo import MongoClient
from tools import configurator
import re
from datetime import datetime,timedelta

def connect(db_name, collection_name):
    mongo_connect = MongoClient(configurator('database', 'host'))
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
    
    print('Database cleanup started')
    
    for query in EVENTS_DB_CONNECTION.find(({})):
        saved_date = datetime.strptime(query['Days'][-1]['Day'], '%Y-%m-%dT%H:%M:%S')
        month_old_date = datetime.now() - timedelta(weeks=4)

        filter = {"EventId": query['EventId']}

        if saved_date <= month_old_date:
            print("Deleted:", query['Title'], "from database.")
            EVENTS_DB_CONNECTION.delete_one(filter=filter)
