#!/usr/bin/env python3
"""
Script para verificar que las empresas se pueden consultar correctamente desde el frontend.
"""

from google.cloud import firestore


def test_business_query():
    """Prueba la consulta que usa el frontend para obtener empresas."""
    print("Probando consulta de business_profiles...")
    
    # Obtener cliente de Firestore
    db = firestore.Client(
        project="agro-extension-digital-npe",
        database="agro-extension-db"
    )
    
    # Consulta que simula lo que hace getAllBusinesses
    collection_ref = db.collection('business_profiles')
    query = collection_ref.order_by('legal_name')
    
    try:
        docs = query.stream()
        
        businesses = []
        for doc in docs:
            data = doc.to_dict()
            business = {
                'id': doc.id,
                'legal_name': data.get('legal_name'),
                'rut': data.get('rut'),
                'region': data.get('region'),
                'commune': data.get('commune'),
                'process_type': data.get('process_type'),
                'owner': data.get('owner'),
                'address': data.get('address')
            }
            businesses.append(business)
            
        print(f"\n✅ Consulta exitosa. Se encontraron {len(businesses)} empresas:")
        
        for i, business in enumerate(businesses[:5], 1):  # Mostrar solo las primeras 5
            print(f"\n{i}. {business['legal_name']}")
            print(f"   RUT: {business['rut']}")
            print(f"   Ubicación: {business['region']}, {business['commune']}")
            print(f"   Tipo: {business['process_type']}")
            if business['owner']:
                print(f"   Propietario: {business['owner'].get('name', 'N/A')}")
                print(f"   Email: {business['owner'].get('email', 'N/A')}")
            
        if len(businesses) > 5:
            print(f"\n... y {len(businesses) - 5} empresas más.")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return False


if __name__ == "__main__":
    test_business_query()
