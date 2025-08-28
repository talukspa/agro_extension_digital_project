import json
import re
from jsonschema import RefResolver, validate

def get_standard_code_from_link(link):
    match = re.search(r's=A(\d+)', link)
    if match:
        num = int(match.group(1))
        return f"A{num:03d}"
    return None

def find_standard_action(standard_data, standard_code):
    for standard in standard_data:
        for action in standard.get('actions', []):
            if action.get('standard_code') == standard_code:
                return action
    return None

def generate_responses():
    try:
        with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/raw/surveys.data.json', 'r', encoding='utf-8') as f:
            surveys_data = json.load(f)
    except FileNotFoundError:
        print("Error: surveys.data.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in surveys.data.json.")
        return

    try:
        with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/standard.json', 'r', encoding='utf-8') as f:
            standard_data = json.load(f)
    except FileNotFoundError:
        print("Error: standard.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in standard.json.")
        return

    responses = []
    for i, survey in enumerate(surveys_data):
        if not survey.get('data'):
            continue

        business_rut = survey['data'][0].get('rut')
        if not business_rut:
            continue

        answers = []
        print(f"Processing survey {i+1} for RUT: {business_rut}")
        for j, answer_data in enumerate(survey.get('data', [])):
            link = answer_data.get('link', '')
            standard_code = get_standard_code_from_link(link)
            if not standard_code:
                print(f"  Could not find standard code in link: {link}")
                continue

            standard_action = find_standard_action(standard_data, standard_code)
            if standard_action:
                answer_value = answer_data.get('answer')
                if answer_value is None:
                    answer_value = ""
                answers.append({
                    "action": standard_action,
                    "answer_value": answer_value
                })
            else:
                print(f"  Could not find standard action for code: {standard_code}")

        print(f"  Found {len(answers)} answers for survey {i+1}")
        response = {
            "business_rut": business_rut,
            "is_completed": survey.get('is_completed'),
            "date": survey.get('date'),
            "answers": answers,
            "auditor_id": "unassigned"
        }
        responses.append(response)

    with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/responses.json', 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)

    # Validate the generated file against the schema
    try:
        with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/response.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except FileNotFoundError:
        print("Error: response.json schema not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in response.json schema.")
        return

    try:
        with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/responses.json', 'r', encoding='utf-8') as f:
            instance = json.load(f)
    except FileNotFoundError:
        print("Error: responses.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in responses.json.")
        return

    try:
        schema_path = 'file:///' + 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/'
        resolver = RefResolver(base_uri=schema_path, referrer=schema)
        validate(instance=instance, schema=schema, resolver=resolver)
        print("Validation successful!")
    except ImportError:
        print("jsonschema library not found. Please install it using 'pip install jsonschema'")
    except Exception as e:
        print(f"Validation failed: {e}")


if __name__ == "__main__":
    generate_responses()
