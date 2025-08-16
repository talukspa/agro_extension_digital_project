import json
import pandas as pd
import numpy as np
import ast

# Load the two JSON files
with open(r'C:\Users\Rodrigo\Downloads\repos\agro_extension_digital_project\data_model\data\clean\standard_aa.json', 'r', encoding='utf-8') as f:
    standard_aa = json.load(f)

with open(r'C:\Users\Rodrigo\Downloads\repos\agro_extension_digital_project\data_model\data\clean\standard_pp.json', 'r', encoding='utf-8') as f:
    standard_pp = json.load(f)

# Function to process questions from a standard
def process_questions(standard_data):
    questions = standard_data.get('questions', [])
    for question in questions:
        # Handle verification_type (convert NaN to empty string)
        if 'verification_type' in question and pd.isna(question['verification_type']):
            question['verification_type'] = ""
        
        # Ensure linked_resources are strings
        if 'linked_resources' in question and isinstance(question['linked_resources'], list):
            question['linked_resources'] = [str(res) for res in question['linked_resources']]
    return questions

# Process questions for both standards
standard_aa['questions'] = process_questions(standard_aa)
standard_pp['questions'] = process_questions(standard_pp)

# Create a list containing the two standards
all_standards = [standard_aa, standard_pp]

# Write the new JSON to a file
with open(r'C:\Users\Rodrigo\Downloads\repos\agro_extension_digital_project\data_model\data\clean\standard.json', 'w', encoding='utf-8') as f:
    json.dump(all_standards, f, ensure_ascii=False, indent=2)

print('File standard.json generated successfully.')