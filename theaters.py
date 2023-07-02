import requests
import tools

def theater_finder(id:int, index:int):
    theater_list = requests.get(tools.THEATERS_URL)
    theater_data = theater_list.json()
    locals_list = theater_data['DS']['Locals']

    theaters = {}

    for local in locals_list:
        local_datas = locals_list[local]
        local_id = local_datas['LocalId']
        local_description = local_datas['Description']
        local_province = local_datas['ProvinceId']
        
        theaters[local_id] = local_description, local_province
        
    return theaters[id][index]