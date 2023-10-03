import tomli
import argparse
import sys
import requests
import pickle
from pathlib import Path
from datetime import datetime

argParser = argparse.ArgumentParser(description='The config file path must be specified')  # noqa: E501
argParser.add_argument("-c", "--config", help="Config file absolute path")

if len(sys.argv)==1:
    argParser.print_help(sys.stderr)
    sys.exit(1)

args = argParser.parse_args()

CINEMA_ID_PATTERN = r"idcinema=(\d+)"
THEATERS_URL = "https://www.webtic.it/proxyWsl/Services/BoWtJsonServices.ashx?datasource=CREADW&wtid=webticEventsMc"
    
def configurator(section, value):
    
    with open(f"{args.config}", "rb") as f:
        toml_data = tomli.load(f)

    configuration = toml_data[section][value]
    return configuration

def notifier(body, picture):
    
    apiToken = configurator('telegram', 'token')
    chatID = configurator('telegram', 'chat_id')
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendPhoto"
    parseMode = 'HTML'
    message = body
 
    try:
        requests.post(apiURL, json={'chat_id': chatID, 'photo': picture, 'caption': message, 'parse_mode': parseMode})  # noqa: E501
    except Exception as e:
        print(e)
        
def pickle_initializer(pickle_name: str):

    CHECK_PATH= Path(pickle_name)
    current_date = datetime.now()
 
    if CHECK_PATH.is_file():
        pass
    else:
        with open(pickle_name, "wb") as file:
            pickle.dump(current_date, file)
            
def unpickler(pickle_name: str):
    
    with open(pickle_name, 'rb') as handle:
        pickle_data = pickle.load(handle)
    
    return pickle_data

def pickler(pickle_name: str, data):
    
    with open(pickle_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def command_argument(chat_message):
    message_parts = chat_message.text.split()
    return message_parts