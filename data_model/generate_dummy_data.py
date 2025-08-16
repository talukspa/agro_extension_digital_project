
import json
import random
from faker import Faker

def generate_dummy_data():
    fake = Faker()

    # Load existing data for consistency
    with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/business_profile.json', 'r', encoding='utf-8') as f:
        business_profiles = json.load(f)
    with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/standard.json', 'r', encoding='utf-8') as f:
        standards = json.load(f)

    business_ruts = [profile['rut'] for profile in business_profiles]
    standard_codes = [question['standard_code'] for template in standards for question in template['questions']]

    # Generate dummy auditors
    auditors = []
    for i in range(1, 6):
        auditor = {
            "auditor_id": i,
            "auditor_name": fake.name(),
            "auditor_email": fake.email(),
            "auditor_phone": fake.phone_number(),
            "assigned_businesses": random.sample(business_ruts, k=random.randint(1, 5))
        }
        auditors.append(auditor)

    with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/dummy/auditors.json', 'w', encoding='utf-8') as f:
        json.dump(auditors, f, indent=2)

    print("Successfully generated dummy data for auditors.")

    # Generate dummy registers
    registers = []
    for i in range(1, 21):
        register = {
            "id": i,
            "business_rut": random.choice(business_ruts),
            "standard_code": random.choice(standard_codes),
            "folder": f"/path/to/folder/{i}",
            "log": fake.text(),
            "upload_timestamp": fake.iso8601(),
            "validation_status": random.choice(["pending", "validated", "rejected"]),
            "validation_timestamp": fake.iso8601(),
            "auditor_id": random.choice([auditor['auditor_id'] for auditor in auditors]),
            "auditor_comments": fake.text()
        }
        registers.append(register)

    with open('C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/dummy/registers.json', 'w', encoding='utf-8') as f:
        json.dump(registers, f, indent=2)

    print("Successfully generated dummy data for registers.")

if __name__ == '__main__':
    generate_dummy_data()
