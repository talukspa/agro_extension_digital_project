#!/bin/bash

# Script de migración para actualizar el esquema de base de datos
# Versión: 2.0 - Optimizada para AuthN/AuthZ
# Fecha: 2025-08-19

set -euo pipefail

# Variables
PROJECT_ID="${PROJECT_ID:-}"
DATABASE_NAME="${DATABASE_NAME:-agro-extension-db}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
DRY_RUN="${DRY_RUN:-true}"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v gcloud &> /dev/null; then
        error "gcloud CLI no está instalado"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        error "Node.js no está instalado"
        exit 1
    fi
    
    success "Dependencias verificadas"
}

# Verificar configuración
check_configuration() {
    log "Verificando configuración..."
    
    if [[ -z "$PROJECT_ID" ]]; then
        error "PROJECT_ID no está configurado"
        exit 1
    fi
    
    # Verificar autenticación con gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 &> /dev/null; then
        error "No hay una cuenta activa en gcloud. Ejecuta: gcloud auth login"
        exit 1
    fi
    
    # Configurar proyecto
    gcloud config set project "$PROJECT_ID"
    
    success "Configuración verificada para proyecto: $PROJECT_ID"
}

# Crear script de migración Node.js
create_migration_script() {
    log "Creando script de migración..."
    
    cat > migration-script.js << 'EOF'
const admin = require('firebase-admin');

// Inicializar Firebase Admin SDK
const serviceAccount = process.env.GOOGLE_APPLICATION_CREDENTIALS 
  ? require(process.env.GOOGLE_APPLICATION_CREDENTIALS)
  : null;

if (serviceAccount) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: `https://${process.env.PROJECT_ID}-default-rtdb.firebaseio.com/`
  });
} else {
  // Usar credenciales por defecto de Google Cloud
  admin.initializeApp();
}

const db = admin.firestore();

async function migrateData() {
  const dryRun = process.env.DRY_RUN === 'true';
  
  console.log(`🚀 Iniciando migración de datos (DRY_RUN: ${dryRun})`);
  
  try {
    // 1. Migrar business_profiles a users
    console.log('\n📋 1. Migrando business_profiles a colección users...');
    await migrateBusinessProfilesToUsers(dryRun);
    
    // 2. Migrar auditors a users
    console.log('\n👨‍💼 2. Migrando auditors a colección users...');
    await migrateAuditorsToUsers(dryRun);
    
    // 3. Actualizar estructura de business_profiles
    console.log('\n🏢 3. Actualizando estructura de business_profiles...');
    await updateBusinessProfilesStructure(dryRun);
    
    // 4. Actualizar estructura de auditors
    console.log('\n🔍 4. Actualizando estructura de auditors...');
    await updateAuditorsStructure(dryRun);
    
    // 5. Actualizar estructura de registers
    console.log('\n📄 5. Actualizando estructura de registers...');
    await updateRegistersStructure(dryRun);
    
    // 6. Actualizar estructura de standards
    console.log('\n📋 6. Actualizando estructura de standards...');
    await updateStandardsStructure(dryRun);
    
    // 7. Actualizar estructura de resources
    console.log('\n📚 7. Actualizando estructura de resources...');
    await updateResourcesStructure(dryRun);
    
    console.log('\n✅ Migración completada exitosamente');
    
  } catch (error) {
    console.error('❌ Error durante la migración:', error);
    process.exit(1);
  }
}

async function migrateBusinessProfilesToUsers(dryRun) {
  const businessProfiles = await db.collection('business_profiles').get();
  let processed = 0;
  
  for (const doc of businessProfiles.docs) {
    const data = doc.data();
    
    const userData = {
      uid: `migrated_business_${doc.id}`,
      email: data.contactEmail || `${doc.id}@temp.com`,
      displayName: data.contactName || data.companyName,
      role: 'business_owner',
      isActive: data.isActive !== undefined ? data.isActive : true,
      businessProfileId: doc.id,
      createdAt: data.createdAt || admin.firestore.Timestamp.now(),
      updatedAt: admin.firestore.Timestamp.now(),
      metadata: {
        migratedFrom: 'business_profiles',
        originalId: doc.id
      }
    };
    
    console.log(`  - Creando usuario para empresa: ${data.companyName} (${userData.email})`);
    
    if (!dryRun) {
      await db.collection('users').doc(userData.uid).set(userData);
      
      // Actualizar business_profile con uid
      await db.collection('business_profiles').doc(doc.id).update({
        uid: userData.uid,
        updatedAt: admin.firestore.Timestamp.now()
      });
    }
    
    processed++;
  }
  
  console.log(`  ✓ Procesados ${processed} perfiles de empresa`);
}

async function migrateAuditorsToUsers(dryRun) {
  const auditors = await db.collection('auditors').get();
  let processed = 0;
  
  for (const doc of auditors.docs) {
    const data = doc.data();
    
    const userData = {
      uid: `migrated_auditor_${doc.id}`,
      email: data.auditor_email || data.auditorEmail,
      displayName: data.auditor_name || data.auditorName,
      role: 'auditor',
      isActive: data.isActive !== undefined ? data.isActive : true,
      auditorProfileId: doc.id,
      createdAt: data.createdAt || admin.firestore.Timestamp.now(),
      updatedAt: admin.firestore.Timestamp.now(),
      metadata: {
        migratedFrom: 'auditors',
        originalId: doc.id
      }
    };
    
    console.log(`  - Creando usuario para auditor: ${userData.displayName} (${userData.email})`);
    
    if (!dryRun) {
      await db.collection('users').doc(userData.uid).set(userData);
      
      // Actualizar auditor con uid
      await db.collection('auditors').doc(doc.id).update({
        uid: userData.uid,
        updatedAt: admin.firestore.Timestamp.now()
      });
    }
    
    processed++;
  }
  
  console.log(`  ✓ Procesados ${processed} perfiles de auditor`);
}

async function updateBusinessProfilesStructure(dryRun) {
  const profiles = await db.collection('business_profiles').get();
  let updated = 0;
  
  for (const doc of profiles.docs) {
    const data = doc.data();
    
    const updates = {
      businessProfileId: doc.id,
      certificationStatus: data.certificationStatus || 'pending',
      isActive: data.isActive !== undefined ? data.isActive : true,
      updatedAt: admin.firestore.Timestamp.now()
    };
    
    // Solo agregar campos nuevos que no existan
    if (!data.address && (data.businessAddress || data.companyAddress)) {
      updates.address = {
        street: data.businessAddress || data.companyAddress || '',
        city: data.city || '',
        region: data.region || '',
        country: 'Chile'
      };
    }
    
    console.log(`  - Actualizando perfil: ${data.companyName}`);
    
    if (!dryRun) {
      await db.collection('business_profiles').doc(doc.id).update(updates);
    }
    
    updated++;
  }
  
  console.log(`  ✓ Actualizados ${updated} perfiles de empresa`);
}

async function updateAuditorsStructure(dryRun) {
  const auditors = await db.collection('auditors').get();
  let updated = 0;
  
  for (const doc of auditors.docs) {
    const data = doc.data();
    
    const updates = {
      auditorId: doc.id,
      auditorName: data.auditor_name || data.auditorName,
      auditorEmail: data.auditor_email || data.auditorEmail,
      auditorPhone: data.auditor_phone || data.auditorPhone,
      certificationLevel: data.certificationLevel || 'senior',
      specializations: data.specializations || ['agricultura_organica'],
      maxConcurrentAudits: data.maxConcurrentAudits || 5,
      currentAuditsCount: data.currentAuditsCount || 0,
      completedAuditsCount: data.completedAuditsCount || 0,
      languages: data.languages || ['es'],
      availableRegions: data.availableRegions || ['Region_del_Maule'],
      isActive: data.isActive !== undefined ? data.isActive : true,
      hireDateAt: data.hireDateAt || admin.firestore.Timestamp.now(),
      updatedAt: admin.firestore.Timestamp.now()
    };
    
    console.log(`  - Actualizando auditor: ${updates.auditorName}`);
    
    if (!dryRun) {
      await db.collection('auditors').doc(doc.id).update(updates);
    }
    
    updated++;
  }
  
  console.log(`  ✓ Actualizados ${updated} perfiles de auditor`);
}

async function updateRegistersStructure(dryRun) {
  const registers = await db.collection('registers').get();
  let updated = 0;
  
  for (const doc of registers.docs) {
    const data = doc.data();
    
    const updates = {
      registerId: doc.id,
      status: mapValidationStatus(data.validation_status),
      evidenceType: data.evidenceType || 'document',
      submissionDate: data.upload_timestamp ? 
        admin.firestore.Timestamp.fromDate(new Date(data.upload_timestamp)) : 
        admin.firestore.Timestamp.now(),
      updatedAt: admin.firestore.Timestamp.now()
    };
    
    if (data.validation_timestamp) {
      updates.reviewDate = admin.firestore.Timestamp.fromDate(new Date(data.validation_timestamp));
    }
    
    if (data.validation_status === 'validated') {
      updates.approvalDate = updates.reviewDate || admin.firestore.Timestamp.now();
    }
    
    if (data.auditor_comments) {
      updates.reviewComments = data.auditor_comments;
    }
    
    console.log(`  - Actualizando registro: ${doc.id} (${updates.status})`);
    
    if (!dryRun) {
      await db.collection('registers').doc(doc.id).update(updates);
    }
    
    updated++;
  }
  
  console.log(`  ✓ Actualizados ${updated} registros`);
}

function mapValidationStatus(oldStatus) {
  const statusMap = {
    'validated': 'approved',
    'rejected': 'rejected',
    'pending': 'submitted',
    'under_review': 'under_review'
  };
  
  return statusMap[oldStatus] || 'draft';
}

async function updateStandardsStructure(dryRun) {
  const standards = await db.collection('standards').get();
  let updated = 0;
  
  for (const doc of standards.docs) {
    const data = doc.data();
    
    const updates = {
      standardId: doc.id,
      category: data.category || 'quality',
      requirementLevel: data.requirementLevel || 'mandatory',
      applicableRoles: data.applicableRoles || ['business_owner'],
      evidenceTypes: data.evidenceTypes || ['documento'],
      points: data.points || 10,
      maxPoints: data.maxPoints || data.points || 10,
      version: data.version || '1.0',
      effectiveDate: data.effectiveDate || admin.firestore.Timestamp.now(),
      isActive: data.isActive !== undefined ? data.isActive : true,
      updatedAt: admin.firestore.Timestamp.now()
    };
    
    console.log(`  - Actualizando estándar: ${data.standardCode || doc.id}`);
    
    if (!dryRun) {
      await db.collection('standards').doc(doc.id).update(updates);
    }
    
    updated++;
  }
  
  console.log(`  ✓ Actualizados ${updated} estándares`);
}

async function updateResourcesStructure(dryRun) {
  const resources = await db.collection('resources').get();
  let updated = 0;
  
  for (const doc of resources.docs) {
    const data = doc.data();
    
    const updates = {
      resourceId: doc.id,
      type: data.type || 'guide',
      category: data.category || 'general',
      targetRoles: data.targetRoles || ['business_owner'],
      language: data.language || 'es',
      downloadCount: data.downloadCount || 0,
      isPublic: data.isPublic !== undefined ? data.isPublic : false,
      version: data.version || '1.0',
      publishDate: data.publishDate || admin.firestore.Timestamp.now(),
      lastUpdate: data.lastUpdate || admin.firestore.Timestamp.now(),
      createdBy: data.createdBy || 'system',
      updatedAt: admin.firestore.Timestamp.now()
    };
    
    console.log(`  - Actualizando recurso: ${data.title || doc.id}`);
    
    if (!dryRun) {
      await db.collection('resources').doc(doc.id).update(updates);
    }
    
    updated++;
  }
  
  console.log(`  ✓ Actualizados ${updated} recursos`);
}

// Ejecutar migración
migrateData().catch(console.error);
EOF
    
    success "Script de migración creado: migration-script.js"
}

# Instalar dependencias de Node.js
install_dependencies() {
    log "Instalando dependencias de Node.js..."
    
    if [[ ! -f package.json ]]; then
        npm init -y
    fi
    
    npm install firebase-admin
    
    success "Dependencias instaladas"
}

# Ejecutar migración
run_migration() {
    log "Ejecutando migración de datos..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        warning "Ejecutando en modo DRY_RUN - No se realizarán cambios"
    else
        warning "Ejecutando migración REAL - Se modificará la base de datos"
        read -p "¿Estás seguro de continuar? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Migración cancelada"
            exit 0
        fi
    fi
    
    export PROJECT_ID="$PROJECT_ID"
    export DRY_RUN="$DRY_RUN"
    
    node migration-script.js
    
    success "Migración completada"
}

# Verificar resultados
verify_migration() {
    log "Verificando resultados de la migración..."
    
    # Verificar collections
    gcloud firestore indexes list --database="$DATABASE_NAME" --format="table(name,state)" || true
    
    success "Verificación completada"
}

# Cleanup
cleanup() {
    log "Limpiando archivos temporales..."
    rm -f migration-script.js package.json package-lock.json
    rm -rf node_modules
    success "Cleanup completado"
}

# Función principal
main() {
    log "🚀 Iniciando migración de esquema de base de datos"
    log "Proyecto: $PROJECT_ID"
    log "Base de datos: $DATABASE_NAME"
    log "Ambiente: $ENVIRONMENT"
    log "Dry Run: $DRY_RUN"
    
    check_dependencies
    check_configuration
    create_migration_script
    install_dependencies
    run_migration
    verify_migration
    cleanup
    
    success "🎉 Migración de esquema completada exitosamente"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        warning "Recuerda ejecutar con DRY_RUN=false para aplicar los cambios reales"
    fi
}

# Manejar señales
trap cleanup EXIT

# Ejecutar si es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
