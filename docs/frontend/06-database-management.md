# 🗄️ Gestión de Base de Datos con Terragrunt

## 📋 Resumen

Este documento explica cómo gestionar la base de datos Firestore `agro-extension-db` usando Terragrunt para infraestructura como código.

## 🏗️ Arquitectura de Base de Datos

### Base de Datos Principal
- **Nombre**: `agro-extension-db`
- **Tipo**: Firestore Native
- **Ubicación**: `us-central1`
- **Proyecto**: `agro-extension-digital-npe`

### Colecciones Principales
1. **`users`** - Usuarios del sistema (admin, auditor, business_owner)
2. **`business_profiles`** - Perfiles de empresas
3. **`auditors`** - Información de auditores certificados
4. **`standards`** - Estándares de certificación
5. **`registers`** - Registros de evidencias de cumplimiento
6. **`resources`** - Recursos y documentación del sistema

## 🚀 Importación de Base de Datos Existente

### Paso 1: Importar Recurso Existente

```bash
# Navegar al proyecto
cd /workspaces/agro_extension_digital_project

# Importar base de datos en desarrollo
./scripts/import-database.sh dev

# Importar base de datos en producción (si existe)
./scripts/import-database.sh prd
```

### Paso 2: Verificar Importación

```bash
# Verificar que la base de datos está en el state de Terraform
cd cicd/stacks/dev/database
terragrunt state list

# Ver detalles del recurso importado
terragrunt state show google_firestore_database.agro_extension_db

# Ejecutar plan para verificar sincronización
terragrunt plan
```

### Paso 3: Aplicar Configuración (si es necesario)

```bash
# Solo si el plan muestra cambios deseados
terragrunt apply
```

## 🔧 Gestión Manual de Recursos

### Importar Recurso Específico

```bash
# Formato general para importación manual
cd cicd/stacks/{environment}/database
terragrunt import google_firestore_database.agro_extension_db projects/agro-extension-digital-npe/databases/agro-extension-db
```

### Verificar Estado de la Base de Datos

```bash
# Verificar que la base de datos existe en GCP
gcloud firestore databases describe agro-extension-db --project=agro-extension-digital-npe

# Listar colecciones (requiere datos)
gcloud firestore collections list --database=agro-extension-db --project=agro-extension-digital-npe
```

## 📝 Configuración por Ambiente

### Desarrollo (dev)

**Características**:
- Sin protección contra eliminación (`delete_protection_enabled = false`)
- Sin backup automático (`enable_daily_backup = false`)
- Reglas de seguridad más permisivas para testing
- Retención de backup: 7 días

**Ubicación**: `/cicd/stacks/dev/database/terragrunt.hcl`

### Producción (prd)

**Características**:
- Protección contra eliminación habilitada (`delete_protection_enabled = true`)
- Backup automático diario (`enable_daily_backup = true`)
- Reglas de seguridad estrictas
- Retención de backup: 90 días
- Validaciones adicionales de usuario activo

**Ubicación**: `/cicd/stacks/prd/database/terragrunt.hcl`

## 🔒 Reglas de Seguridad

### Estructura de Permisos

```
Admin (admin):
├── Acceso completo a todas las colecciones
├── Gestión de usuarios y roles
└── Operaciones de sistema

Auditor (auditor):
├── Lectura: auditorías asignadas, estándares, recursos
├── Escritura: reportes de auditoría
└── Solo en recursos asignados

Business Owner (business_owner):
├── Lectura/escritura: perfil propio, evidencias propias
├── Lectura: estándares, recursos, estado de auditorías
└── Sin acceso a otros perfiles
```

### Funciones de Seguridad Implementadas

```javascript
// Verificaciones principales en Firestore Rules
- isAuthenticated()      // Usuario autenticado
- getUserRole()          // Obtener rol del usuario
- isAdmin()              // Verificar si es administrador
- isAuditor()            // Verificar si es auditor
- isBusinessOwner()      // Verificar si es propietario
- isOwner(resourceData)  // Verificar ownership del recurso
- isActiveUser()         // Usuario activo (solo PRD)
```

## 🔄 Operaciones Comunes

### Aplicar Cambios en Reglas de Seguridad

```bash
# Editar reglas en el archivo terragrunt.hcl
vim cicd/stacks/dev/database/terragrunt.hcl

# Aplicar cambios
cd cicd/stacks/dev/database
terragrunt apply
```

### Crear Índices Adicionales

Los índices se definen en `/cicd/modules/database/main.tf`:

```hcl
resource "google_firestore_index" "custom_index" {
  project    = var.project_id
  database   = google_firestore_database.agro_extension_db.name
  collection = "collection_name"

  fields {
    field_path = "field1"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "field2" 
    order      = "DESCENDING"
  }
}
```

### Backup y Recuperación

```bash
# Verificar backups automáticos (solo PRD)
gcloud firestore backups list --database=agro-extension-db --project=agro-extension-digital-npe

# Crear backup manual
gcloud firestore export gs://agro-extension-digital-npe-backups/manual-backup-$(date +%Y%m%d) \
  --database=agro-extension-db \
  --project=agro-extension-digital-npe
```

## 🛠️ Troubleshooting

### Error: "Database already exists"

```bash
# La base de datos ya existe, importar en lugar de crear
./scripts/import-database.sh dev
```

### Error: "Permission denied"

```bash
# Verificar permisos IAM
gcloud projects get-iam-policy agro-extension-digital-npe

# Agregar permisos necesarios
gcloud projects add-iam-policy-binding agro-extension-digital-npe \
    --member="user:$(gcloud config get-value account)" \
    --role="roles/datastore.owner"
```

### Error: "Resource not found in state"

```bash
# Reimportar el recurso
cd cicd/stacks/dev/database
terragrunt import google_firestore_database.agro_extension_db projects/agro-extension-digital-npe/databases/agro-extension-db
```

### Limpiar State Corrupto

```bash
# Remover recurso del state (cuidado!)
terragrunt state rm google_firestore_database.agro_extension_db

# Reimportar
terragrunt import google_firestore_database.agro_extension_db projects/agro-extension-digital-npe/databases/agro-extension-db
```

## 📊 Monitoreo y Métricas

### Métricas Importantes

```bash
# Verificar uso de Firestore
gcloud firestore operations list --database=agro-extension-db --project=agro-extension-digital-npe

# Estadísticas de la base de datos
gcloud firestore databases describe agro-extension-db --project=agro-extension-digital-npe
```

### Logs de Acceso

```bash
# Ver logs de Firestore
gcloud logs read "resource.type=firestore_database" \
  --project=agro-extension-digital-npe \
  --format="table(timestamp,severity,jsonPayload.method,jsonPayload.status)"
```

## 🔗 Referencias

### Archivos Relacionados

- **Módulo Base**: `/cicd/modules/database/`
- **Config Dev**: `/cicd/stacks/dev/database/terragrunt.hcl`
- **Config Prd**: `/cicd/stacks/prd/database/terragrunt.hcl`
- **Script Import**: `/scripts/import-database.sh`
- **Schema Docs**: `/docs/frontend/data-schema.md`

### Enlaces Útiles

- [Terraform Google Provider - Firestore](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/firestore_database)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Terragrunt Documentation](https://terragrunt.gruntwork.io/docs/)

---

## 📞 Soporte

Para problemas con la base de datos:
1. Verificar logs de Terragrunt
2. Consultar documentación de Terraform Google Provider
3. Revisar permisos IAM en Google Cloud Console
4. Validar reglas de seguridad en Firebase Console
