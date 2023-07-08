from pymongo import MongoClient
from tools import configurator
    
def connect(db_name, collection_name):
    mongo_connect = MongoClient(configurator('database', 'host'))
    db = mongo_connect[db_name]
    collection = db[collection_name]
    return collection