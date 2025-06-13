import requests
import tools
import db

def theater_updater():

        theater_list = requests.get(tools.THEATERS_URL)
        theater_data = theater_list.json()
        
        locals_list = theater_data['DS']['Locals']

        if locals_list:
            tools.logger("Ricevuto lista cinema")
        else:
            tools.logger("Non ho ricevuto lista cinema")

        documents_count = db.connect('webtic', 'theaters').count_documents({})

        if len(locals_list) > documents_count:
            tools.logger('Updating theater collection.')
            for local in locals_list:
                local_data = locals_list[local]
                filter = {'LocalId': local_data['LocalId']}
                update = {'$set': local_data}
                db.connect('webtic', 'theaters').update_one(filter, update, upsert=True)
        else:
            tools.logger('Theater list is now up-to-date.')