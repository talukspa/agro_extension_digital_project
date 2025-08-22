# 🗄️ Esquema de Base de Datos Actualizado - CiruelaCertificada

**Proyecto**: agro-extension-digital-npe  
**Base de datos**: agro-extension-db  
**Versión**: 2.0 - Optimizada para AuthN/AuthZ  
**Fecha**: 2025-08-19

## 📋 Resumen de Colecciones

Total de colecciones: **8** (6 existentes + 2 nuevas)

1. **`users`** - Sistema de autenticación y roles *(NUEVA)*
2. **`business_profiles`** - Perfiles de empresas *(ACTUALIZADA)*
3. **`auditors`** - Información de auditores *(ACTUALIZADA)*
4. **`standards`** - Estándares de certificación *(ACTUALIZADA)*
5. **`registers`** - Registros de evidencias *(ACTUALIZADA)*
6. **`resources`** - Recursos del sistema *(ACTUALIZADA)*
7. **`audits`** - Proceso de auditorías *(NUEVA)*
8. **`standard_responses`** - Respuestas estándar *(ACTUALIZADA)*

---

## 🔐 Colección: `users` *(NUEVA)*

**Propósito**: Gestión centralizada de usuarios, autenticación y autorización

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `uid` | string | ✅ | UID de Firebase Auth (ID del documento) |
| `email` | string | ✅ | Email del usuario |
| `displayName` | string | ✅ | Nombre para mostrar |
| `role` | string | ✅ | Rol: 'admin', 'auditor', 'business_owner' |
| `isActive` | boolean | ✅ | Estado del usuario |
| `businessProfileId` | string | ❌ | ID del perfil de empresa (solo business_owner) |
| `auditorProfileId` | string | ❌ | ID del perfil de auditor (solo auditor) |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |
| `lastLoginAt` | timestamp | ❌ | Último inicio de sesión |
| `permissions` | array | ❌ | Permisos específicos adicionales |
| `metadata` | map | ❌ | Información adicional del usuario |

### Documento de Ejemplo

```json
{
  "uid": "firebase_auth_uid_123",
  "email": "empresa@ciruelacertificada.cl",
  "displayName": "Juan Pérez",
  "role": "business_owner",
  "isActive": true,
  "businessProfileId": "profile_empresa_001",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-08-19T14:20:00Z",
  "lastLoginAt": "2024-08-19T14:20:00Z",
  "permissions": ["view:own_audit_results", "submit:evidence"],
  "metadata": {
    "registrationSource": "manual",
    "preferredLanguage": "es"
  }
}
```

---

## 🏢 Colección: `business_profiles` *(ACTUALIZADA)*

**Propósito**: Información detallada de empresas certificadoras

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `businessProfileId` | string | ✅ | ID único del perfil (ID del documento) |
| `uid` | string | ✅ | UID del usuario propietario |
| `companyName` | string | ✅ | Nombre de la empresa |
| `businessRut` | string | ✅ | RUT de la empresa |
| `contactName` | string | ✅ | Nombre del contacto principal |
| `contactEmail` | string | ✅ | Email de contacto |
| `contactPhone` | string | ✅ | Teléfono de contacto |
| `address` | map | ✅ | Dirección completa |
| `certificationLevel` | string | ❌ | Nivel de certificación actual |
| `certificationYear` | number | ❌ | Año de certificación |
| `certificationStatus` | string | ✅ | Estado: 'pending', 'in_progress', 'certified', 'expired' |
| `assignedAuditorId` | string | ❌ | ID del auditor asignado |
| `productionVolume` | number | ❌ | Volumen de producción anual |
| `productTypes` | array | ❌ | Tipos de productos |
| `facilitiesCount` | number | ❌ | Número de instalaciones |
| `employeesCount` | number | ❌ | Número de empleados |
| `isActive` | boolean | ✅ | Estado del perfil |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |
| `tags` | array | ❌ | Etiquetas para clasificación |

### Documento de Ejemplo

```json
{
  "businessProfileId": "profile_empresa_001",
  "uid": "firebase_auth_uid_123",
  "companyName": "Frutas del Valle SpA",
  "businessRut": "76.543.210-5",
  "contactName": "Juan Pérez González",
  "contactEmail": "contacto@frutasdelvalle.cl",
  "contactPhone": "+56 9 8765 4321",
  "address": {
    "street": "Camino Rural 1234",
    "city": "Curicó",
    "region": "Región del Maule",
    "postalCode": "3340000",
    "country": "Chile"
  },
  "certificationLevel": "Premium",
  "certificationYear": 2024,
  "certificationStatus": "in_progress",
  "assignedAuditorId": "auditor_002",
  "productionVolume": 50000,
  "productTypes": ["ciruela_deshidratada", "ciruela_fresca"],
  "facilitiesCount": 3,
  "employeesCount": 45,
  "isActive": true,
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-08-19T14:20:00Z",
  "tags": ["exportador", "organico", "premium"]
}
```

---

## 👨‍💼 Colección: `auditors` *(ACTUALIZADA)*

**Propósito**: Información de auditores certificados

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `auditorId` | string | ✅ | ID único del auditor (ID del documento) |
| `uid` | string | ✅ | UID del usuario auditor |
| `auditorName` | string | ✅ | Nombre completo del auditor |
| `auditorEmail` | string | ✅ | Email del auditor |
| `auditorPhone` | string | ✅ | Teléfono del auditor |
| `certificationNumber` | string | ✅ | Número de certificación profesional |
| `certificationLevel` | string | ✅ | Nivel: 'junior', 'senior', 'lead', 'principal' |
| `specializations` | array | ✅ | Especializaciones del auditor |
| `assignedBusinesses` | array | ❌ | IDs de empresas asignadas |
| `maxConcurrentAudits` | number | ✅ | Máximo de auditorías simultáneas |
| `currentAuditsCount` | number | ✅ | Auditorías actuales en progreso |
| `completedAuditsCount` | number | ✅ | Total de auditorías completadas |
| `averageRating` | number | ❌ | Calificación promedio |
| `languages` | array | ✅ | Idiomas que maneja |
| `availableRegions` | array | ✅ | Regiones donde puede auditar |
| `isActive` | boolean | ✅ | Estado del auditor |
| `hireDateAt` | timestamp | ✅ | Fecha de contratación |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |

### Documento de Ejemplo

```json
{
  "auditorId": "auditor_002",
  "uid": "firebase_auth_uid_456",
  "auditorName": "María Silva Contreras",
  "auditorEmail": "maria.silva@ciruelacertificada.cl",
  "auditorPhone": "+56 9 1234 5678",
  "certificationNumber": "CERT-2023-045",
  "certificationLevel": "senior",
  "specializations": ["agricultura_organica", "procesamiento_alimentos", "trazabilidad"],
  "assignedBusinesses": ["profile_empresa_001", "profile_empresa_003"],
  "maxConcurrentAudits": 5,
  "currentAuditsCount": 2,
  "completedAuditsCount": 47,
  "averageRating": 4.8,
  "languages": ["es", "en"],
  "availableRegions": ["Region_del_Maule", "Region_de_OHiggins", "Region_Metropolitana"],
  "isActive": true,
  "hireDateAt": "2023-03-15T09:00:00Z",
  "createdAt": "2023-03-15T09:00:00Z",
  "updatedAt": "2024-08-19T14:20:00Z"
}
```

---

## 📋 Colección: `standards` *(ACTUALIZADA)*

**Propósito**: Estándares de certificación del sistema

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `standardId` | string | ✅ | ID único del estándar (ID del documento) |
| `standardCode` | string | ✅ | Código del estándar (ej: A001, B015) |
| `title` | string | ✅ | Título del estándar |
| `description` | string | ✅ | Descripción detallada |
| `category` | string | ✅ | Categoría: 'quality', 'safety', 'environment', 'social' |
| `subcategory` | string | ❌ | Subcategoría específica |
| `requirementLevel` | string | ✅ | Nivel: 'mandatory', 'recommended', 'optional' |
| `applicableRoles` | array | ✅ | Roles que deben cumplir el estándar |
| `evidenceTypes` | array | ✅ | Tipos de evidencia requeridos |
| `validationCriteria` | map | ✅ | Criterios de validación |
| `points` | number | ✅ | Puntaje asignado |
| `maxPoints` | number | ✅ | Puntaje máximo posible |
| `version` | string | ✅ | Versión del estándar |
| `effectiveDate` | timestamp | ✅ | Fecha de vigencia |
| `expirationDate` | timestamp | ❌ | Fecha de vencimiento |
| `isActive` | boolean | ✅ | Estado del estándar |
| `relatedStandards` | array | ❌ | Estándares relacionados |
| `resources` | array | ❌ | Recursos asociados |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |

### Documento de Ejemplo

```json
{
  "standardId": "std_A001",
  "standardCode": "A001",
  "title": "Control de Calidad en Recepción de Materia Prima",
  "description": "Estándar para asegurar la calidad de las ciruelas recibidas antes del procesamiento",
  "category": "quality",
  "subcategory": "materia_prima",
  "requirementLevel": "mandatory",
  "applicableRoles": ["business_owner"],
  "evidenceTypes": ["documento", "fotografia", "registro_control"],
  "validationCriteria": {
    "documentationRequired": true,
    "photosRequired": true,
    "minSampleSize": 10,
    "qualityThreshold": 95
  },
  "points": 15,
  "maxPoints": 15,
  "version": "2.1",
  "effectiveDate": "2024-01-01T00:00:00Z",
  "isActive": true,
  "relatedStandards": ["std_A002", "std_A015"],
  "resources": ["resource_001", "resource_023"],
  "createdAt": "2023-11-15T10:00:00Z",
  "updatedAt": "2024-06-01T15:30:00Z"
}
```

---

## 📄 Colección: `registers` *(ACTUALIZADA)*

**Propósito**: Registros de evidencias de cumplimiento

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `registerId` | string | ✅ | ID único del registro (ID del documento) |
| `businessProfileId` | string | ✅ | ID de la empresa |
| `standardId` | string | ✅ | ID del estándar |
| `uid` | string | ✅ | UID del usuario que subió |
| `status` | string | ✅ | Estado: 'draft', 'submitted', 'under_review', 'approved', 'rejected' |
| `evidenceType` | string | ✅ | Tipo: 'document', 'photo', 'video', 'form_data' |
| `title` | string | ✅ | Título descriptivo |
| `description` | string | ❌ | Descripción de la evidencia |
| `files` | array | ❌ | URLs de archivos subidos |
| `formData` | map | ❌ | Datos de formulario estructurados |
| `metadata` | map | ❌ | Metadatos adicionales |
| `submissionDate` | timestamp | ✅ | Fecha de envío |
| `reviewDate` | timestamp | ❌ | Fecha de revisión |
| `approvalDate` | timestamp | ❌ | Fecha de aprobación |
| `reviewedBy` | string | ❌ | UID del auditor que revisó |
| `reviewComments` | string | ❌ | Comentarios del auditor |
| `score` | number | ❌ | Puntaje asignado |
| `maxScore` | number | ❌ | Puntaje máximo posible |
| `auditId` | string | ❌ | ID de la auditoría asociada |
| `tags` | array | ❌ | Etiquetas para clasificación |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |

### Documento de Ejemplo

```json
{
  "registerId": "reg_001_A001_2024",
  "businessProfileId": "profile_empresa_001",
  "standardId": "std_A001",
  "uid": "firebase_auth_uid_123",
  "status": "approved",
  "evidenceType": "document",
  "title": "Control de Calidad - Lote C-2024-045",
  "description": "Registro de control de calidad para lote de ciruelas recibidas el 15/08/2024",
  "files": [
    "gs://bucket/evidence/reg_001_A001_2024_doc1.pdf",
    "gs://bucket/evidence/reg_001_A001_2024_photo1.jpg"
  ],
  "formData": {
    "loteNumber": "C-2024-045",
    "receivedQuantity": 1500,
    "qualityGrade": "Premium",
    "moistureContent": 18.5,
    "defectPercentage": 2.1
  },
  "metadata": {
    "supplier": "Huerto Las Palmas",
    "harvestDate": "2024-08-10"
  },
  "submissionDate": "2024-08-15T14:30:00Z",
  "reviewDate": "2024-08-17T10:15:00Z",
  "approvalDate": "2024-08-17T16:45:00Z",
  "reviewedBy": "firebase_auth_uid_456",
  "reviewComments": "Documentación completa y conforme a estándares",
  "score": 15,
  "maxScore": 15,
  "auditId": "audit_2024_001",
  "tags": ["calidad", "recepcion", "lote_premium"],
  "createdAt": "2024-08-15T14:30:00Z",
  "updatedAt": "2024-08-17T16:45:00Z"
}
```

---

## 📚 Colección: `resources` *(ACTUALIZADA)*

**Propósito**: Recursos y documentación del sistema

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `resourceId` | string | ✅ | ID único del recurso (ID del documento) |
| `resourceCode` | string | ✅ | Código del recurso |
| `title` | string | ✅ | Título del recurso |
| `description` | string | ✅ | Descripción del recurso |
| `type` | string | ✅ | Tipo: 'guide', 'template', 'video', 'document', 'checklist' |
| `category` | string | ✅ | Categoría del recurso |
| `relatedStandards` | array | ❌ | Estándares relacionados |
| `targetRoles` | array | ✅ | Roles objetivo |
| `language` | string | ✅ | Idioma del recurso |
| `fileUrl` | string | ❌ | URL del archivo |
| `fileSize` | number | ❌ | Tamaño del archivo en bytes |
| `fileType` | string | ❌ | Tipo de archivo |
| `thumbnailUrl` | string | ❌ | URL de imagen miniatura |
| `downloadCount` | number | ✅ | Número de descargas |
| `rating` | number | ❌ | Calificación promedio |
| `ratingCount` | number | ❌ | Número de calificaciones |
| `tags` | array | ❌ | Etiquetas para búsqueda |
| `isPublic` | boolean | ✅ | Acceso público o restringido |
| `version` | string | ✅ | Versión del recurso |
| `publishDate` | timestamp | ✅ | Fecha de publicación |
| `lastUpdate` | timestamp | ✅ | Última actualización del contenido |
| `createdBy` | string | ✅ | UID del creador |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |

### Documento de Ejemplo

```json
{
  "resourceId": "resource_001",
  "resourceCode": "GUIDE-A001",
  "title": "Guía de Control de Calidad en Recepción",
  "description": "Guía detallada para implementar controles de calidad efectivos en la recepción de materia prima",
  "type": "guide",
  "category": "quality_control",
  "relatedStandards": ["std_A001", "std_A002"],
  "targetRoles": ["business_owner", "auditor"],
  "language": "es",
  "fileUrl": "gs://bucket/resources/guide_control_calidad_recepcion_v2.1.pdf",
  "fileSize": 2457600,
  "fileType": "application/pdf",
  "thumbnailUrl": "gs://bucket/thumbnails/guide_001_thumb.jpg",
  "downloadCount": 127,
  "rating": 4.6,
  "ratingCount": 23,
  "tags": ["calidad", "recepcion", "materia_prima", "ciruelas"],
  "isPublic": false,
  "version": "2.1",
  "publishDate": "2024-01-15T00:00:00Z",
  "lastUpdate": "2024-06-01T10:00:00Z",
  "createdBy": "admin_uid_001",
  "createdAt": "2024-01-10T09:00:00Z",
  "updatedAt": "2024-06-01T10:00:00Z"
}
```

---

## 🔍 Colección: `audits` *(NUEVA)*

**Propósito**: Gestión del proceso de auditorías

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `auditId` | string | ✅ | ID único de la auditoría (ID del documento) |
| `businessProfileId` | string | ✅ | ID de la empresa auditada |
| `auditorId` | string | ✅ | ID del auditor asignado |
| `auditType` | string | ✅ | Tipo: 'initial', 'follow_up', 'surveillance', 'renewal' |
| `status` | string | ✅ | Estado: 'scheduled', 'in_progress', 'completed', 'cancelled' |
| `scheduledDate` | timestamp | ✅ | Fecha programada |
| `startDate` | timestamp | ❌ | Fecha de inicio real |
| `endDate` | timestamp | ❌ | Fecha de finalización |
| `scope` | array | ✅ | Alcance de la auditoría |
| `standardsToAudit` | array | ✅ | Estándares a auditar |
| `location` | map | ✅ | Ubicación de la auditoría |
| `findings` | array | ❌ | Hallazgos de la auditoría |
| `nonConformities` | array | ❌ | No conformidades encontradas |
| `recommendations` | array | ❌ | Recomendaciones del auditor |
| `totalScore` | number | ❌ | Puntaje total obtenido |
| `maxScore` | number | ❌ | Puntaje máximo posible |
| `certificationRecommendation` | string | ❌ | Recomendación: 'approve', 'conditional', 'reject' |
| `reportId` | string | ❌ | ID del reporte final |
| `followUpRequired` | boolean | ✅ | Requiere seguimiento |
| `followUpDate` | timestamp | ❌ | Fecha de seguimiento |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |

### Documento de Ejemplo

```json
{
  "auditId": "audit_2024_001",
  "businessProfileId": "profile_empresa_001",
  "auditorId": "auditor_002",
  "auditType": "initial",
  "status": "completed",
  "scheduledDate": "2024-08-20T09:00:00Z",
  "startDate": "2024-08-20T09:15:00Z",
  "endDate": "2024-08-20T16:30:00Z",
  "scope": ["production_facility", "storage_area", "quality_lab"],
  "standardsToAudit": ["std_A001", "std_A002", "std_B015"],
  "location": {
    "address": "Camino Rural 1234, Curicó",
    "coordinates": {
      "lat": -34.983333,
      "lng": -71.233333
    }
  },
  "findings": [
    {
      "standardId": "std_A001",
      "finding": "Excelente implementación de controles de calidad",
      "type": "positive"
    }
  ],
  "nonConformities": [],
  "recommendations": [
    "Implementar sistema digital de trazabilidad",
    "Mejorar ventilación en área de secado"
  ],
  "totalScore": 87,
  "maxScore": 90,
  "certificationRecommendation": "approve",
  "reportId": "report_audit_2024_001",
  "followUpRequired": false,
  "createdAt": "2024-08-15T10:00:00Z",
  "updatedAt": "2024-08-20T17:00:00Z"
}
```

---

## 📊 Colección: `standard_responses` *(ACTUALIZADA)*

**Propósito**: Respuestas estándar para auditores

### Estructura de Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `responseId` | string | ✅ | ID único de la respuesta (ID del documento) |
| `category` | string | ✅ | Categoría de la respuesta |
| `subcategory` | string | ❌ | Subcategoría específica |
| `responseText` | string | ✅ | Texto de la respuesta |
| `severity` | string | ✅ | Severidad: 'info', 'minor', 'major', 'critical' |
| `applicableStandards` | array | ❌ | Estándares aplicables |
| `tags` | array | ❌ | Etiquetas para búsqueda |
| `language` | string | ✅ | Idioma de la respuesta |
| `usageCount` | number | ✅ | Número de veces utilizada |
| `isActive` | boolean | ✅ | Estado de la respuesta |
| `createdBy` | string | ✅ | UID del creador |
| `approvedBy` | string | ❌ | UID del aprobador |
| `version` | string | ✅ | Versión de la respuesta |
| `createdAt` | timestamp | ✅ | Fecha de creación |
| `updatedAt` | timestamp | ✅ | Última actualización |

### Documento de Ejemplo

```json
{
  "responseId": "response_001",
  "category": "quality_control",
  "subcategory": "documentation",
  "responseText": "La documentación de control de calidad está completa y conforme a los estándares establecidos. Se evidencia un sistema robusto de trazabilidad.",
  "severity": "info",
  "applicableStandards": ["std_A001", "std_A002"],
  "tags": ["calidad", "documentacion", "trazabilidad", "conforme"],
  "language": "es",
  "usageCount": 45,
  "isActive": true,
  "createdBy": "admin_uid_001",
  "approvedBy": "admin_uid_002",
  "version": "1.0",
  "createdAt": "2024-01-10T09:00:00Z",
  "updatedAt": "2024-01-10T09:00:00Z"
}
```

---

## 🔗 Relaciones Entre Colecciones

### Diagrama de Relaciones

```
users (1) ←→ (1) business_profiles
users (1) ←→ (1) auditors
business_profiles (1) ←→ (n) registers
business_profiles (1) ←→ (n) audits
auditors (1) ←→ (n) audits
standards (1) ←→ (n) registers
standards (n) ←→ (n) resources
audits (1) ←→ (n) registers
auditors (n) ←→ (n) standard_responses
```

### Campos de Referencia

| Colección Origen | Campo | Colección Destino | Propósito |
|-----------------|-------|-------------------|-----------|
| `users` | `businessProfileId` | `business_profiles` | Enlazar usuario con empresa |
| `users` | `auditorProfileId` | `auditors` | Enlazar usuario con auditor |
| `business_profiles` | `uid` | `users` | Propietario del perfil |
| `business_profiles` | `assignedAuditorId` | `auditors` | Auditor asignado |
| `auditors` | `uid` | `users` | Usuario auditor |
| `registers` | `businessProfileId` | `business_profiles` | Empresa del registro |
| `registers` | `standardId` | `standards` | Estándar evaluado |
| `registers` | `auditId` | `audits` | Auditoría asociada |
| `audits` | `businessProfileId` | `business_profiles` | Empresa auditada |
| `audits` | `auditorId` | `auditors` | Auditor asignado |

---

## 📋 Scripts de Migración

### Script de Actualización de Datos

```javascript
// Script para migrar datos existentes al nuevo esquema
// Ejecutar en Firebase Functions o Admin SDK

const admin = require('firebase-admin');
const db = admin.firestore();

async function migrateExistingData() {
  // 1. Crear colección users basada en business_profiles existentes
  const businessProfiles = await db.collection('business_profiles').get();
  
  for (const doc of businessProfiles.docs) {
    const data = doc.data();
    
    // Crear usuario para cada business_profile
    const userData = {
      uid: `migrated_${doc.id}`,
      email: data.contactEmail || `${doc.id}@temp.com`,
      displayName: data.contactName || data.companyName,
      role: 'business_owner',
      isActive: true,
      businessProfileId: doc.id,
      createdAt: data.createdAt || new Date(),
      updatedAt: new Date()
    };
    
    await db.collection('users').doc(userData.uid).set(userData);
    
    // Actualizar business_profile con uid
    await db.collection('business_profiles').doc(doc.id).update({
      uid: userData.uid,
      updatedAt: new Date()
    });
  }
  
  // 2. Migrar auditores
  const auditorsSnapshot = await db.collection('auditors').get();
  
  for (const doc of auditorsSnapshot.docs) {
    const data = doc.data();
    
    // Crear usuario para cada auditor
    const userData = {
      uid: `migrated_auditor_${doc.id}`,
      email: data.auditor_email,
      displayName: data.auditor_name,
      role: 'auditor',
      isActive: true,
      auditorProfileId: doc.id,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    await db.collection('users').doc(userData.uid).set(userData);
    
    // Actualizar estructura del auditor
    await db.collection('auditors').doc(doc.id).update({
      uid: userData.uid,
      auditorId: doc.id,
      auditorName: data.auditor_name,
      auditorEmail: data.auditor_email,
      auditorPhone: data.auditor_phone,
      certificationLevel: 'senior', // valor por defecto
      isActive: true,
      updatedAt: new Date()
    });
  }
  
  // 3. Actualizar registers con nuevos campos
  const registersSnapshot = await db.collection('registers').get();
  
  for (const doc of registersSnapshot.docs) {
    const data = doc.data();
    
    await db.collection('registers').doc(doc.id).update({
      registerId: doc.id,
      status: data.validation_status === 'validated' ? 'approved' : 'rejected',
      submissionDate: data.upload_timestamp ? new Date(data.upload_timestamp) : new Date(),
      reviewDate: data.validation_timestamp ? new Date(data.validation_timestamp) : null,
      updatedAt: new Date()
    });
  }
  
  console.log('Migración completada');
}
```

## 🚀 Próximos Pasos

1. **Ejecutar migración de datos**: Usar el script anterior para actualizar esquemas
2. **Actualizar índices**: Crear índices optimizados en Firestore
3. **Implementar validaciones**: Agregar reglas de validación en el frontend
4. **Testing**: Probar todas las funcionalidades con el nuevo esquema
5. **Deploy**: Aplicar cambios en producción

---

## 📞 Notas de Implementación

- Todos los campos de fecha usan `timestamp` de Firestore
- Los IDs de documento siguen convenciones consistentes
- Se mantiene retrocompatibilidad donde es posible
- Las reglas de seguridad están alineadas con este esquema
- Campos opcionales permiten migración gradual
