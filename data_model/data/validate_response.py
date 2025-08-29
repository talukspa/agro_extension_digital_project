import json
import os
from jsonschema import validate, RefResolver

# a function to load all the schemas from the schemas directory
def load_schemas(schema_path):
    schemas = {}
    for filename in os.listdir(schema_path):
        if filename.endswith('.json'):
            with open(os.path.join(schema_path, filename), 'r') as f:
                schema = json.load(f)
                schemas[filename] = schema
    return schemas

# Path to the schemas directory
schema_path = r'C:\Users\Rodrigo\Downloads\repos\agro_extension_digital_project\data_model\data\clean\schemas'

# Load all schemas
all_schemas = load_schemas(schema_path)

# The main schema to validate against
main_schema = all_schemas['response.json']

# Create a resolver
resolver = RefResolver.from_schema(main_schema, store=all_schemas)

# Load the JSON data
with open(r'C:\Users\Rodrigo\Downloads\repos\agro_extension_digital_project\data_model\data\clean\response.json', 'r') as f:
    data = json.load(f)

# Validate the data against the schema
try:
    validate(instance=data, schema=main_schema, resolver=resolver)
    print("Validation successful!")
except Exception as e:
    print(f"Validation failed: {e}")