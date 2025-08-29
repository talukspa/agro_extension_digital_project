from google.cloud import firestore
import json
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK
try:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'agro-extension-digital-npe',
    })
    db = firestore.Client(database='agro-extension-db')
except Exception as e:
    print(f"Error initializing: {e}")
    exit()

# Ingest business profiles
try:
    with open('C:\\Users\\Rodrigo\\Downloads\\repos\\agro_extension_digital_project\\data_model\\data\\clean\\business_profile.json', 'r', encoding='utf-8') as f:
        business_profiles = json.load(f)

    for profile in business_profiles:
        rut = profile.get('rut')
        if rut:
            db.collection('business_profiles').document(rut).set(profile)
    print("Successfully ingested business profiles.")
except Exception as e:
    print(f"Error ingesting business profiles: {e}")

# Ingest standards
try:
    with open('C:\\Users\\Rodrigo\\Downloads\\repos\\agro_extension_digital_project\\data_model\\data\\clean\\standard.json', 'r', encoding='utf-8') as f:
        standards = json.load(f)

    for standard in standards:
        template_name = standard.get('template_name')
        if template_name:
            db.collection('standards').document(template_name).set(standard)
    print("Successfully ingested standards.")
except Exception as e:
    print(f"Error ingesting standards: {e}")

# Ingest responses
try:
    with open('C:\\Users\\Rodrigo\\Downloads\\repos\\agro_extension_digital_project\\data_model\\data\\clean\\response.json', 'r', encoding='utf-8') as f:
        responses = json.load(f)

    for response in responses:
        db.collection('responses').add(response)
    print("Successfully ingested responses.")
except Exception as e:
    print(f"Error ingesting responses: {e}")

# Ingest auditors
try:
    with open('C:\\Users\\Rodrigo\\Downloads\\repos\\agro_extension_digital_project\\data_model\\data\\dummy\\auditor.json', 'r', encoding='utf-8') as f:
        auditors = json.load(f)

    for auditor in auditors:
        auditor_id = auditor.get('auditor_id')
        if auditor_id:
            db.collection('auditors').document(str(auditor_id)).set(auditor)
    print("Successfully ingested auditors.")
except Exception as e:
    print(f"Error ingesting auditors: {e}")