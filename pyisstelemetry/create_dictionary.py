import requests
from bs4 import BeautifulSoup
import json
import module_dictionary

DICT_SOURCE = "https://raw.githubusercontent.com/ISS-Mimic/Mimic/main/docs/dashboard.html"
dict_file = open('module_dictionary.py', 'w')
dict_list = module_dictionary.MODULES_DICT

response = requests.get(DICT_SOURCE)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table')

    if table:
        result = []

        title_divs = table.find_all('div', attrs={'title': True})
        
        for title_div in title_divs:
            info = title_div['title']
            subsystem = title_div['class'][0]
            desc = title_div.find_next('div', class_='desc').text
            val_id = title_div.find_next('div', class_='val')['id']

            entry = {
                "name": val_id,
                "telemetry_name": desc,
                "telemetry_info": info,
                "subsystem": subsystem,
            }

            result.append(entry)

        sorted_result = sorted(result, key=lambda x: x["name"])

        json_result = json.dumps(sorted_result, indent=4)

        dict_file.write('MODULES_DICT = ')
        dict_file.write(json_result)
    else:
        print("No table found in the HTML.")
else:
    print(f"Failed to fetch the HTML content. Status code: {response.status_code}")
