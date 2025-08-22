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
- [ ] Crear/verificar base de datos `agro-extension-db`
- [ ] Crear colección `users` con estructura:
```javascript
{
  "uid": "firebase-user-id", // Document ID
  "role": "business_owner|auditor|admin",
  "displayName": "Nombre Usuario",
  "email": "usuario@ejemplo.com",
  "companyId": "company-123", // Para business_owner
  "permissions": {
    "canViewReports": true,
    "canEditData": false,
    "canManageUsers": false
  },
  "createdAt": "timestamp",
  "lastLogin": "timestamp"
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
  userRole: string | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, userData: any) => Promise<void>;
  signOut: () => Promise<void>;
  signInWithGoogle: () => Promise<void>;
}
```

#### 2.3 Componentes de UI
- [ ] Crear `/src/components/auth/LoginForm.tsx`
- [ ] Crear `/src/components/auth/RegisterForm.tsx`
- [ ] Crear `/src/components/auth/AuthGuard.tsx`
- [ ] Crear `/src/components/auth/RoleGuard.tsx`

#### 2.4 Páginas de Autenticación
- [ ] Crear `/src/app/auth/login/page.tsx`
- [ ] Crear `/src/app/auth/register/page.tsx`
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
- [ ] Crear estructura de rutas:
```
/src/app/api/
├── auth/
│   ├── register/route.ts
│   └── profile/route.ts
├── admin/
│   ├── users/route.ts
│   └── analytics/route.ts
├── business/
│   ├── reports/route.ts
│   └── data/route.ts
└── audit/
    ├── reviews/route.ts
    └── compliance/route.ts
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
│   │   └── profile/page.tsx
│   ├── api/
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── business/
│   │   └── audit/
│   ├── dashboard/
│   │   ├── admin/
│   │   ├── business/
│   │   └── audit/
│   └── layout.tsx (con AuthProvider)
├── components/
│   ├── auth/
│   │   ├── AuthGuard.tsx
│   │   ├── RoleGuard.tsx
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   └── ui/
├── contexts/
│   └── AuthContext.tsx
├── hooks/
│   └── useAuth.ts
├── lib/
│   └── firebase/
│       ├── config.ts
│       ├── server.ts
│       └── index.ts
├── utils/
│   ├── auth-server.ts
│   └── constants.ts
└── middleware.ts
```

## Roles y Permisos

### Definición de Roles

#### 1. Admin
- **Descripción**: Acceso completo al sistema
- **Permisos**:
  - Gestión de usuarios
  - Acceso a todas las funcionalidades
  - Configuración del sistema
  - Reportes globales

#### 2. Business Owner
- **Descripción**: Propietario de empresa con datos en el sistema
- **Permisos**:
  - Ver sus propios datos y reportes
  - Gestionar información de su empresa
  - Acceso a auditorías de su empresa
  - Dashboard empresarial

#### 3. Auditor
- **Descripción**: Auditor externo con acceso a datos específicos
- **Permisos**:
  - Ver datos de empresas asignadas
  - Crear reportes de auditoría
  - Acceso de solo lectura a la mayoría de datos
  - Dashboard de auditoría

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
    // Users can only read/write their own user document
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Business data access based on role and company
    match /companies/{companyId} {
      allow read: if request.auth != null && 
        (resource.data.ownerId == request.auth.uid || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
      allow write: if request.auth != null && 
        (resource.data.ownerId == request.auth.uid || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
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
