# Scripts de Migración de Roles de Usuario

Este directorio contiene scripts en Python para agregar y migrar roles de usuario en Firestore.

## Scripts Disponibles

### 1. `add_business_user_simple.py` (Recomendado para inicio)
Script simple que solo agrega el nuevo tipo de usuario `business_user` a la colección `user_types`.

**Uso:**
```bash
cd /workspaces/agro_extension_digital_project/data_model
python add_business_user_simple.py
```

**Qué hace:**
- ✅ Agrega el tipo de usuario `business_user` con permisos apropiados
- ✅ Verifica si ya existe antes de crear
- ✅ Permite sobrescribir si es necesario

### 2. `add_business_user_role.py` (Migración completa)
Script completo que agrega el rol y migra datos existentes.

**Uso:**
```bash
cd /workspaces/agro_extension_digital_project/data_model
python add_business_user_role.py
```

**Qué hace:**
- ✅ Agrega el tipo de usuario `business_user`
- ✅ Migra usuarios existentes de `business_owner` a `business_user`
- ✅ Intenta eliminar el tipo `viewer` (si no hay usuarios asignados)
- ✅ Lista el estado antes y después de la migración

## Prerrequisitos

### 1. Autenticación con Google Cloud
Asegúrate de tener configuradas las credenciales de Google Cloud:

```bash
# Instalar Google Cloud CLI si no está instalado
# En el dev container ya debería estar disponible

# Autenticarse
gcloud auth application-default login

# Configurar el proyecto
gcloud config set project agro-extension-digital-npe
```

### 2. Dependencias de Python
```bash
pip install google-cloud-firestore firebase-admin
```

## Estructura del Rol `business_user`

```json
{
  "id": "business_user",
  "name": "business_user",
  "displayName": "Usuario de Empresa", 
  "description": "Usuario de empresa que puede subir evidencia y realizar operaciones del proceso de certificación desde la perspectiva empresarial",
  "permissions": [
    "manage_own_business",
    "request_certifications",
    "upload_evidence", 
    "view_own_audits",
    "manage_business_users",
    "submit_certification_requests",
    "track_certification_progress", 
    "manage_company_documents",
    "view_certification_requirements"
  ],
  "isActive": true
}
```

## Orden de Ejecución Recomendado

1. **Primero:** Ejecutar `add_business_user_simple.py` para agregar el nuevo tipo
2. **Segundo:** Verificar en la consola de Firebase que se creó correctamente
3. **Tercero:** (Opcional) Ejecutar `add_business_user_role.py` para migrar usuarios existentes

## Verificación

Después de ejecutar los scripts, puedes verificar el resultado:

1. **En Firebase Console:**
   - Ir a Firestore Database
   - Navegar a la colección `user_types` 
   - Verificar que existe el documento `business_user`

2. **Con script de verificación:**
```bash
python list_collections.py
```

## Troubleshooting

### Error de autenticación
```
Error inicializando Firebase: Could not automatically determine credentials
```
**Solución:** Ejecutar `gcloud auth application-default login`

### Error de permisos
```
Error: 403 Permission denied
```
**Solución:** Verificar que tu cuenta tenga permisos de escritura en Firestore

### Base de datos no encontrada
```
Error: Database 'agro-extension-db' not found
```
**Solución:** Verificar que la base de datos existe en el proyecto correcto

## Logs y Monitoreo

Los scripts proporcionan logs detallados que incluyen:
- ✅ Operaciones exitosas
- ⚠️ Advertencias 
- ❌ Errores
- ℹ️ Información general

Revisa la salida del script para identificar cualquier problema.
