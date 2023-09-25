#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import requests
import json
import jsonschema
from jsonschema import validate

# Define the XML source URL
XML_SOURCE = "https://demos.lightstreamer.com/ISSLive/assets/PUIList.xml"

ADDITIONAL_PUI_DATA = [
    {
        "Discipline": "ADCO",
        "PUI": "***nOt*aVaiLable***",
        "Public_PUI": "USLAB000PIT",
        "Description": "US Attitude Pitch",
        "OPS_NOM": "N/A",
        "ENG_NOM": "N/A",
        "UNITS": "RAD",
        "ENUM": None,
        "Format_Spec": "{0:f2}"
    },
    {
        "Discipline": "ADCO",
        "PUI": "***nOt*aVaiLable***",
        "Public_PUI": "USLAB000ROL",
        "Description": "US Attitude Roll",
        "OPS_NOM": "N/A",
        "ENG_NOM": "N/A",
        "UNITS": "RAD",
        "ENUM": None,
        "Format_Spec": "{0:f2}"
    },
    {
        "Discipline": "ADCO",
        "PUI": "***nOt*aVaiLable***",
        "Public_PUI": "USLAB000YAW",
        "Description": "US Attitude Yaw",
        "OPS_NOM": "N/A",
        "ENG_NOM": "N/A",
        "UNITS": "RAD",
        "ENUM": None,
        "Format_Spec": "{0:f2}"
    }
]

dict_file = open('../pyisstelemetry/module_dictionary.json', 'w')

# Send an HTTP request to fetch the XML content
response = requests.get(XML_SOURCE)

if response.status_code == 200:
    root = ET.fromstring(response.text)
    data = []

    # Iterate over Discipline elements
    for discipline in root.findall(".//Discipline"):
        discipline_name = discipline.get("name")

        # Iterate over Symbol elements within each Discipline
        for symbol in discipline.findall(".//Symbol"):
            pui = symbol.find("PUI").text
            public_pui = symbol.find("Public_PUI").text
            description = symbol.find("Description").text
            ops_nom = symbol.find("OPS_NOM").text
            eng_nom = symbol.find("ENG_NOM").text
            units = symbol.find("UNITS").text
            enum = symbol.find("ENUM").text
            format_spec = symbol.find("Format_Spec").text

            # Create a dictionary for the current Symbol
            entry = {
                "Discipline": discipline_name,
                "PUI": pui,
                "Public_PUI": public_pui,
                "Description": description.rstrip(),
                "OPS_NOM": ops_nom,
                "ENG_NOM": eng_nom,
                "UNITS": units,
                "ENUM": enum,
                "Format_Spec": format_spec,
            }

            data.append(entry)

    data = data + ADDITIONAL_PUI_DATA

    sorted_data = sorted(data, key=lambda x: x["Discipline"])

    json_data = json.dumps(sorted_data, indent=4)

    # Read the JSON schema from an external file
    with open('schema.json', 'r') as schema_file:
        schema = json.load(schema_file)

    try:
        # Validate the JSON data against the schema
        validate(json.loads(json_data), schema)
        dict_file.write(json_data)
        print("JSON data is valid and written to 'module_dictionary.py'.")
    except jsonschema.exceptions.ValidationError as e:
        print("JSON data validation failed:")
        print(e)
else:
    print(f"Failed to fetch the XML content. Status code: {response.status_code}")
