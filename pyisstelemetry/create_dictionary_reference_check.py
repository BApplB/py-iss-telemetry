import requests
from bs4 import BeautifulSoup
import json
import module_dictionary

DICT_SOURCE = "https://raw.githubusercontent.com/ISS-Mimic/Mimic/main/docs/index.html"
dict_file = open('module_dictionary.py', 'w')
dict_list = module_dictionary.MODULES_DICT

response = requests.get(DICT_SOURCE)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find_all('table')[1]

    if table:
        result = []

        rows = table.find_all('tr')[1:]

        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 4:
                category = columns[0].text.strip()
                telemetry_info = columns[1].text.strip()
                value_id = columns[2]['id'].strip()

                entry = {
                    "name": value_id,
                    "telemetry_name": telemetry_info,
                    "telemetry_info": f"{category}: {telemetry_info}",
                    "subsystem": category,
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
