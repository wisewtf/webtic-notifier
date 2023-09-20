from pymongo import MongoClient
from tools import configurator
import re
    
def connect(db_name, collection_name):
    mongo_connect = MongoClient(configurator('database', 'host'))
    db = mongo_connect[db_name]
    collection = db[collection_name]
    return collection

def find_theater_by_province(two_letter_code):
    filter = {
        'ProvinceId': {
            '$regex': re.compile(rf"(?i){two_letter_code}")
        }
    }

    result = []
    if re.match(r'^[a-zA-Z]{2}$', two_letter_code):
        for query in connect('webtic', 'theaters').find( filter = filter ):
            result.append(query)
    else:
        result = "Specificare il codice a due lettere della provincia."  # noqa: E501
    
    return result