#!/usr/bin/env python3
"""
Script de migración para la colección business_profiles en Firestore.

Modificaciones:
1. Eliminar campos: business_users y pendingUsers
2. Transformar campos owner_* en un objeto user embebido con user_type 'business_owner'
3. Eliminar los campos owner_* originales
4. Crear documento en colección 'users' para cada business_owner

Uso:
    uv run python data_model/migrate_business_profiles.py --dry-run  # Para simular sin cambios
    uv run python data_model/migrate_business_profiles.py           # Para ejecutar la migración
"""

import argparse
import json
from datetime import datetime
from typing import Dict, Any

from google.cloud import firestore


def generate_user_id(email: str, business_rut: str) -> str:
    """
    Genera un ID único para el usuario basado en email y RUT del negocio.
    
    Args:
        email: Email del usuario
        business_rut: RUT del negocio
        
    Returns:
        ID único para el usuario
    """
    import hashlib
    # Crear un ID determinístico basado en email y RUT
    combined = f"{email.lower().strip()}_{business_rut}"
    return hashlib.md5(combined.encode()).hexdigest()


def check_user_exists(db, user_id: str) -> bool:
    """
    Verifica si ya existe un usuario con el ID dado.
    
    Args:
        db: Cliente de Firestore
        user_id: ID del usuario a verificar
        
    Returns:
        True si el usuario existe, False si no
    """
    try:
        user_doc = db.collection('users').document(user_id).get()
        return user_doc.exists
    except Exception:
        return False


def create_business_owner_user(db, owner_data: Dict[str, Any], business_rut: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Crea un documento en la colección 'users' para el business_owner.
    Sigue el esquema actual de la colección 'users'.
    
    Args:
        db: Cliente de Firestore
        owner_data: Datos del propietario
        business_rut: RUT del negocio
        dry_run: Si True, solo simula la creación
        
    Returns:
        Diccionario con información sobre la creación del usuario
    """
    email = owner_data.get('email', '').strip()
    if not email:
        return {
            'status': 'skipped',
            'reason': 'Email vacío',
            'user_id': None
        }
    
    # Generar ID único para el usuario
    user_id = generate_user_id(email, business_rut)
    
    # Verificar si el usuario ya existe
    if check_user_exists(db, user_id):
        return {
            'status': 'already_exists',
            'reason': f'Usuario con ID {user_id} ya existe',
            'user_id': user_id
        }
    
    # Crear documento de usuario siguiendo el esquema REAL de la colección users
    user_document = {
        'uid': user_id,
        'email': email,
        'displayName': owner_data.get('name', ''),  # Usar displayName, no name
        'photoURL': '',  # Vacío inicialmente
        'userTypeId': 'business_owner',  # Usar userTypeId, no userType
        'status': 'approved',  # Estado aprobado para business_owners
        'isActive': True,  # Activo por defecto
        'createdAt': firestore.SERVER_TIMESTAMP,
        'lastLoginAt': None,  # Null inicialmente
        # Campos adicionales que podrían aparecer pero no en todos los docs:
        # 'requestedAt', 'approvedBy', 'approvedAt' - no los incluimos inicialmente
    }
    
    if dry_run:
        return {
            'status': 'dry_run',
            'reason': 'Sería creado en modo dry-run',
            'user_id': user_id,
            'user_data': user_document
        }
    
    # Crear el documento en Firestore
    try:
        db.collection('users').document(user_id).set(user_document)
        return {
            'status': 'created',
            'reason': 'Usuario creado exitosamente',
            'user_id': user_id,
            'user_data': user_document
        }
    except Exception as e:
        return {
            'status': 'error',
            'reason': f'Error creando usuario: {str(e)}',
            'user_id': user_id
        }


def get_firestore_client():
    """Obtiene el cliente de Firestore configurado."""
    return firestore.Client(
        project="agro-extension-digital-npe",
        database="agro-extension-db"
    )


def transform_owner_to_user(document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma los campos owner_* en un objeto user embebido.
    Incluye información adicional que no se almacena en la colección users.
    
    Args:
        document_data: Datos del documento business_profile
        
    Returns:
        Objeto user transformado
    """
    owner_fields = {
        'email': document_data.get('owner_email', ''),
        'name': document_data.get('owner_name', ''),
        'phone': document_data.get('owner_phone', ''),
        'role': document_data.get('owner_role', '')
    }
    
    # Crear objeto user embebido con información extendida para business_profile
    # Nota: Algunos campos como phone y role no están en el esquema users
    # pero los mantenemos en el objeto embebido para información completa
    user_object = {
        'email': owner_fields['email'],
        'name': owner_fields['name'],
        'phone': owner_fields['phone'],  # Información adicional no en users
        'role': owner_fields['role'],    # Información adicional no en users
        'userType': 'business_owner',
        'status': 'active',
        'createdAt': firestore.SERVER_TIMESTAMP,
        'lastLogin': None,
        # No incluimos uid ya que este usuario embebido no es exactamente igual
        # al documento de la colección users
    }
    
    return user_object


def migrate_business_profile(db, doc_ref, document_data: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Migra un documento individual de business_profile.
    
    Args:
        db: Cliente de Firestore
        doc_ref: Referencia al documento de Firestore
        document_data: Datos actuales del documento
        dry_run: Si True, solo simula los cambios sin aplicarlos
        
    Returns:
        Diccionario con información sobre la migración
    """
    print(f"\n🔄 Procesando documento ID: {doc_ref.id}")
    
    # Verificar si ya está migrado
    if 'owner' in document_data and all(
        field not in document_data 
        for field in ['owner_email', 'owner_name', 'owner_phone', 'owner_role']
    ):
        print("  ⏭️  Documento ya migrado, saltando...")
        return {
            'id': doc_ref.id,
            'status': 'already_migrated',
            'changes': [],
            'user_creation': {'status': 'skipped', 'reason': 'Documento ya migrado'}
        }
    
    # Crear copia de los datos para modificar
    updated_data = document_data.copy()
    changes = []
    business_rut = document_data.get('rut', '')
    
    # 1. Eliminar campos business_users y pendingUsers
    fields_to_remove = ['business_users', 'pendingUsers']
    for field in fields_to_remove:
        if field in updated_data:
            del updated_data[field]
            changes.append(f"Eliminado campo: {field}")
            print(f"  ❌ Eliminando campo: {field}")
    
    # 2. Transformar campos owner_* en objeto user embebido
    owner_fields_present = [
        field for field in ['owner_email', 'owner_name', 'owner_phone', 'owner_role']
        if field in document_data
    ]
    
    user_creation_result = {'status': 'skipped', 'reason': 'Sin campos owner_*'}
    
    if owner_fields_present:
        # Crear objeto user embebido
        owner_user = transform_owner_to_user(document_data)
        updated_data['owner'] = owner_user
        changes.append("Creado objeto 'owner' embebido con user_type 'business_owner'")
        print("  ✅ Creando objeto 'owner' embebido:")
        print(f"     - Email: {owner_user['email']}")
        print(f"     - Nombre: {owner_user['name']}")
        print(f"     - Teléfono: {owner_user['phone']}")
        print(f"     - Rol: {owner_user['role']}")
        print(f"     - User Type: {owner_user['userType']}")
        
        # 3. Crear usuario en colección 'users'
        user_creation_result = create_business_owner_user(db, owner_user, business_rut, dry_run)
        if user_creation_result['status'] == 'created':
            print(f"  👤 Usuario creado en colección 'users' con ID: {user_creation_result['user_id']}")
            print("     - Schema: uid, email, displayName, userTypeId=business_owner, status=approved")
            changes.append(f"Creado usuario en colección 'users': {user_creation_result['user_id']}")
        elif user_creation_result['status'] == 'dry_run':
            print(f"  👤 [DRY-RUN] Usuario sería creado con ID: {user_creation_result['user_id']}")
            print("     - Schema: uid, email, displayName, userTypeId=business_owner, status=approved")
        elif user_creation_result['status'] == 'already_exists':
            print(f"  👤 Usuario ya existe con ID: {user_creation_result['user_id']}")
        elif user_creation_result['status'] == 'error':
            print(f"  ❌ Error creando usuario: {user_creation_result['reason']}")
        elif user_creation_result['status'] == 'skipped':
            print(f"  ⏭️  Creación de usuario omitida: {user_creation_result['reason']}")
        
        # 4. Eliminar campos owner_* originales
        for field in owner_fields_present:
            del updated_data[field]
            changes.append(f"Eliminado campo original: {field}")
            print(f"  ❌ Eliminando campo original: {field}")
    
    # Actualizar timestamp de modificación
    updated_data['updatedAt'] = firestore.SERVER_TIMESTAMP
    changes.append("Actualizado updatedAt")
    
    # Aplicar cambios si no es dry-run
    if not dry_run and changes:
        try:
            doc_ref.set(updated_data)
            print(f"  ✅ Documento {doc_ref.id} migrado exitosamente")
            status = 'migrated'
        except Exception as e:
            print(f"  ❌ Error migrando documento {doc_ref.id}: {e}")
            status = 'error'
            changes.append(f"Error: {str(e)}")
    elif dry_run:
        print(f"  🔍 [DRY-RUN] Documento {doc_ref.id} sería migrado")
        status = 'dry_run'
    else:
        print(f"  ⚠️  Sin cambios necesarios para documento {doc_ref.id}")
        status = 'no_changes'
    
    return {
        'id': doc_ref.id,
        'status': status,
        'changes': changes,
        'owner_data': updated_data.get('owner', {}) if 'owner' in updated_data else None,
        'user_creation': user_creation_result
    }


def main():
    """Función principal del script de migración."""
    parser = argparse.ArgumentParser(
        description="Migrar colección business_profiles en Firestore"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular migración sin aplicar cambios'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limitar número de documentos a procesar (para pruebas)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 INICIANDO MIGRACIÓN DE BUSINESS_PROFILES")
    print("=" * 60)
    
    if args.dry_run:
        print("🔍 MODO DRY-RUN: Los cambios serán simulados sin aplicarse")
    else:
        print("⚠️  MODO EJECUCIÓN: Los cambios serán aplicados a Firestore")
        response = input("\n¿Continuar con la migración? (y/N): ")
        if response.lower() != 'y':
            print("❌ Migración cancelada por el usuario")
            return
    
    print(f"\nFecha/Hora: {datetime.now().isoformat()}")
    
    # Obtener cliente de Firestore
    try:
        db = get_firestore_client()
        print("✅ Conexión a Firestore establecida")
    except Exception as e:
        print(f"❌ Error conectando a Firestore: {e}")
        return
    
    # Obtener colección business_profiles
    collection_ref = db.collection('business_profiles')
    
    # Construir query
    query = collection_ref
    if args.limit:
        query = query.limit(args.limit)
        print(f"📊 Limitando procesamiento a {args.limit} documentos")
    
    # Obtener documentos
    try:
        documents = query.stream()
        print("📄 Obteniendo documentos de la colección...")
    except Exception as e:
        print(f"❌ Error obteniendo documentos: {e}")
        return
    
    # Procesar documentos
    results = []
    total_processed = 0
    
    for doc in documents:
        total_processed += 1
        document_data = doc.to_dict()
        
        # Migrar documento
        result = migrate_business_profile(db, doc.reference, document_data, args.dry_run)
        results.append(result)
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LA MIGRACIÓN")
    print("=" * 60)
    
    stats = {
        'total': total_processed,
        'migrated': len([r for r in results if r['status'] == 'migrated']),
        'already_migrated': len([r for r in results if r['status'] == 'already_migrated']),
        'dry_run': len([r for r in results if r['status'] == 'dry_run']),
        'no_changes': len([r for r in results if r['status'] == 'no_changes']),
        'errors': len([r for r in results if r['status'] == 'error'])
    }
    
    # Estadísticas de creación de usuarios
    user_stats = {
        'users_created': len([r for r in results if r.get('user_creation', {}).get('status') == 'created']),
        'users_already_exist': len([r for r in results if r.get('user_creation', {}).get('status') == 'already_exists']),
        'users_dry_run': len([r for r in results if r.get('user_creation', {}).get('status') == 'dry_run']),
        'users_skipped': len([r for r in results if r.get('user_creation', {}).get('status') == 'skipped']),
        'users_error': len([r for r in results if r.get('user_creation', {}).get('status') == 'error'])
    }
    
    print("📄 Business Profiles:")
    for status, count in stats.items():
        if count > 0:
            print(f"  {status.replace('_', ' ').title()}: {count}")
    
    print("\n👤 Usuarios:")
    for status, count in user_stats.items():
        if count > 0:
            status_display = status.replace('users_', '').replace('_', ' ').title()
            print(f"  {status_display}: {count}")
    
    # Guardar log de migración
    log_filename = f"business_profiles_migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path = f"/workspaces/agro_extension_digital_project/data_model/{log_filename}"
    
    migration_log = {
        'timestamp': datetime.now().isoformat(),
        'dry_run': args.dry_run,
        'limit': args.limit,
        'stats': stats,
        'user_stats': user_stats,
        'results': results
    }
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(migration_log, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📝 Log de migración guardado en: {log_filename}")
    
    if args.dry_run:
        print("\n🔍 Para ejecutar la migración real, ejecuta sin --dry-run")
    else:
        print("\n✅ Migración completada")


if __name__ == "__main__":
    main()
