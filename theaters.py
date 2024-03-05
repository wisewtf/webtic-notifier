import requests
import tools
import db

def theater_finder(id,item):
    
    local_id = id
    query = {'LocalId': local_id}

    theater = db.connect('webtic', 'theaters').find_one(query)
        
    return theater[item]

def theater_updater():

        theater_list = requests.get(tools.THEATERS_URL)
        theater_data = theater_list.json()
        locals_list = theater_data['DS']['Locals']

        tools.logger('Aggiornamento lista cinema')
        for locals in locals_list:
            local_data = locals_list[locals]
            filter = {'LocalId': local_data['LocalId']}
            update = {'$set': local_data}
            db.connect('webtic', 'theaters').update_one(filter, update, upsert=True)
        tools.logger('Lista cinema aggiornata')