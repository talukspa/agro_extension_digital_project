import json
import os
from google.cloud import firestore
from jsonschema import validate, RefResolver
from pathlib import Path

# Function to ingest data from a JSON file to Firestore
def ingest_data(file_path, collection_name, schema_path, id_field=None):
    try:
        # Initialize Firestore client
        db = firestore.Client(project='agro-extension-digital-npe', database='agro-extension-db')

        # Load schema
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        # Load data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Create a resolver for local schema references
        schema_dir = Path(schema_path).parent
        resolver = RefResolver(base_uri=schema_dir.as_uri() + '/', referrer=schema)

        # Validate data against schema
        if schema.get('type') == 'object':
            for item in data:
                validate(instance=item, schema=schema, resolver=resolver)
        else:
            validate(instance=data, schema=schema, resolver=resolver)

        # Upload data to Firestore
        collection_ref = db.collection(collection_name)
        if isinstance(data, list):
            for item in data:
                if id_field and id_field in item:
                    doc_ref = collection_ref.document(str(item[id_field]))
                    doc_ref.set(item)
                else:
                    collection_ref.add(item)
        else:
            if id_field and id_field in data:
                doc_ref = collection_ref.document(str(data[id_field]))
                doc_ref.set(data)
            else:
                collection_ref.add(data)


        print(f'Successfully ingested data from {file_path} to collection {collection_name}')

    except Exception as e:
        print(f'Error ingesting data from {file_path}: {e}')

if __name__ == '__main__':
    # Define file paths and collection names
    files_to_ingest = [
        {
            'file_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/standard.json',
            'collection_name': 'standards',
            'schema_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/standard.json',
            'id_field': 'template_name'
        },
        {
            'file_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/resources.json',
            'collection_name': 'resources',
            'schema_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/resources.json',
            'id_field': 'resource_code'
        },
        {
            'file_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/standard_response.json',
            'collection_name': 'standard_responses',
            'schema_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/standard_response.json'
        },
        {
            'file_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/business_profile.json',
            'collection_name': 'business_profiles',
            'schema_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/business_profile.json',
            'id_field': 'rut'
        },
        {
            'file_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/dummy/auditors.json',
            'collection_name': 'auditors',
            'schema_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/auditor.json',
            'id_field': 'auditor_id'
        },
        {
            'file_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/dummy/registers.json',
            'collection_name': 'registers',
            'schema_path': 'C:/Users/Rodrigo/Downloads/repos/agro_extension_digital_project/data_model/data/clean/schemas/register.json',
            'id_field': 'id'
        }
    ]

    # Ingest data for each file
    for file_info in files_to_ingest:
        ingest_data(file_info['file_path'], file_info['collection_name'], file_info['schema_path'], file_info.get('id_field'))