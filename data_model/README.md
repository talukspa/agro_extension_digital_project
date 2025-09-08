# AgroExtensión Digital - Modelo de Datos Firestore

Este proyecto implementa el modelo de datos para **AgroExtensión Digital**, una plataforma multi-tenant de extensión agrícola diseñada para gestionar certificaciones y estándares agro-industriales usando **Google Firestore**.

## Arquitectura General

### Paradigma NoSQL Multi-tenant
El sistema utiliza Firestore (base de datos NoSQL) con un diseño multi-tenant que permite a múltiples empresas (tenants) operar de forma independiente dentro de la misma instancia de la plataforma.

**Ventajas del diseño NoSQL:**
1. **Flexibilidad**: Cada documento puede tener estructura ligeramente diferente
2. **Rendimiento**: Datos relacionados embebidos reducen operaciones de lectura
3. **Escalabilidad**: Diseño multi-tenant eficiente

**Técnicas de relacionamiento:**
- **Embebido**: Objetos anidados para datos fuertemente acoplados
- **Referenciado**: IDs de documentos para datos independientes o compartidos

---

## Colecciones Principales

### 1. `user_types` (Collection)
**Propósito**: Define los tipos de usuario válidos en el sistema con sus permisos correspondientes.

**Document ID**: ID del tipo de usuario (debe coincidir con `id` y `name`)

**Estructura crítica**: `document_id = id = name` (patrón requerido para sincronización frontend/backend)

**Tipos de usuario definidos**:
- `admin`: Administrador del sistema
- `auditor`: Auditor de certificación  
- `business_user`: Usuario de empresa
- `business_owner`: Propietario de empresa

```typescript
interface UserType {
  id: string;           // debe coincidir con document_id y name
  name: string;         // debe coincidir con document_id e id
  description: string;
  permissions: string[];
  routes: string[];
}
```

### 2. `users` (Collection)
**Propósito**: Perfiles de todos los usuarios del sistema con asociaciones multi-tenant.

**Document ID**: Firebase Auth UID

```typescript
interface User {
  uid: string;
  name: string;
  email: string;
  userType: UserTypeId; // referencia a user_types
  businesses: string[]; // array de business IDs para multi-tenant
  createdAt: Timestamp;
  lastLogin: Timestamp;
  status: 'active' | 'inactive' | 'pending';
}
```

### 3. `businesses` (Collection)
**Propósito**: Entidades tenant del sistema (empresas/organizaciones).

**Document ID**: ID único generado automáticamente

```typescript
interface Business {
  id: string;
  rut: string;          // identificador tributario único
  legal_name: string;
  address: string;
  region: string;
  commune: string;
  business_size: string;
  process_type: string;
  owner_name: string;
  owner_email: string;
  owner_phone: string;
  owner_role: string;
  digital_tools_used_at_work: string[];
  digital_tools_experienced: string[];
  members: string[];    // array de user UIDs
  status: 'active' | 'suspended' | 'inactive';
  createdAt: Timestamp;
  updatedAt: Timestamp;
}
```

### 4. `auditor_profiles` (Collection)
**Propósito**: Perfiles específicos para auditores con certificaciones y asignaciones.

**Document ID**: Firebase Auth UID del auditor

```typescript
interface AuditorProfile {
  userId: string;       // referencia a users collection
  certifications: string[];
  specializations: string[];
  assignedBusinesses: string[]; // business IDs asignados
  status: 'active' | 'inactive';
  createdAt: Timestamp;
}
```

### 5. `standards` (Collection)
**Propósito**: Plantillas maestras de estándares de certificación.

**Document ID**: Nombre descriptivo del estándar (ej: `adecuacion-agroindustrial`)

```typescript
interface Standard {
  template_name: string;
  description: string;
  actions: Action[];    // array embebido de preguntas/acciones
  version: string;
  status: 'active' | 'deprecated';
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

interface Action {
  standard_code: string;  // código único (ej: "A001")
  level: 'Fundamental' | 'Básico' | 'Avanzado';
  points: number;
  dimension: string;
  theme: string;
  good_practice: string;
  action: string;
  verification_detail: string;
  verification_type: 'log' | 'image' | 'document' | 'none';
  valid_answers: string[];
  link: string;
  resources: Resource[];  // array embebido de recursos
}

interface Resource {
  type: string;         // 'Guía' | 'Curso' | 'Estándar' | 'Registro'
  detail: string;
  urls: {
    web?: string;
    pdf?: string;
    curso?: string;
  };
}
```

### 6. `responses` (Collection)
**Propósito**: Respuestas de empresas a estándares específicos (núcleo del sistema de certificación).

**Document ID**: ID único generado automáticamente

```typescript
interface Response {
  id: string;
  business_rut: string;     // referencia a business
  standard_template: string; // referencia a standard
  auditor_id?: string;      // referencia opcional a auditor
  is_completed: boolean;
  date: Timestamp;
  answers: Answer[];        // array embebido de respuestas
  status: 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected';
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

interface Answer {
  action: Action;          // copia embebida del action original (snapshot)
  answer_value: string;    // respuesta del usuario
  register?: Register;     // evidencia opcional embebida
}

interface Register {
  upload_timestamp: Timestamp;
  validation_status: 'pending' | 'validated' | 'rejected';
  validation_timestamp?: Timestamp;
  auditor_id?: string;
  auditor_comments?: string;
  
  // Campos condicionales según verification_type
  image_url?: string;      // si verification_type = 'image'
  document_url?: string;   // si verification_type = 'document'  
  logs?: LogEntry[];       // si verification_type = 'log'
}

interface LogEntry {
  standard_code: string;   // referencia al action
  data: Record<string, any>; // esquema definido por standard_code
  timestamp: Timestamp;
}
```

---

## Patrones de Diseño Críticos

### Multi-tenancy
- Cada operación debe incluir `businessId` para scope
- Usuarios pueden pertenecer a múltiples businesses
- Validación de permisos tanto client-side como server-side

### Snapshot Pattern (Respuestas)
- Cada `answer` embebe una copia completa del `action` original
- Garantiza inmutabilidad histórica aunque el estándar cambie
- Permite auditoría completa de lo que se preguntó vs. lo que se respondió

### Verificación Polimórfica
- El objeto `register` cambia estructura según `verification_type`
- `log`: estructura de datos definida por `standard_code`
- `image`/`document`: URLs a Firebase Storage
- Flexibilidad para nuevos tipos de verificación

### Consistencia de IDs
- `user_types`: `document_id = id = name` (requerido para sync frontend/backend)
- Otros documentos usan IDs autogenerados o naturales según contexto

---

## Flujo de Datos Principal

1. **Business** se registra → documento en `businesses`
2. **Users** se asocian al business → documentos en `users` con `businesses[]`
3. **Standard** se selecciona → documento de `standards`
4. **Response** se crea → documento en `responses` referenciando business y standard
5. Para cada `action` del standard:
   - Se crea `answer` embebido con snapshot del `action`
   - Si requiere verificación → se crea `register` embebido
   - Para logs → array de `LogEntry` con esquema específico
6. **Auditor** revisa → actualiza `validation_status` en cada `register`

---

## Scripts de Verificación

### Sincronización Frontend/Backend
```bash
cd data_model && uv run verify_basic_types_sync.py
```
Verifica que los `USER_TYPES` del frontend coincidan con documentos en Firestore.

### Normalización de Formato
```bash
cd data_model && uv run normalize_user_types_format.py  
```
Corrige formato de IDs en `user_types` collection.

---

## Consideraciones de Rendimiento

### Lecturas Optimizadas
- Embedding reduce operaciones: 1 read para response completa
- Indices en campos de query frecuente: `business_rut`, `standard_template`

### Escrituras Escalables
- Batch operations para updates masivos
- Transacciones para operaciones críticas (assign auditor + update status)

### Storage
- Archivos grandes en Firebase Storage con URLs en Firestore
- Compresión automática de imágenes
- Limpieza periódica de archivos huérfanos

---

## Evolución y Mantenimiento

### Versionado de Estándares
- Campo `version` en standards
- Snapshot pattern preserva consistencia histórica
- Migración gradual entre versiones

### Escalabilidad Multi-tenant
- Sharding por región geográfica si es necesario
- Indices compuestos para queries multi-tenant eficientes
- Monitoring por tenant para detectar hot spots

### Compliance y Auditoría
- Immutable audit trail en `register` objects
- Logs de todas las operaciones administrativas
- Backup incremental con retención por requerimientos legales
---

## Diagrama de Estructura de Datos

```mermaid
graph TD
    subgraph "Collections Principales"
        UT[user_types] 
        U[users]
        B[businesses]
        AP[auditor_profiles]
        S[standards]
        R[responses]
    end

    subgraph "Documentos Embebidos"
        R --> A[answers]
        A --> REG[register]
        REG --> L[logs]
        S --> AC[actions]
        AC --> RES[resources]
    end

    subgraph "Referencias"
        U -.-> UT
        U -.-> B
        AP -.-> U
        R -.-> B
        R -.-> AP
        A -.-> AC
    end

    subgraph "Patrones Multi-tenant"
        B --> |business_id| R
        U --> |businesses[]| B
        AP --> |assignedBusinesses[]| B
    end
```

## Ejemplo de Documento Response Completo

```json
{
  "id": "resp_001",
  "business_rut": "76.432.187-4",
  "standard_template": "adecuacion-agroindustrial",
  "auditor_id": "aud_carlos_ruiz",
  "is_completed": true,
  "status": "under_review",
  "date": "2025-09-08T10:00:00Z",
  "answers": [
    {
      "action": {
        "standard_code": "A001",
        "level": "Fundamental",
        "points": 5,
        "dimension": "Ambiente",
        "theme": "Agua",
        "good_practice": "Gestionar los recursos hídricos en la planta",
        "action": "La planta registra mensualmente el consumo de agua...",
        "verification_type": "log",
        "verification_detail": "Registro de consumo de agua mensual...",
        "valid_answers": ["Si cumplo", "No cumplo", "No cumplo, pero me es factible", "No aplica"],
        "resources": [...]
      },
      "answer_value": "Si cumplo",
      "register": {
        "upload_timestamp": "2025-09-08T10:30:00Z",
        "validation_status": "validated",
        "validation_timestamp": "2025-09-08T15:00:00Z",
        "auditor_id": "aud_carlos_ruiz",
        "auditor_comments": "Registro completo y consistente",
        "logs": [
          {
            "standard_code": "A001",
            "timestamp": "2025-08-01T00:00:00Z",
            "data": {
              "supply_source": "Canal",
              "monthly_consumption_m3": 150,
              "process_use_type": "Irrigation"
            }
          }
        ]
      }
    }
  ],
  "createdAt": "2025-09-08T09:00:00Z",
  "updatedAt": "2025-09-08T15:00:00Z"
}
```
