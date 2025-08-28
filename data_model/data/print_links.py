import json

def print_links():
    with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/raw/surveys.data.json', 'r', encoding='utf-8') as f:
        surveys_data = json.load(f)

    for survey in surveys_data:
        for answer_data in survey.get('data', []):
            link = answer_data.get('link', '')
            print(link)

print_links()
