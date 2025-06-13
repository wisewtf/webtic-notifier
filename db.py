from pymongo import MongoClient
import tools

def connect(db_name, collection_name):
    mongo_connect = MongoClient(tools.configurator('database', 'host'))
    db = mongo_connect[db_name]
    collection = db[collection_name]
    return collection

EVENTS_DB_CONNECTION = connect('webtic', 'events')
THEATERS_DB_CONNECTION = connect('webtic', 'theaters')