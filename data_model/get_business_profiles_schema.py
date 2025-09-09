#!/usr/bin/env python3
"""
Script para obtener el esquema actual de la colección business_profiles en Firestore.
"""

import json
from google.cloud import firestore
from typing import Dict, Any
import sys

def get_firestore_client():
    """Inicializa el cliente de Firestore"""
    try:
        # Usar Application Default Credentials
        client = firestore.Client(project="agro-extension-digital-npe", database="agro-extension-db")
        return client
    except Exception as e:
        print(f"Error al conectar con Firestore: {e}")
        return None

def analyze_document_structure(doc_data: Dict[str, Any]) -> Dict[str, str]:
    """Analiza la estructura de un documento y retorna los tipos de campos"""
    schema = {}
    
    for field, value in doc_data.items():
        if value is None:
            schema[field] = "null"
        elif isinstance(value, bool):
            schema[field] = "boolean"
        elif isinstance(value, int):
            schema[field] = "integer"
        elif isinstance(value, float):
            schema[field] = "float"
        elif isinstance(value, str):
            schema[field] = "string"
        elif isinstance(value, list):
            if len(value) > 0:
                # Analizar el tipo de elementos en la lista
                first_item_type = type(value[0]).__name__
                schema[field] = f"array<{first_item_type}>"
            else:
                schema[field] = "array<unknown>"
        elif isinstance(value, dict):
            schema[field] = "object"
        else:
            schema[field] = type(value).__name__
    
    return schema

def get_business_profiles_schema():
    """Obtiene y analiza el esquema de la colección business_profiles"""
    client = get_firestore_client()
    
    if not client:
        print("No se pudo conectar a Firestore")
        return None
    
    try:
        # Obtener la colección business_profiles
        collection_ref = client.collection('business_profiles')
        docs = collection_ref.limit(10).stream()  # Limitar a 10 documentos para análisis
        
        all_fields = set()
        doc_schemas = []
        doc_count = 0
        
        print("=== Análisis de la colección business_profiles ===\n")
        
        for doc in docs:
            doc_count += 1
            doc_data = doc.to_dict()
            
            print(f"Documento ID: {doc.id}")
            print(f"Campos encontrados: {list(doc_data.keys())}")
            
            # Analizar estructura del documento
            schema = analyze_document_structure(doc_data)
            doc_schemas.append({
                'doc_id': doc.id,
                'schema': schema,
                'data': doc_data
            })
            
            # Agregar campos únicos encontrados
            all_fields.update(doc_data.keys())
            
            print("Esquema del documento:")
            for field, field_type in schema.items():
                print(f"  {field}: {field_type}")
            
            # Mostrar datos específicos que buscamos
            print("\nCampos relevantes para la migración:")
            owner_fields = [k for k in doc_data.keys() if k.startswith('owner_')]
            if owner_fields:
                print(f"  Campos owner_*: {owner_fields}")
                for field in owner_fields:
                    print(f"    {field}: {doc_data.get(field)}")
            
            if 'pending_users' in doc_data:
                print(f"  pending_users: {doc_data['pending_users']} (tipo: {type(doc_data['pending_users'])})")
            
            if 'business_users' in doc_data:
                print(f"  business_users: {doc_data['business_users']} (tipo: {type(doc_data['business_users'])})")
            
            print("\n" + "="*50 + "\n")
        
        if doc_count == 0:
            print("No se encontraron documentos en la colección business_profiles")
            return None
        
        print("=== RESUMEN DEL ANÁLISIS ===")
        print(f"Total de documentos analizados: {doc_count}")
        print(f"Campos únicos encontrados: {sorted(all_fields)}")
        
        # Crear un esquema consolidado
        consolidated_schema = {}
        for doc_schema_info in doc_schemas:
            for field, field_type in doc_schema_info['schema'].items():
                if field in consolidated_schema:
                    if consolidated_schema[field] != field_type:
                        consolidated_schema[field] = f"{consolidated_schema[field]}|{field_type}"
                else:
                    consolidated_schema[field] = field_type
        
        print("\n=== ESQUEMA CONSOLIDADO ===")
        for field, field_type in sorted(consolidated_schema.items()):
            print(f"  {field}: {field_type}")
        
        # Verificar campos específicos para la migración
        print("\n=== VERIFICACIÓN DE CAMPOS PARA MIGRACIÓN ===")
        owner_fields = [f for f in all_fields if f.startswith('owner_')]
        print(f"Campos owner_* encontrados: {owner_fields}")
        
        has_pending_users = 'pending_users' in all_fields
        has_business_users = 'business_users' in all_fields
        
        print(f"Campo 'pending_users' presente: {has_pending_users}")
        print(f"Campo 'business_users' presente: {has_business_users}")
        
        return {
            'doc_count': doc_count,
            'all_fields': sorted(all_fields),
            'consolidated_schema': consolidated_schema,
            'doc_schemas': doc_schemas,
            'owner_fields': owner_fields,
            'has_pending_users': has_pending_users,
            'has_business_users': has_business_users
        }
        
    except Exception as e:
        print(f"Error al obtener datos de Firestore: {e}")
        return None

def main():
    """Función principal"""
    print("Iniciando análisis del esquema de business_profiles...\n")
    
    result = get_business_profiles_schema()
    
    if result:
        # Guardar el resultado en un archivo JSON para referencia
        output_file = "/workspaces/agro_extension_digital_project/data_model/business_profiles_current_schema.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Análisis completado. Resultados guardados en: {output_file}")
    else:
        print("❌ No se pudo completar el análisis")
        sys.exit(1)

if __name__ == "__main__":
    main()
