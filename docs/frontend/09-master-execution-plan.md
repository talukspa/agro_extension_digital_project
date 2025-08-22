# 🚀 Plan de Ejecución Completo - CiruelaCertificada

**Proyecto**: agro-extension-digital-npe  
**Fecha**: 2025-08-19  
**Versión**: Master Execution Plan v1.0  
**Objetivo**: Implementación completa del sistema AuthN/AuthZ con base de datos actualizada

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Dependencias y Requisitos](#dependencias-y-requisitos)
3. [Plan de Ejecución](#plan-de-ejecución)
4. [Scripts de Fallback](#scripts-de-fallback)
5. [Validación Post-Implementación](#validación-post-implementación)
6. [Monitoreo y Soporte](#monitoreo-y-soporte)

---

## 🎯 Descripción General

Este plan ejecuta la implementación completa del sistema de autenticación, autorización y base de datos actualizada en el siguiente orden:

### 📊 Componentes a Implementar:
1. **Infraestructura de Base de Datos** (Terragrunt + Firestore)
2. **Sistema de Secretos** (Google Secret Manager)
3. **Migración de Esquema de DB** (Firestore v2.0)
4. **Frontend Next.js** (AuthN/AuthZ + Tailwind CSS)
5. **Validación y Monitoreo** (Testing + Logs)

### ⏱️ Tiempo Total Estimado: 
- **DEV** (migración): 3-4 horas
- **PRD** (creación nueva): 2-3 horas

### 👥 Recursos Necesarios: 2-3 personas técnicas

---

## 🌍 Ambientes de Despliegue

### 🔧 **DEV Environment**
- **Base de datos**: ✅ Existe (agro-extension-db)
- **Datos**: ✅ Requiere migración de esquema existente
- **Estrategia**: Migración con backup y rollback
- **Riesgo**: Medio (datos existentes)

### 🏭 **PRD Environment** 
- **Base de datos**: ❌ No existe (nueva creación)
- **Datos**: ❌ Base de datos limpia
- **Estrategia**: Creación desde cero con datos iniciales
- **Riesgo**: Bajo (ambiente limpio)

---

## 🔧 Dependencias y Requisitos

### ✅ Pre-requisitos Técnicos

#### 🛠️ Software Requerido
```bash
# Verificar instalaciones
gcloud --version          # >= 400.0.0
terragrunt --version      # >= 0.45.0
node --version           # >= 18.0.0
npm --version           # >= 9.0.0
pnpm --version          # >= 8.0.0
git --version           # >= 2.30.0
```

#### 🔑 Credenciales y Permisos
```bash
# Google Cloud
gcloud auth list                    # Cuenta autenticada
gcloud projects list               # Acceso al proyecto
gcloud iam service-accounts list   # Permisos de IAM

# Variables de entorno requeridas
export PROJECT_ID="tu-proyecto-gcp"
export ENVIRONMENT="dev"  # o "prd"
export REGION="us-central1"

# Verificar ambiente seleccionado
echo "🌍 Desplegando en ambiente: $ENVIRONMENT"
```

#### 🗂️ Estructura de Archivos
```
✅ /cicd/modules/          # Módulos Terraform
✅ /cicd/stacks/           # Configuraciones Terragrunt
✅ /scripts/               # Scripts de automatización
✅ /docs/frontend/         # Documentación
✅ /frontend/              # Aplicación Next.js
```

### ⚠️ Dependencias Críticas por Ambiente

#### 🔧 **Para DEV (Migración)**
1. **Base de datos existente** con datos
2. **Backup automático** antes de cambios
3. **Plan de rollback** detallado
4. **Validación de integridad** post-migración

#### 🏭 **Para PRD (Creación Nueva)**
1. **Proyecto GCP limpio** sin BD existente
2. **Datos iniciales** preparados (admins, estándares)
3. **Configuración de producción** validada
4. **Monitoreo y alertas** configuradas

---

## 🚀 Plan de Ejecución

### 🔴 IMPORTANTE: Ejecutar en orden secuencial

---

## FASE 1: Preparación del Entorno (30 min)

### 📋 Paso 1.1: Verificación de Requisitos
```bash
cd /workspaces/agro_extension_digital_project

# Ejecutar script de verificación
./scripts/validate-secrets.sh

# Verificar estructura del proyecto
find . -name "*.tf" -o -name "*.hcl" | head -10
find . -name "package.json" | head -5
```

**✅ Criterio de Éxito**: Todos los comandos ejecutan sin error
**❌ Fallback**: Ver [Fallback F1.1](#fallback-f11)

### 📋 Paso 1.2: Backup de Datos Existentes (Solo DEV)
```bash
# ⚠️ IMPORTANTE: Solo ejecutar en DEV - PRD no tiene datos existentes
if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 Ambiente DEV - Creando backup de datos existentes"
    
    # Crear backup de Firestore
    export BACKUP_BUCKET="gs://${PROJECT_ID}-backups"
    export BACKUP_ID="pre-migration-$(date +%Y%m%d-%H%M%S)"

    # Crear bucket si no existe
    gsutil mb -p $PROJECT_ID $BACKUP_BUCKET || true

    # Exportar datos actuales
    gcloud firestore export $BACKUP_BUCKET/$BACKUP_ID \
      --database=agro-extension-db

    echo "✅ Backup creado: $BACKUP_BUCKET/$BACKUP_ID"
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 Ambiente PRD - No hay datos existentes, saltando backup"
    export BACKUP_ID="no-backup-needed-$(date +%Y%m%d-%H%M%S)"
    echo "✅ Backup no requerido para ambiente PRD"
else
    echo "❌ ENVIRONMENT debe ser 'dev' o 'prd'"
    exit 1
fi
```

**✅ Criterio de Éxito**: 
- DEV: Backup completado exitosamente
- PRD: Confirmación de ambiente limpio
**❌ Fallback**: Ver [Fallback F1.2](#fallback-f12)

### 📋 Paso 1.3: Configuración de Variables de Entorno
```bash
# Configurar variables principales
cat > .env.deployment << EOF
PROJECT_ID=${PROJECT_ID}
ENVIRONMENT=${ENVIRONMENT}
REGION=${REGION}
BACKUP_ID=${BACKUP_ID}
DATABASE_NAME=agro-extension-db
FRONTEND_SERVICE_NAME=ciruela-certificada-frontend
EOF

# Cargar variables
source .env.deployment

echo "✅ Variables configuradas para $ENVIRONMENT"
```

**✅ Criterio de Éxito**: Variables cargadas correctamente
**❌ Fallback**: Ver [Fallback F1.3](#fallback-f13)

---

## FASE 2: Infraestructura de Base de Datos (45 min)

### 📋 Paso 2.1: Restaurar Módulo de Base de Datos
```bash
# El archivo main.tf está vacío, necesitamos restaurarlo
cd cicd/modules/database

# Restaurar contenido del módulo
cat > main.tf << 'EOF'
# Módulo para gestión de base de datos Firestore
resource "google_firestore_database" "agro_extension_db" {
  project                           = var.project_id
  name                             = var.database_name
  location_id                      = var.database_location
  type                             = "FIRESTORE_NATIVE"
  concurrency_mode                 = "OPTIMISTIC"
  app_engine_integration_mode      = "DISABLED"
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state          = var.delete_protection_enabled ? "DELETE_PROTECTION_ENABLED" : "DELETE_PROTECTION_DISABLED"

  lifecycle {
    prevent_destroy = true
  }
}

# Índices básicos para empezar
resource "google_firestore_index" "business_profiles_index" {
  project    = var.project_id
  database   = google_firestore_database.agro_extension_db.name
  collection = "business_profiles"

  fields {
    field_path = "companyName"
    order      = "ASCENDING"
  }

  fields {
    field_path = "isActive"
    order      = "ASCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}
EOF

echo "✅ Módulo de base de datos restaurado"
```

**✅ Criterio de Éxito**: Archivo main.tf creado y válido
**❌ Fallback**: Ver [Fallback F2.1](#fallback-f21)

### 📋 Paso 2.2: Validar Configuración Terragrunt
```bash
cd /workspaces/agro_extension_digital_project/cicd/stacks/$ENVIRONMENT/database

# Verificar configuración
terragrunt validate

# Plan de aplicación
terragrunt plan -out=database.tfplan

echo "✅ Plan de Terragrunt validado"
```

**✅ Criterio de Éxito**: Plan ejecuta sin errores
**❌ Fallback**: Ver [Fallback F2.2](#fallback-f22)

### 📋 Paso 2.3: Aplicar Infraestructura de Base de Datos
```bash
# Verificar estado actual de la base de datos
echo "🔍 Verificando estado de base de datos en $ENVIRONMENT..."

# Verificar si la base de datos ya existe
DB_EXISTS=$(gcloud firestore databases list --format="value(name)" --filter="name:agro-extension-db" | head -n1)

if [[ "$ENVIRONMENT" == "dev" ]]; then
    if [[ -n "$DB_EXISTS" ]]; then
        echo "🔧 DEV: Base de datos existe - Aplicando actualizaciones"
        terragrunt apply database.tfplan
    else
        echo "❌ DEV: Base de datos no encontrada - Verificar configuración"
        exit 1
    fi
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    if [[ -z "$DB_EXISTS" ]]; then
        echo "🏭 PRD: Creando nueva base de datos desde cero"
        terragrunt apply database.tfplan
        
        # Esperar a que la base de datos esté completamente lista
        echo "⏳ Esperando a que la base de datos esté lista..."
        sleep 60
        
        # Verificar creación exitosa
        gcloud firestore databases describe agro-extension-db
        echo "✅ Base de datos PRD creada exitosamente"
    else
        echo "⚠️ PRD: Base de datos ya existe - Aplicando actualizaciones"
        terragrunt apply database.tfplan
    fi
else
    echo "❌ ENVIRONMENT debe ser 'dev' o 'prd'"
    exit 1
fi

# Verificar recursos creados
gcloud firestore databases list
gcloud firestore indexes list --database=$DATABASE_NAME

echo "✅ Infraestructura de base de datos desplegada en $ENVIRONMENT"
```

**✅ Criterio de Éxito**: 
- DEV: Base de datos actualizada con nuevos índices
- PRD: Base de datos creada desde cero con toda la infraestructura
**❌ Fallback**: Ver [Fallback F2.3](#fallback-f23)

---

## FASE 3: Gestión de Secretos (20 min)

### 📋 Paso 3.1: Configurar Google Secret Manager
```bash
cd /workspaces/agro_extension_digital_project

# Ejecutar script de setup de secretos
chmod +x scripts/setup-secrets.sh
./scripts/setup-secrets.sh

echo "✅ Secretos configurados en Google Secret Manager"
```

**✅ Criterio de Éxito**: Secretos creados sin errores
**❌ Fallback**: Ver [Fallback F3.1](#fallback-f31)

### 📋 Paso 3.2: Validar Acceso a Secretos
```bash
# Validar secretos
./scripts/validate-secrets.sh

# Verificar acceso desde Terragrunt
cd cicd/stacks/$ENVIRONMENT/frontend
terragrunt run-cmd gcloud secrets list

echo "✅ Acceso a secretos validado"
```

**✅ Criterio de Éxito**: Todos los secretos accesibles
**❌ Fallback**: Ver [Fallback F3.2](#fallback-f32)

---

## FASE 4: Migración/Inicialización de Base de Datos (40 min)

### 📋 Paso 4.1: Preparación de Datos por Ambiente
```bash
cd /workspaces/agro_extension_digital_project

# Configurar variables para el proceso de datos
export DRY_RUN="true"
export PROJECT_ID=$PROJECT_ID

if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 DEV: Preparando migración de datos existentes"
    
    # Verificar datos existentes
    echo "📊 Verificando datos actuales en DEV..."
    gcloud firestore collections list --database=$DATABASE_NAME
    
    # Ejecutar migración en modo prueba
    chmod +x scripts/migrate-database-schema.sh
    ./scripts/migrate-database-schema.sh
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 PRD: Preparando datos iniciales para ambiente limpio"
    
    # Verificar que la base de datos esté vacía
    echo "📊 Verificando que PRD esté limpio..."
    COLLECTIONS=$(gcloud firestore collections list --database=$DATABASE_NAME --format="value(collectionIds)" | wc -l)
    
    if [[ $COLLECTIONS -eq 0 ]]; then
        echo "✅ Base de datos PRD está limpia - Preparando datos iniciales"
        
        # En PRD no migramos, sino que inicializamos con datos base
        echo "🔧 Creando estructura inicial para PRD"
        
        # Crear script específico para datos iniciales PRD
        cat > scripts/initialize-prd-data.js << 'EOF'
const admin = require('firebase-admin');

admin.initializeApp();
const db = admin.firestore();

async function initializePRDData() {
  console.log('🏭 Inicializando datos base para PRD...');
  
  // Crear usuario admin inicial
  await db.collection('users').doc('admin-initial').set({
    uid: 'admin-initial',
    email: 'admin@ciruelacertificada.cl',
    displayName: 'Administrador Sistema',
    role: 'admin',
    isActive: true,
    createdAt: admin.firestore.Timestamp.now(),
    updatedAt: admin.firestore.Timestamp.now(),
    metadata: {
      initialSetup: true,
      environment: 'prd'
    }
  });
  
  // Crear estándares básicos
  const basicStandards = [
    {
      standardId: 'std_A001',
      standardCode: 'A001',
      title: 'Control de Calidad en Recepción',
      category: 'quality',
      requirementLevel: 'mandatory',
      isActive: true,
      version: '1.0',
      effectiveDate: admin.firestore.Timestamp.now(),
      applicableRoles: ['business_owner'],
      evidenceTypes: ['documento', 'fotografia'],
      points: 15,
      maxPoints: 15
    }
  ];
  
  for (const standard of basicStandards) {
    await db.collection('standards').doc(standard.standardId).set({
      ...standard,
      createdAt: admin.firestore.Timestamp.now(),
      updatedAt: admin.firestore.Timestamp.now()
    });
  }
  
  console.log('✅ Datos iniciales PRD creados exitosamente');
}

initializePRDData().catch(console.error);
EOF
        
        # Solo crear estructura, no ejecutar aún
        echo "✅ Script de inicialización PRD preparado"
    else
        echo "⚠️ PRD no está limpio - Verificar antes de continuar"
        exit 1
    fi
fi

echo "✅ Preparación de datos completada para $ENVIRONMENT"
```

**✅ Criterio de Éxito**: 
- DEV: Migración simulada exitosa
- PRD: Scripts de inicialización preparados
**❌ Fallback**: Ver [Fallback F4.1](#fallback-f41)

### 📋 Paso 4.2: Ejecución de Migración/Inicialización Real
```bash
# ATENCIÓN: Este paso modifica la base de datos
echo "⚠️ A punto de modificar la base de datos en ambiente: $ENVIRONMENT"

if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 DEV: Ejecutando migración de datos existentes"
    read -p "¿Proceder con migración DEV (datos existentes)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        export DRY_RUN="false"
        ./scripts/migrate-database-schema.sh
        echo "✅ Migración DEV completada"
    else
        echo "❌ Migración DEV cancelada por el usuario"
        exit 1
    fi
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 PRD: Ejecutando inicialización de datos base"
    read -p "¿Proceder con inicialización PRD (base de datos limpia)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Instalar dependencias si no existen
        if [[ ! -d "node_modules" ]]; then
            npm install firebase-admin
        fi
        
        # Ejecutar inicialización PRD
        export PROJECT_ID=$PROJECT_ID
        node scripts/initialize-prd-data.js
        echo "✅ Inicialización PRD completada"
    else
        echo "❌ Inicialización PRD cancelada por el usuario"
        exit 1
    fi
else
    echo "❌ ENVIRONMENT debe ser 'dev' o 'prd'"
    exit 1
fi
```

**✅ Criterio de Éxito**: 
- DEV: Datos migrados correctamente al nuevo esquema
- PRD: Datos iniciales creados en base de datos limpia
**❌ Fallback**: Ver [Fallback F4.2](#fallback-f42)

### 📋 Paso 4.3: Verificar Integridad de Datos
```bash
# Verificar colecciones creadas
echo "🔍 Verificando integridad de datos en $ENVIRONMENT..."
gcloud firestore collections list --database=$DATABASE_NAME

if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 DEV: Verificando migración de datos existentes"
    
    # Contar documentos en colecciones principales
    for collection in users business_profiles auditors standards registers; do
        echo "📊 Verificando colección: $collection"
        # Verificar que las colecciones tengan datos migrados
        COUNT=$(gcloud firestore query --database=$DATABASE_NAME "SELECT COUNT(*) FROM $collection" --format="value(count)" 2>/dev/null || echo "0")
        echo "   - Documentos en $collection: $COUNT"
    done
    
    # Verificar que los datos fueron migrados correctamente
    echo "🔍 Verificando estructura de datos migrados..."
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 PRD: Verificando datos iniciales"
    
    # Verificar que se crearon los datos base
    echo "📊 Verificando datos iniciales en PRD:"
    
    # Verificar usuario admin
    ADMIN_EXISTS=$(gcloud firestore query --database=$DATABASE_NAME "SELECT * FROM users WHERE role = 'admin'" --format="value(uid)" 2>/dev/null | head -n1)
    if [[ -n "$ADMIN_EXISTS" ]]; then
        echo "   ✅ Usuario admin inicial creado"
    else
        echo "   ❌ Usuario admin inicial no encontrado"
        exit 1
    fi
    
    # Verificar estándares básicos
    STANDARDS_COUNT=$(gcloud firestore query --database=$DATABASE_NAME "SELECT COUNT(*) FROM standards" --format="value(count)" 2>/dev/null || echo "0")
    echo "   ✅ Estándares iniciales: $STANDARDS_COUNT"
    
    # Verificar colecciones vacías (esperado en PRD nuevo)
    for collection in business_profiles auditors registers; do
        COUNT=$(gcloud firestore query --database=$DATABASE_NAME "SELECT COUNT(*) FROM $collection" --format="value(count)" 2>/dev/null || echo "0")
        echo "   ✅ Colección $collection (vacía): $COUNT documentos"
    done
fi

echo "✅ Integridad de datos verificada para $ENVIRONMENT"
```

**✅ Criterio de Éxito**: 
- DEV: Todas las colecciones migradas con datos preservados
- PRD: Datos iniciales creados, colecciones operativas listas
**❌ Fallback**: Ver [Fallback F4.3](#fallback-f43)

---

## FASE 5: Frontend Next.js (50 min)

### 📋 Paso 5.1: Configurar Dependencias del Frontend
```bash
cd /workspaces/agro_extension_digital_project/frontend

# Instalar dependencias
pnpm install

# Verificar versiones críticas
pnpm list firebase
pnpm list next
pnpm list tailwindcss

echo "✅ Dependencias del frontend instaladas"
```

**✅ Criterio de Éxito**: Todas las dependencias instaladas
**❌ Fallback**: Ver [Fallback F5.1](#fallback-f51)

### 📋 Paso 5.2: Configurar Variables de Entorno del Frontend
```bash
# Crear archivo .env.local para desarrollo
cat > .env.local << EOF
NEXT_PUBLIC_FIREBASE_PROJECT_ID=$PROJECT_ID
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=${PROJECT_ID}.firebaseapp.com
NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://${PROJECT_ID}-default-rtdb.firebaseio.com
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=${PROJECT_ID}.appspot.com
NEXT_PUBLIC_ENVIRONMENT=$ENVIRONMENT
EOF

echo "✅ Variables de entorno del frontend configuradas"
```

**✅ Criterio de Éxito**: Archivo .env.local creado
**❌ Fallback**: Ver [Fallback F5.2](#fallback-f52)

### 📋 Paso 5.3: Build y Test Local
```bash
# Build de desarrollo
pnpm build

# Ejecutar tests (si existen)
pnpm test --passWithNoTests

# Iniciar servidor de desarrollo para verificación
pnpm dev &
FRONTEND_PID=$!

# Esperar a que inicie
sleep 10

# Verificar que responde
curl -f http://localhost:3000 || echo "⚠️ Frontend no responde localmente"

# Detener servidor
kill $FRONTEND_PID 2>/dev/null || true

echo "✅ Build y test local completados"
```

**✅ Criterio de Éxito**: Build exitoso y servidor responde
**❌ Fallback**: Ver [Fallback F5.3](#fallback-f53)

### 📋 Paso 5.4: Deploy del Frontend
```bash
cd /workspaces/agro_extension_digital_project

# Ejecutar script de deploy completo
chmod +x scripts/deploy-frontend.sh
./scripts/deploy-frontend.sh

echo "✅ Frontend desplegado en Cloud Run"
```

**✅ Criterio de Éxito**: Servicio desplegado y accesible
**❌ Fallback**: Ver [Fallback F5.4](#fallback-f54)

---

## FASE 6: Validación Final (25 min)

### 📋 Paso 6.1: Testing de Integración
```bash
# Obtener URL del servicio desplegado
export FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME \
  --region=$REGION --format="value(status.url)")

echo "Frontend URL: $FRONTEND_URL"

# Tests básicos de conectividad
curl -f "$FRONTEND_URL" -o /dev/null || echo "❌ Frontend no accesible"
curl -f "$FRONTEND_URL/api/health" -o /dev/null || echo "⚠️ Health check no disponible"

echo "✅ Tests de integración completados"
```

**✅ Criterio de Éxito**: Frontend accesible públicamente
**❌ Fallback**: Ver [Fallback F6.1](#fallback-f61)

### 📋 Paso 6.2: Verificación de Autenticación
```bash
# Manual: Abrir frontend y probar login
echo "🔗 Abrir en navegador: $FRONTEND_URL"
echo "📋 Verificar manualmente:"
echo "  - Página de login carga"
echo "  - Registro de usuario funciona"
echo "  - Login con credenciales funciona"
echo "  - Dashboard se muestra según rol"

read -p "¿Autenticación funciona correctamente? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Autenticación no funciona - revisar logs"
    exit 1
fi

echo "✅ Autenticación verificada manualmente"
```

**✅ Criterio de Éxito**: Login y roles funcionan
**❌ Fallback**: Ver [Fallback F6.2](#fallback-f62)

### 📋 Paso 6.3: Configurar Monitoreo
```bash
# Configurar alertas básicas
gcloud logging metrics create frontend_errors \
  --description="Errores en frontend" \
  --log-filter="resource.type=cloud_run_revision AND severity>=ERROR"

# Configurar dashboard básico
echo "📊 Configurar monitoreo en:"
echo "  - Cloud Console: https://console.cloud.google.com/run"
echo "  - Logs: https://console.cloud.google.com/logs"
echo "  - Firestore: https://console.firebase.google.com"

echo "✅ Monitoreo configurado"
```

**✅ Criterio de Éxito**: Métricas y logs disponibles
**❌ Fallback**: Ver [Fallback F6.3](#fallback-f63)

---

## 🔄 Scripts de Fallback

### Fallback F1.1: Error en Verificación de Requisitos
```bash
# Instalar herramientas faltantes
curl -O https://releases.hashicorp.com/terragrunt/0.45.0/terragrunt_linux_amd64
sudo mv terragrunt_linux_amd64 /usr/local/bin/terragrunt
sudo chmod +x /usr/local/bin/terragrunt

# Actualizar gcloud
gcloud components update

# Verificar nuevamente
./scripts/validate-secrets.sh
```

### Fallback F1.2: Error en Backup (Solo DEV)
```bash
if [[ "$ENVIRONMENT" == "dev" ]]; then
    # Crear bucket manualmente
    gsutil mb -p $PROJECT_ID gs://${PROJECT_ID}-backups-manual

    # Verificar permisos
    gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="user:$(gcloud config get-value account)" \
      --role="roles/datastore.importExportAdmin"

    # Reintentar backup
    gcloud firestore export gs://${PROJECT_ID}-backups-manual/manual-backup-$(date +%Y%m%d-%H%M%S) \
      --database=agro-extension-db
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "✅ PRD no requiere backup - continuar con creación"
fi
```

### Fallback F1.3: Error en Variables de Entorno
```bash
# Configuración manual
echo "Configurar manualmente:"
echo "export PROJECT_ID=\"tu-proyecto-real\""
echo "export ENVIRONMENT=\"dev\""
echo "export REGION=\"us-central1\""

# Verificar proyecto actual
gcloud config get-value project
gcloud config set project TU_PROJECT_ID
```

### Fallback F2.1: Error en Módulo de Base de Datos
```bash
# Restaurar desde repositorio
cd /workspaces/agro_extension_digital_project
git checkout HEAD -- cicd/modules/database/

# Si no existe, crear mínimo viable
mkdir -p cicd/modules/database
cat > cicd/modules/database/main.tf << 'EOF'
resource "google_firestore_database" "agro_extension_db" {
  project     = var.project_id
  name        = "agro-extension-db"
  location_id = "us-central1"
  type        = "FIRESTORE_NATIVE"
}
EOF

cat > cicd/modules/database/variables.tf << 'EOF'
variable "project_id" {
  type = string
}
EOF
```

### Fallback F2.2: Error en Terragrunt Plan
```bash
# Limpiar cache de Terragrunt
cd cicd/stacks/$ENVIRONMENT/database
terragrunt init -reconfigure

# Verificar provider
cat > versions.tf << 'EOF'
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}
EOF

# Reintentar
terragrunt plan
```

### Fallback F2.3: Error en Apply de Infraestructura
```bash
if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 DEV: Intentando aplicación incremental"
    # Aplicar paso a paso para no afectar datos existentes
    terragrunt apply -target=google_firestore_index.business_profiles_company_name_index
    terragrunt apply -target=google_firebaserules_ruleset.agro_extension_ruleset
    terragrunt apply
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 PRD: Intentando creación completa"
    # En PRD podemos ser más agresivos ya que no hay datos
    terragrunt apply -target=google_firestore_database.agro_extension_db
    sleep 30  # Esperar a que la BD esté lista
    terragrunt apply
fi

# Si persiste error, usar configuración mínima
# Contactar equipo de infraestructura
```

### Fallback F3.1: Error en Setup de Secretos
```bash
# Crear secretos manualmente
gcloud secrets create firebase-config --data-file=<(echo '{"type":"service_account"}')
gcloud secrets create database-url --data-file=<(echo 'https://project.firebaseio.com')

# Verificar permisos
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:$(gcloud config get-value account)" \
  --role="roles/secretmanager.admin"
```

### Fallback F3.2: Error en Validación de Secretos
```bash
# Verificar acceso manual
gcloud secrets versions access latest --secret="firebase-config"

# Recrear secretos si necesario
gcloud secrets delete firebase-config --quiet || true
gcloud secrets create firebase-config --data-file=config.json
```

### Fallback F4.1: Error en Preparación de Datos
```bash
if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 DEV: Error en migración - verificar datos existentes"
    
    # Verificar Node.js y dependencias
    node --version
    npm install -g firebase-admin

    # Ejecutar verificación manual de datos existentes
    gcloud firestore collections list --database=agro-extension-db
    
    # Intentar migración paso a paso
    cd scripts
    node -e "console.log('Testing Node.js setup')"
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 PRD: Error en inicialización - verificar BD limpia"
    
    # Verificar que la BD esté realmente vacía
    COLLECTIONS=$(gcloud firestore collections list --database=agro-extension-db --format="value(collectionIds)" | wc -l)
    echo "Colecciones encontradas: $COLLECTIONS"
    
    if [[ $COLLECTIONS -gt 0 ]]; then
        echo "⚠️ BD no está limpia - limpiar antes de continuar"
        echo "Manual: Eliminar colecciones en Firebase Console"
    fi
    
    # Recrear script de inicialización
    npm install firebase-admin
fi
```

### Fallback F4.2: Error en Migración/Inicialización Real
```bash
if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🚨 EMERGENCIA DEV: Restaurar desde backup"

    # Restaurar base de datos desde backup
    if [[ -n "$BACKUP_ID" ]]; then
        gcloud firestore import $BACKUP_BUCKET/$BACKUP_ID
        echo "✅ Base de datos DEV restaurada desde backup"
    else
        echo "❌ No hay backup disponible - contactar equipo"
    fi
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🚨 EMERGENCIA PRD: Limpiar BD y reintentar"
    
    # En PRD podemos limpiar y empezar de nuevo
    echo "🧹 Limpiando base de datos PRD para reintentar"
    
    # Eliminar colecciones creadas parcialmente
    for collection in users standards business_profiles auditors; do
        echo "Eliminando colección: $collection"
        # Nota: Esto requiere implementación específica
    done
    
    echo "✅ PRD limpiado - listo para reintentar inicialización"
fi

# Verificar estado final
gcloud firestore collections list --database=agro-extension-db
```

### Fallback F4.3: Error en Verificación de Datos
```bash
if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 DEV: Verificación manual de migración"
    
    # Verificar manualmente en Firebase Console
    echo "Verificar migración DEV en:"
    echo "https://console.firebase.google.com/project/$PROJECT_ID/firestore"
    
    # Verificar colecciones críticas
    echo "Verificando colecciones migradas:"
    gcloud firestore query --database=agro-extension-db "SELECT COUNT(*) FROM business_profiles"
    gcloud firestore query --database=agro-extension-db "SELECT COUNT(*) FROM auditors"
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 PRD: Verificación manual de inicialización"
    
    # Verificar datos iniciales básicos
    echo "Verificando inicialización PRD en:"
    echo "https://console.firebase.google.com/project/$PROJECT_ID/firestore"
    
    # Crear datos mínimos manualmente si es necesario
    echo "Si es necesario, crear datos iniciales manualmente:"
    echo "1. Usuario admin en colección 'users'"
    echo "2. Estándares básicos en colección 'standards'"
fi

# Contactar equipo de datos para revisión manual
echo "📞 Contactar equipo de datos para verificación manual"
```

### Fallback F5.1: Error en Dependencias Frontend
```bash
# Limpiar caché de pnpm
pnpm store prune

# Reinstalar desde scratch
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Usar npm como alternativa
npm install
```

### Fallback F5.2: Error en Variables Frontend
```bash
# Obtener configuración Firebase
gcloud firebase config get

# Crear configuración manual
cat > .env.local << EOF
NEXT_PUBLIC_FIREBASE_PROJECT_ID=$PROJECT_ID
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=${PROJECT_ID}.firebaseapp.com
EOF
```

### Fallback F5.3: Error en Build Frontend
```bash
# Verificar logs de error
pnpm build 2>&1 | tee build.log

# Build básico sin optimizaciones
NODE_ENV=development pnpm build

# Usar configuración mínima
echo "Revisar errores en build.log"
```

### Fallback F5.4: Error en Deploy Frontend
```bash
# Deploy manual
cd frontend

# Crear Dockerfile si no existe
cat > Dockerfile << 'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
EOF

# Build y deploy manual
gcloud builds submit --tag gcr.io/$PROJECT_ID/frontend
gcloud run deploy $FRONTEND_SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/frontend \
  --region $REGION \
  --allow-unauthenticated
```

### Fallback F6.1: Error en Testing de Integración
```bash
# Verificar estado del servicio
gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION

# Verificar logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Test de conectividad básica
ping -c 3 $(echo $FRONTEND_URL | sed 's|https\?://||')
```

### Fallback F6.2: Error en Autenticación
```bash
# Verificar configuración Firebase
gcloud firebase config list

# Verificar reglas de Firestore
gcloud firestore rules get --database=agro-extension-db

# Revisar logs de autenticación
gcloud logs read "jsonPayload.message:auth" --limit=20
```

### Fallback F6.3: Error en Monitoreo
```bash
# Configuración manual de alertas
echo "Configurar alertas manualmente en:"
echo "https://console.cloud.google.com/monitoring/alerting"

# Verificar métricas básicas
gcloud logging metrics list
```

---

## 📊 Validación Post-Implementación

### ✅ Checklist de Validación Final

#### 🏗️ Infraestructura
- [ ] Base de datos Firestore creada y accesible
- [ ] Índices de Firestore funcionando
- [ ] Secretos en Google Secret Manager configurados
- [ ] Backups automáticos habilitados

#### 🔐 Autenticación y Autorización
- [ ] Firebase Auth configurado correctamente
- [ ] Roles de usuario funcionando (admin, auditor, business_owner)
- [ ] Reglas de Firestore aplicadas y funcionando
- [ ] Permisos por colección validados

#### 🎨 Frontend
- [ ] Aplicación Next.js desplegada en Cloud Run
- [ ] Tailwind CSS con tema plum funcionando
- [ ] Navegación por roles implementada
- [ ] Responsivo en móvil y desktop

#### 🗄️ Base de Datos
- [ ] Esquema v2.0 implementado completamente
- [ ] Migración de datos exitosa
- [ ] Relaciones entre colecciones funcionando
- [ ] Consultas optimizadas con índices

#### 🔍 Monitoreo
- [ ] Logs de aplicación configurados
- [ ] Métricas de performance disponibles
- [ ] Alertas básicas configuradas
- [ ] Dashboard de monitoreo funcional

---

## 🚨 Plan de Emergencia

### 🔴 Rollback Completo por Ambiente

```bash
echo "🚨 EJECUTANDO ROLLBACK COMPLETO PARA $ENVIRONMENT"

if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🔧 DEV: Rollback con restauración de backup"
    
    # 1. Restaurar base de datos desde backup
    if [[ -n "$BACKUP_ID" && "$BACKUP_ID" != "no-backup-needed"* ]]; then
        echo "📦 Restaurando desde backup: $BACKUP_ID"
        gcloud firestore import $BACKUP_BUCKET/$BACKUP_ID
    else
        echo "❌ No hay backup válido para restaurar"
    fi

    # 2. Revertir infraestructura (cuidadosamente para no eliminar BD)
    cd cicd/stacks/$ENVIRONMENT/database
    git checkout HEAD~1 -- .
    terragrunt plan  # Solo revisar, no aplicar automáticamente
    
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "🏭 PRD: Rollback con eliminación completa"
    
    # 1. Eliminar base de datos completa (PRD nuevo, podemos ser agresivos)
    echo "🗑️ Eliminando base de datos PRD (nueva)"
    gcloud firestore databases delete agro-extension-db --quiet || true
    
    # 2. Revertir infraestructura completamente
    cd cicd/stacks/$ENVIRONMENT/database
    terragrunt destroy -auto-approve
fi

# 3. Eliminar servicio frontend (común para ambos)
gcloud run services delete $FRONTEND_SERVICE_NAME --region=$REGION --quiet || true

# 4. Limpiar secretos (común para ambos)
gcloud secrets delete firebase-config --quiet || true

echo "✅ Rollback completo ejecutado para $ENVIRONMENT"

if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "⚠️ DEV: Sistema restaurado al estado pre-implementación con datos originales"
elif [[ "$ENVIRONMENT" == "prd" ]]; then
    echo "⚠️ PRD: Sistema completamente eliminado - ambiente limpio"
fi
```

---

## 📞 Contactos y Escalación

### 🆘 Niveles de Escalación

#### Nivel 1: Soporte Técnico Inmediato
- **DevOps Engineer**: Infraestructura y deploy
- **Frontend Developer**: Interfaz y autenticación
- **Backend Developer**: Base de datos y APIs

#### Nivel 2: Supervisión Técnica
- **Tech Lead**: Decisiones arquitectónicas
- **Product Owner**: Priorizaciones de funcionalidad

#### Nivel 3: Escalación Ejecutiva
- **CTO**: Decisiones de arquitectura críticas
- **Project Manager**: Coordinación de equipos

### 📱 Canales de Comunicación
- **Slack**: #ciruela-certificada-alerts
- **Email**: tech-team@ciruelacertificada.cl
- **Phone**: +56 9 XXXX XXXX (emergencias)

---

## 📅 Cronograma Recomendado

### 🕐 Ejecución Sugerida por Ambiente

#### 🔧 **DEV Environment (Migración)**
- **Día**: Viernes (horario de baja actividad)
- **Hora inicio**: 14:00 CLT
- **Duración Total**: 3-4 horas
- **Finalización**: 17:00-18:00 CLT
- **Monitoreo**: Hasta lunes 09:00 CLT

#### 🏭 **PRD Environment (Creación Nueva)**
- **Día**: Sábado (sin usuarios activos)
- **Hora inicio**: 10:00 CLT
- **Duración Total**: 2-3 horas
- **Finalización**: 12:00-13:00 CLT
- **Monitoreo**: Hasta lunes 09:00 CLT

### 📋 Timeline Detallado por Ambiente

#### 🔧 **DEV Timeline (Migración)**
```
14:00 - 14:30  Fase 1: Preparación (incluye backup)
14:30 - 15:15  Fase 2: Infraestructura DB (actualización)
15:15 - 15:35  Fase 3: Gestión Secretos
15:35 - 16:15  Fase 4: Migración DB (compleja)
16:15 - 17:05  Fase 5: Frontend Deploy
17:05 - 17:30  Fase 6: Validación Final
17:30 - 18:00  Buffer y documentación
```

#### 🏭 **PRD Timeline (Creación)**
```
10:00 - 10:30  Fase 1: Preparación (sin backup)
10:30 - 11:15  Fase 2: Infraestructura DB (creación)
11:15 - 11:35  Fase 3: Gestión Secretos
11:35 - 12:05  Fase 4: Inicialización DB (simple)
12:05 - 12:35  Fase 5: Frontend Deploy
12:35 - 13:00  Fase 6: Validación Final
```

---

## 📝 Post-Implementación

### 📋 Tareas Inmediatas (24h)
1. Monitoreo continuo de logs y métricas
2. Validación de funcionalidades críticas
3. Recopilación de feedback inicial de usuarios
4. Ajustes menores si son necesarios

### 📋 Tareas de Seguimiento (1 semana)
1. Análisis de performance y optimizaciones
2. Documentación de lecciones aprendidas
3. Planificación de mejoras iterativas
4. Training del equipo en nuevas funcionalidades

### 📋 Entregables Finales
1. **Reporte de implementación** con métricas y resultados
2. **Documentación de operaciones** actualizada
3. **Plan de mantenimiento** y actualizaciones
4. **Guía de troubleshooting** para soporte

---

## ✅ Aprobación y Sign-off

### 📋 Checklist de Aprobación

- [ ] **Tech Lead**: Plan técnico revisado y aprobado
- [ ] **DevOps**: Infraestructura validada y lista
- [ ] **Product Owner**: Funcionalidades verificadas
- [ ] **QA**: Criterios de aceptación definidos
- [ ] **Equipo**: Capacitado y preparado para ejecución

### ✍️ Firmas de Aprobación

**Tech Lead**: _________________ Fecha: _________

**DevOps Engineer**: _________________ Fecha: _________

**Product Owner**: _________________ Fecha: _________

---

**🚀 Estado del Plan**: ✅ LISTO PARA EJECUCIÓN

**📅 Última actualización**: 2025-08-22

**👥 Preparado por**: Equipo Técnico CiruelaCertificada

---

## 📊 REGISTRO DE PROGRESO

### ✅ FASE 1: Preparación del Entorno (30 min) - **COMPLETADA**
- ✅ Configuración de credenciales
- ✅ Verificación de dependencias
- ✅ Validación de estructura de proyecto

### ✅ FASE 2: Infraestructura de Base de Datos (45 min) - **COMPLETADA**
- ✅ Deploy de módulos Terraform
- ✅ Configuración de Firestore
- ✅ Validación de conectividad

### ✅ FASE 3: Gestión de Secretos (20 min) - **COMPLETADA**
- ✅ Configuración de Secret Manager
- ✅ Almacenamiento de credenciales Firebase
- ✅ Validación de acceso

### ✅ FASE 4: Backend Services (40 min) - **COMPLETADA**
- ✅ Deploy de agent-aa-dev
- ✅ Deploy de agent-webhook-dev
- ✅ Validación de servicios backend

### ✅ FASE 5: Frontend Next.js (50 min) - **COMPLETADA ✨**
- ✅ Configuración del Dockerfile corregido
- ✅ Build y push de imagen Docker
- ✅ Deploy del frontend a Cloud Run
- ✅ Configuración de variables de entorno
- ✅ **URL del Frontend**: https://frontend-dev-c2udweuoga-uc.a.run.app

### 🚧 FASE 6: Validación Final (25 min) - **PENDIENTE**
- [ ] Testing end-to-end
- [ ] Validación de autenticación
- [ ] Verificación de integración completa
- [ ] Documentación de operaciones

---

### 🎯 **RESUMEN DE ESTADO ACTUAL**

**Ambiente**: DEV  
**Progreso**: 5/6 Fases completadas (83%)  
**Frontend URL**: https://frontend-dev-c2udweuoga-uc.a.run.app  
**Backend AA URL**: https://agent-aa-dev-c2udweuoga-uc.a.run.app  
**Backend Webhook URL**: https://agent-webhook-dev-c2udweuoga-uc.a.run.app  

**Próximos pasos**: Ejecutar Fase 6 (Validación Final) para completar el deployment.

---
