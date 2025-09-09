#!/usr/bin/env python3
"""
Script para analizar el esquema actual de la colección 'users' en Firestore.
"""

import json
from datetime import datetime
from typing import Dict, Any, Set

from google.cloud import firestore


def get_firestore_client():
    """Obtiene el cliente de Firestore configurado."""
    return firestore.Client(
        project="agro-extension-digital-npe",
        database="agro-extension-db"
    )


def analyze_users_schema():
    """Analiza el esquema de la colección 'users'."""
    print("Iniciando análisis del esquema de users...")
    
    # Obtener cliente de Firestore
    db = get_firestore_client()
    
    # Obtener colección users
    users_ref = db.collection('users')
    
    # Obtener todos los documentos
    docs = users_ref.stream()
    
    all_fields: Set[str] = set()
    field_types: Dict[str, Set[str]] = {}
    documents_analyzed = 0
    sample_documents = []
    
    print("\n=== Análisis de la colección users ===\n")
    
    for doc in docs:
        documents_analyzed += 1
        doc_data = doc.to_dict()
        
        print(f"Documento ID: {doc.id}")
        print(f"Campos encontrados: {list(doc_data.keys())}")
        
        # Recopilar todos los campos
        for field, value in doc_data.items():
            all_fields.add(field)
            
            # Determinar tipo del campo
            field_type = type(value).__name__
            if field_type == 'list' and value:
                element_type = type(value[0]).__name__ if value else 'unknown'
                field_type = f"array<{element_type}>"
            elif field_type == 'DocumentSnapshot':
                field_type = 'reference'
            elif hasattr(value, '__class__') and 'datetime' in str(value.__class__).lower():
                field_type = 'DatetimeWithNanoseconds'
            
            if field not in field_types:
                field_types[field] = set()
            field_types[field].add(field_type)
        
        print("Esquema del documento:")
        for field, value in doc_data.items():
            field_type = type(value).__name__
            if field_type == 'list' and value:
                element_type = type(value[0]).__name__ if value else 'unknown'
                field_type = f"array<{element_type}>"
            elif hasattr(value, '__class__') and 'datetime' in str(value.__class__).lower():
                field_type = 'DatetimeWithNanoseconds'
            
            print(f"  {field}: {field_type}")
            if field_type.startswith('array') or field == 'business_ruts':
                print(f"    Valor: {value}")
            elif isinstance(value, str) and len(str(value)) < 100:
                print(f"    Valor: {value}")
        
        # Guardar muestra de documentos para referencia
        if documents_analyzed <= 3:
            sample_documents.append({
                'id': doc.id,
                'data': doc_data
            })
        
        print("=" * 50)
    
    # Resumen consolidado
    print(f"\n=== RESUMEN DEL ANÁLISIS ===")
    print(f"Total de documentos analizados: {documents_analyzed}")
    print(f"Campos únicos encontrados: {sorted(all_fields)}")
    
    print(f"\n=== ESQUEMA CONSOLIDADO ===")
    for field in sorted(all_fields):
        types = field_types[field]
        type_str = " | ".join(sorted(types))
        print(f"  {field}: {type_str}")
    
    # Guardar resultados
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_documents': documents_analyzed,
        'all_fields': sorted(all_fields),
        'field_types': {field: sorted(types) for field, types in field_types.items()},
        'sample_documents': sample_documents
    }
    
    output_file = '/workspaces/agro_extension_digital_project/data_model/users_current_schema.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Análisis completado. Resultados guardados en: {output_file}")
    return results


if __name__ == "__main__":
    analyze_users_schema()
