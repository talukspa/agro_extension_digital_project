import json

def count_answers_in_surveys():
    with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/raw/surveys.data.json', 'r', encoding='utf-8') as f:
        surveys_data = json.load(f)

    for i, survey in enumerate(surveys_data):
        business_rut = None
        if survey.get('data'):
            business_rut = survey['data'][0].get('rut')
        
        answers_count = len(survey.get('data', []))
        print(f"Survey {i+1} (RUT: {business_rut}): {answers_count} answers")

count_answers_in_surveys()
