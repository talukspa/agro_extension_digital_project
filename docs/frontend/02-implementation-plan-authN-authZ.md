# Plan de Implementación Detallado: Autenticación y Autorización en Next.js

## Resumen Ejecutivo

Este documento describe un plan detallado para implementar la autenticación (AuthN) y autorización (AuthZ) en el frontend de Next.js siguiendo la arquitectura Firebase Auth + Firestore descrita en `01-authN-authZ.md`.

## Estado Actual del Proyecto

### ✅ Componentes Ya Configurados
- Firebase configurado parcialmente en `/frontend/src/lib/firebase/`
- Next.js 15.4.6 con App Router
- TypeScript configurado
- Dependencias básicas de Firebase instaladas

### 🔄 Componentes Pendientes
- Context de autenticación
- Middleware de autorización
- Páginas de login/registro
- Protección de rutas
- Integración con Firestore para roles

## Fases de Implementación

### Fase 1: Configuración Manual (Firebase Console) 🔧
**Duración estimada: 2-3 horas**

#### 1.1 Configuración de Firebase Authentication
- [ ] Acceder a Firebase Console del proyecto `agro-extension-digital-npe`
- [ ] Habilitar Authentication
- [ ] Configurar proveedores de autenticación:
  - [ ] Email/Password
  - [ ] Google Sign-In
  - [ ] (Opcional) Otros proveedores según necesidades

#### 1.2 Configuración de Firestore
- [ ] Verificar base de datos `agro-extension-db` existente
- [ ] Actualizar colecciones existentes para autenticación:

**Actualizar `business_profiles` collection:**
```javascript
// Document ID: Business RUT (e.g., "76.432.187-4")
{
  "rut": "76.432.187-4",
  "firebase_uid": "firebase-user-id", // AÑADIR ESTE CAMPO
  "legal_name": "Exportadora de Ciruelas Paine",
  "owner_name": "Juan Rojas",
  "owner_email": "contacto@exportadorapaine.cl",
  "owner_phone": "+56987654321",
  "role": "business_owner", // AÑADIR ESTE CAMPO
  "commune": "Paine",
  "region": "Metropolitana",
  "address": "Av. Gral. Baquedano 108",
  "business_size": "Microempresa",
  "process_type": "Producción Primaria",
  "digital_tools_used_at_work": ["WhatsApp", "Facebook"],
  "digital_tools_experienced": ["WhatsApp", "Facebook"],
  "auth_setup_date": "timestamp", // AÑADIR ESTE CAMPO
  "last_login": "timestamp" // AÑADIR ESTE CAMPO
}
```

**Actualizar `auditors` collection:**
```javascript
// Document ID: Auditor ID (e.g., "1", "2")
{
  "auditor_id": 1,
  "firebase_uid": "firebase-auditor-uid", // AÑADIR ESTE CAMPO
  "auditor_name": "Carlos Ruiz",
  "auditor_email": "carlos.ruiz@auditcorp.com",
  "role": "auditor", // AÑADIR ESTE CAMPO
  "assigned_businesses": ["76.432.187-4"], // AÑADIR ESTE CAMPO
  "auth_setup_date": "timestamp", // AÑADIR ESTE CAMPO
  "last_login": "timestamp" // AÑADIR ESTE CAMPO
}
```

**Crear nueva `admin_users` collection:**
```javascript
// Document ID: Admin ID (e.g., "admin-1")
{
  "admin_id": "admin-1",
  "firebase_uid": "firebase-admin-uid",
  "admin_name": "System Administrator",
  "admin_email": "admin@agroextension.com",
  "role": "admin",
  "permissions": [
    "manage_users",
    "manage_standards", 
    "view_all_responses",
    "manage_auditors",
    "generate_reports"
  ],
  "auth_setup_date": "timestamp",
  "last_login": "timestamp"
}
```

#### 1.3 Configuración de Service Account
- [ ] Generar clave de service account en Firebase Console
- [ ] Almacenar credenciales en Google Secret Manager
- [ ] Configurar variables de entorno para Cloud Run

### Fase 2: Implementación del Cliente (Frontend) 🎯
**Duración estimada: 1-2 días**

#### 2.1 Configuración de Firebase Cliente
- [ ] Verificar configuración en `/src/lib/firebase/config.ts`
- [ ] Actualizar si es necesario con las credenciales correctas

#### 2.2 Context de Autenticación
- [ ] Crear `/src/contexts/AuthContext.tsx`:
```typescript
interface AuthContextType {
  user: User | null;
  userRole: 'business_owner' | 'auditor' | 'admin' | null;
  userData: BusinessProfile | Auditor | AdminUser | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, userType: 'business' | 'auditor') => Promise<void>;
  signOut: () => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  linkBusinessProfile: (businessRut: string) => Promise<void>;
  linkAuditorProfile: (auditorId: number) => Promise<void>;
}

// Tipos específicos del sistema agrícola
interface BusinessProfile {
  rut: string;
  firebase_uid: string;
  legal_name: string;
  owner_name: string;
  owner_email: string;
  role: 'business_owner';
  process_type: 'Producción Primaria' | 'Procesamiento Agroindustrial';
  business_size: 'Microempresa' | 'Pequeña empresa' | 'Mediana empresa' | 'Gran empresa';
  commune: string;
  region: string;
}

interface Auditor {
  auditor_id: number;
  firebase_uid: string;
  auditor_name: string;
  auditor_email: string;
  role: 'auditor';
  assigned_businesses: string[];
}

interface AdminUser {
  admin_id: string;
  firebase_uid: string;
  admin_name: string;
  admin_email: string;
  role: 'admin';
  permissions: string[];
}
```

#### 2.3 Componentes de UI
- [ ] Crear `/src/components/auth/LoginForm.tsx`
- [ ] Crear `/src/components/auth/RegisterForm.tsx`
- [ ] Crear `/src/components/auth/AuthGuard.tsx`
- [ ] Crear `/src/components/auth/RoleGuard.tsx`

#### 2.4 Páginas de Autenticación
- [ ] Crear `/src/app/auth/login/page.tsx`
- [ ] Crear `/src/app/auth/register/page.tsx` (con formularios específicos para business/auditor)
- [ ] Crear `/src/app/auth/link-profile/page.tsx` (para vincular Firebase con perfiles existentes)
- [ ] Crear `/src/app/auth/profile/page.tsx`

#### 2.5 Hook personalizado
- [ ] Crear `/src/hooks/useAuth.ts` para acceso fácil al contexto

### Fase 3: Implementación del Servidor (Backend) ⚙️
**Duración estimada: 1-2 días**

#### 3.1 Firebase Admin SDK
- [ ] Actualizar `/src/lib/firebase/server.ts` para incluir:
  - Inicialización del Admin SDK
  - Función de verificación de tokens
  - Funciones de gestión de usuarios en Firestore

#### 3.2 Middleware de Autorización
- [ ] Crear `/src/middleware.ts` con:
  - Verificación de tokens ID
  - Consulta de roles en Firestore
  - Control de acceso basado en rutas
  - Headers personalizados para API routes

#### 3.3 API Routes Protegidas
- [ ] Crear estructura de rutas específicas para el sistema agrícola:
```
/src/app/api/
├── auth/
│   ├── register/route.ts
│   ├── link-business-profile/route.ts
│   ├── link-auditor-profile/route.ts
│   └── profile/route.ts
├── admin/
│   ├── users/route.ts
│   ├── business-profiles/route.ts
│   ├── auditors/route.ts
│   ├── standards/route.ts
│   └── analytics/route.ts
├── business/
│   ├── profile/route.ts
│   ├── responses/route.ts
│   ├── standards/route.ts
│   └── reports/route.ts
├── audit/
│   ├── assigned-businesses/route.ts
│   ├── responses/route.ts
│   ├── reviews/route.ts
│   └── validation/route.ts
├── standards/
│   ├── templates/route.ts
│   └── [templateName]/route.ts
└── responses/
    ├── [responseId]/route.ts
    └── by-business/[businessRut]/route.ts
```

#### 3.4 Utilidades del Servidor
- [ ] Crear `/src/utils/auth-server.ts`:
  - Funciones de verificación de roles
  - Helpers para extraer información del usuario
  - Funciones de logging de seguridad

### Fase 4: Protección de Rutas y UX 🛡️
**Duración estimada: 1 día**

#### 4.1 Protección de Páginas
- [ ] Implementar `AuthGuard` en páginas que requieren autenticación
- [ ] Implementar `RoleGuard` para páginas específicas por rol
- [ ] Configurar redirecciones automáticas

#### 4.2 Navegación Condicional
- [ ] Actualizar componentes de navegación para mostrar/ocultar según rol
- [ ] Implementar menús dinámicos basados en permisos

#### 4.3 Estados de Carga y Error
- [ ] Componentes de loading durante verificación de auth
- [ ] Páginas de error 401/403 personalizadas
- [ ] Feedback visual para operaciones de auth

### Fase 5: Testing y Seguridad 🧪
**Duración estimada: 1-2 días**

#### 5.1 Testing de Autenticación
- [ ] Tests unitarios para AuthContext
- [ ] Tests de integración para flujos de login/logout
- [ ] Tests E2E para protección de rutas

#### 5.2 Testing de Autorización
- [ ] Tests de middleware con diferentes roles
- [ ] Tests de API routes protegidas
- [ ] Verificación de acceso a recursos

#### 5.3 Seguridad
- [ ] Revisión de reglas de Firestore Security Rules
- [ ] Validación de tokens en todas las rutas protegidas
- [ ] Auditoría de permisos y roles

### Fase 6: Deployment y Monitoreo 🚀
**Duración estimada: 1 día**

#### 6.1 Variables de Entorno
- [ ] Configurar variables en Cloud Run:
  - `FIREBASE_PROJECT_ID`
  - `FIREBASE_CLIENT_EMAIL`
  - `FIREBASE_PRIVATE_KEY`
  - `NEXT_PUBLIC_FIREBASE_CONFIG`

#### 6.2 Deployment
- [ ] Build y deploy a Cloud Run
- [ ] Verificación en ambiente de producción
- [ ] Tests de smoke en producción

#### 6.3 Monitoreo
- [ ] Configurar logging de eventos de auth
- [ ] Alertas para intentos de acceso no autorizado
- [ ] Métricas de uso de autenticación

## Estructura de Archivos Final

```
frontend/src/
├── app/
│   ├── auth/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── link-profile/page.tsx
│   │   └── profile/page.tsx
│   ├── api/
│   │   ├── auth/
│   │   │   ├── register/route.ts
│   │   │   ├── link-business-profile/route.ts
│   │   │   └── link-auditor-profile/route.ts
│   │   ├── admin/
│   │   │   ├── users/route.ts
│   │   │   ├── business-profiles/route.ts
│   │   │   ├── auditors/route.ts
│   │   │   └── standards/route.ts
│   │   ├── business/
│   │   │   ├── profile/route.ts
│   │   │   ├── responses/route.ts
│   │   │   └── standards/route.ts
│   │   ├── audit/
│   │   │   ├── assigned-businesses/route.ts
│   │   │   ├── responses/route.ts
│   │   │   └── validation/route.ts
│   │   ├── standards/
│   │   │   └── templates/route.ts
│   │   └── responses/
│   │       └── [responseId]/route.ts
│   ├── dashboard/
│   │   ├── admin/
│   │   │   ├── page.tsx
│   │   │   ├── users/page.tsx
│   │   │   ├── standards/page.tsx
│   │   │   └── analytics/page.tsx
│   │   ├── business/
│   │   │   ├── page.tsx
│   │   │   ├── profile/page.tsx
│   │   │   ├── standards/page.tsx
│   │   │   ├── responses/page.tsx
│   │   │   └── reports/page.tsx
│   │   └── audit/
│   │       ├── page.tsx
│   │       ├── assigned-businesses/page.tsx
│   │       ├── responses/page.tsx
│   │       └── validation/page.tsx
│   └── layout.tsx (con AuthProvider)
├── components/
│   ├── auth/
│   │   ├── AuthGuard.tsx
│   │   ├── RoleGuard.tsx
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── LinkProfileForm.tsx
│   ├── business/
│   │   ├── ProfileForm.tsx
│   │   ├── StandardsView.tsx
│   │   └── ResponseForm.tsx
│   ├── audit/
│   │   ├── AssignedBusinesses.tsx
│   │   ├── ResponseValidation.tsx
│   │   └── ValidationForm.tsx
│   └── admin/
│       ├── UserManagement.tsx
│       ├── StandardsManagement.tsx
│       └── Analytics.tsx
├── contexts/
│   └── AuthContext.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useBusinessProfile.ts
│   ├── useAuditorData.ts
│   └── useStandardResponses.ts
├── lib/
│   └── firebase/
│       ├── config.ts
│       ├── server.ts
│       ├── firestore.ts
│       └── index.ts
├── types/
│   ├── auth.ts
│   ├── firestore.ts
│   └── api.ts
├── utils/
│   ├── auth-server.ts
│   ├── validation.ts
│   └── constants.ts
└── middleware.ts
```

## Roles y Permisos

### Definición de Roles del Sistema Agrícola

#### 1. Admin (Administrador del Sistema)
- **Descripción**: Acceso completo al sistema de estándares agrícolas
- **Permisos**:
  - Gestión de usuarios (business_profiles, auditors, admin_users)
  - Administración de plantillas de estándares (standards collection)
  - Acceso a todas las respuestas y auditorías
  - Generación de reportes globales
  - Configuración del sistema
  - Asignación de auditores a empresas

#### 2. Business Owner (Propietario de Empresa)
- **Descripción**: Propietario de empresa agrícola con perfil en business_profiles
- **Permisos**:
  - Ver y actualizar su propio perfil de empresa (business_profiles[rut])
  - Acceso a estándares aplicables a su tipo de proceso
  - Crear y gestionar respuestas a estándares (responses collection)
  - Ver auditorías y validaciones de sus respuestas
  - Dashboard empresarial con métricas de cumplimiento
  - Acceso solo a sus propios datos y reportes

#### 3. Auditor (Auditor Externo)
- **Descripción**: Auditor asignado para revisar respuestas de empresas específicas
- **Permisos**:
  - Ver perfiles de empresas asignadas (según assigned_businesses)
  - Acceso de solo lectura a responses de empresas asignadas
  - Validar evidencia en registers (fotos, documentos, bitácoras)
  - Crear comentarios de auditoría (auditor_comments)
  - Cambiar validation_status de registers
  - Dashboard de auditoría con empresas asignadas
  - Generar reportes de auditoría para empresas asignadas

### Matriz de Permisos por Colección

| Colección | Admin | Business Owner | Auditor |
|-----------|-------|----------------|---------|
| `business_profiles` | CRUD All | Read/Update Own | Read Assigned |
| `standards` | CRUD All | Read All | Read All |
| `responses` | Read All | CRUD Own | Read/Update Assigned |
| `auditors` | CRUD All | None | Read Own |
| `admin_users` | CRUD All | None | None |

### Reglas de Acceso Específicas

#### Business Owner
- Solo puede acceder a responses donde `business_rut` = su RUT
- Solo puede ver estándares aplicables a su `process_type`
- No puede modificar `validation_status` en registers

#### Auditor  
- Solo puede acceder a responses de empresas en su `assigned_businesses`
- Puede modificar `validation_status` y `auditor_comments` en registers
- No puede crear nuevas responses, solo revisar existentes

#### Admin
- Acceso completo a todas las colecciones
- Puede asignar/desasignar auditores a empresas
- Puede crear nuevas plantillas de estándares

## Consideraciones de Seguridad

### 1. Tokens y Sesiones
- Tokens ID de Firebase con expiración automática
- Refresh automático de tokens
- Logout automático en caso de tokens inválidos

### 2. Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Business Profiles - only own profile access for business owners
    match /business_profiles/{businessRut} {
      allow read: if request.auth != null && (
        // Admin can read all
        getUserRole(request.auth.uid) == 'admin' ||
        // Business owner can read own profile
        (getUserRole(request.auth.uid) == 'business_owner' && resource.data.firebase_uid == request.auth.uid) ||
        // Auditor can read assigned businesses
        (getUserRole(request.auth.uid) == 'auditor' && businessRut in getAuditorAssignedBusinesses(request.auth.uid))
      );
      
      allow write: if request.auth != null && (
        // Admin can write all
        getUserRole(request.auth.uid) == 'admin' ||
        // Business owner can update own profile (except firebase_uid)
        (getUserRole(request.auth.uid) == 'business_owner' && 
         resource.data.firebase_uid == request.auth.uid &&
         request.resource.data.firebase_uid == resource.data.firebase_uid)
      );
    }
    
    // Standards - read access for all authenticated users
    match /standards/{standardId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && getUserRole(request.auth.uid) == 'admin';
    }
    
    // Responses - access based on business ownership and auditor assignment
    match /responses/{responseId} {
      allow read: if request.auth != null && (
        // Admin can read all
        getUserRole(request.auth.uid) == 'admin' ||
        // Business owner can read own responses
        (getUserRole(request.auth.uid) == 'business_owner' && 
         resource.data.business_rut == getBusinessRutByFirebaseUid(request.auth.uid)) ||
        // Auditor can read responses from assigned businesses
        (getUserRole(request.auth.uid) == 'auditor' && 
         resource.data.business_rut in getAuditorAssignedBusinesses(request.auth.uid))
      );
      
      allow create: if request.auth != null && (
        // Admin can create all
        getUserRole(request.auth.uid) == 'admin' ||
        // Business owner can create own responses
        (getUserRole(request.auth.uid) == 'business_owner' && 
         request.resource.data.business_rut == getBusinessRutByFirebaseUid(request.auth.uid))
      );
      
      allow update: if request.auth != null && (
        // Admin can update all
        getUserRole(request.auth.uid) == 'admin' ||
        // Business owner can update own responses (except auditor fields)
        (getUserRole(request.auth.uid) == 'business_owner' && 
         resource.data.business_rut == getBusinessRutByFirebaseUid(request.auth.uid) &&
         !('auditor_id' in request.resource.data.diff(resource.data).affectedKeys())) ||
        // Auditor can update validation status and comments
        (getUserRole(request.auth.uid) == 'auditor' && 
         resource.data.business_rut in getAuditorAssignedBusinesses(request.auth.uid))
      );
    }
    
    // Auditors - admins manage, auditors read own
    match /auditors/{auditorId} {
      allow read: if request.auth != null && (
        getUserRole(request.auth.uid) == 'admin' ||
        (getUserRole(request.auth.uid) == 'auditor' && resource.data.firebase_uid == request.auth.uid)
      );
      allow write: if request.auth != null && getUserRole(request.auth.uid) == 'admin';
    }
    
    // Admin Users - only admins can access
    match /admin_users/{adminId} {
      allow read, write: if request.auth != null && getUserRole(request.auth.uid) == 'admin';
    }
    
    // Helper functions
    function getUserRole(firebaseUid) {
      // Check in business_profiles
      let businessQuery = exists(/databases/$(database)/documents/business_profiles/$(firebaseUid));
      if (businessQuery) {
        return 'business_owner';
      }
      
      // Check in auditors
      let auditorQuery = exists(/databases/$(database)/documents/auditors/$(firebaseUid));
      if (auditorQuery) {
        return 'auditor';
      }
      
      // Check in admin_users
      let adminQuery = exists(/databases/$(database)/documents/admin_users/$(firebaseUid));
      if (adminQuery) {
        return 'admin';
      }
      
      return null;
    }
    
    function getBusinessRutByFirebaseUid(firebaseUid) {
      // This would need to be implemented based on your indexing strategy
      // For now, assume the business profile document ID is stored somewhere accessible
      return get(/databases/$(database)/documents/business_profiles/$(firebaseUid)).data.rut;
    }
    
    function getAuditorAssignedBusinesses(firebaseUid) {
      // Get the assigned businesses for this auditor
      return get(/databases/$(database)/documents/auditors/$(firebaseUid)).data.assigned_businesses;
    }
  }
}
```

### 3. Rate Limiting
- Implementar rate limiting en API routes sensibles
- Protección contra ataques de fuerza bruta

## Métricas de Éxito

- [ ] 100% de rutas protegidas funcionando correctamente
- [ ] Tiempo de carga de autenticación < 2 segundos
- [ ] 0 fallos de seguridad en auditoría
- [ ] Experiencia de usuario fluida en login/logout
- [ ] Cobertura de tests > 80%

## Cronograma Estimado

| Fase | Duración | Dependencias |
|------|----------|--------------|
| Fase 1 | 2-3 horas | Acceso a Firebase Console |
| Fase 2 | 1-2 días | Fase 1 completada |
| Fase 3 | 1-2 días | Fase 2 completada |
| Fase 4 | 1 día | Fase 3 completada |
| Fase 5 | 1-2 días | Fases 2-4 completadas |
| Fase 6 | 1 día | Todas las fases anteriores |

**Total estimado: 5-8 días de desarrollo**

## Próximos Pasos

1. **Revisar y aprobar** este plan con el equipo
2. **Asignar recursos** para cada fase
3. **Comenzar con Fase 1** - configuración manual en Firebase Console
4. **Establecer reuniones de revisión** al final de cada fase
5. **Preparar entorno de testing** para validaciones continuas

---

*Este plan está basado en las mejores prácticas de seguridad y la arquitectura descrita en `01-authN-authZ.md`. Se recomienda revisar y ajustar según las necesidades específicas del proyecto.*
