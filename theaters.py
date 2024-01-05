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

        documents_count = db.connect('webtic', 'theaters').count_documents({})

        if len(locals_list) < documents_count:
            tools.logger('Updating theater collection')
            for locals in locals_list:
                local_data = locals_list[locals]
                filter = {'LocalId': local_data['LocalId']}
                update = {'$set': local_data}
                db.connect('webtic', 'theaters').update_one(filter, update, upsert=True)
        else:
            tools.logger('Theater list is now up-to-date.')