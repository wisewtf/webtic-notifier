import requests

theaters_url = "https://www.webtic.it/proxyWsl/Services/BoWtJsonServices.ashx?datasource=CREADW&wtid=webticEventsMc"

theater_list = requests.get(theaters_url)
theater_data = theater_list.json()
locals_list = theater_data['DS']['Locals']

theaters = {}

for local in locals_list:
    local_datas = locals_list[local]
    local_id = local_datas['LocalId']
    local_description = local_datas['Description']
    local_province = local_datas['ProvinceId']
    
    theaters[local_id] = local_description, local_province
    
print(theaters)
