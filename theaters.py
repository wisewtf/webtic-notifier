import requests
import tools
import db

def theater_finder(id:int,item:str):
    local_id = id
    query = {'LocalId': local_id}

    theater = db.connect('webtic', 'theaters').find_one(query)
        
    return theater[item]

def theater_updater():
    
        print('Updating full theaters collection')
    
        theater_list = requests.get(tools.THEATERS_URL)
        theater_data = theater_list.json()
        locals_list = theater_data['DS']['Locals']
        
        for locals in locals_list:
            local_data = locals_list[locals]
            filter = {'LocalId': local_data['LocalId']}
            update = {'$set': local_data}
            db.connect('webtic', 'theaters').update_one(filter, update, upsert=True)
            
        print("Theater collection updated")