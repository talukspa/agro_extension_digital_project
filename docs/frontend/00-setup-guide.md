# Guía de Configuración Inicial del Frontend - Next.js

## Información General del Proyecto

Este proyecto utiliza **Next.js 15.4.6** con **App Router** y está configurado para despliegue en **Google Cloud Run**. La gestión de dependencias se realiza con **pnpm** en lugar de npm.

## Requisitos Previos

### Herramientas Requeridas
- **Node.js** v18 o superior
- **pnpm** v8 o superior
- **Firebase CLI** (para desarrollo local)
- **Google Cloud CLI** (para deployment)
- **Terraform** v1.5+ (para infraestructura)
- **Terragrunt** v0.50+ (para gestión de infraestructura)

### Verificación de Instalación
```bash
# Verificar versiones
node --version
pnpm --version
firebase --version
gcloud --version
terraform --version
terragrunt --version
```

## Configuración del Entorno de Desarrollo

### 1. Instalación de Dependencias
```bash
# Navegar al directorio del frontend
cd frontend/

# Instalar dependencias con pnpm
pnpm install

# Verificar instalación
pnpm list
```

### 3. Configuración de Variables de Entorno

### 🔐 Configuración de Secretos (REQUERIDO)

**IMPORTANTE**: Antes de cualquier deployment, configure todos los secretos requeridos usando Google Secret Manager.

```bash
# Paso 1: Navegar al directorio del proyecto
cd /workspaces/agro_extension_digital_project

# Paso 2: Ejecutar script de configuración de secretos
./scripts/setup-secrets.sh

# Paso 3: Validar que todos los secretos estén configurados
./scripts/validate-secrets.sh
```

**Ver documento completo**: [📋 Prerrequisitos de Variables de Entorno](./04-environment-variables-prerequisites.md)

### 🔑 Variables de Entorno Locales

Crear archivo `.env.local` para desarrollo local:

```bash
# Crear archivo de variables de entorno local
cat > .env.local << 'EOF'
# Firebase Configuration (para desarrollo local)
NEXT_PUBLIC_FIREBASE_API_KEY=tu_api_key_aqui
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=agro-extension-digital-npe.firebaseapp.com  
NEXT_PUBLIC_FIREBASE_PROJECT_ID=agro-extension-digital-npe
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=agro-extension-digital-npe.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=tu_sender_id_aqui
NEXT_PUBLIC_FIREBASE_APP_ID=tu_app_id_aqui
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=tu_measurement_id_aqui

# Development Settings
NODE_ENV=development
NEXT_PUBLIC_ENV=development
EOF
```

**⚠️ Seguridad**: 
- El archivo `.env.local` NO debe commitearse al repositorio
- Para producción, las variables se obtienen automáticamente de Google Secret Manager
- Ver [prerrequisitos completos](./04-environment-variables-prerequisites.md) para configuración de secretos

## 7. Gestión de Base de Datos

### 🗄️ Importar Base de Datos Existente en Terragrunt

**IMPORTANTE**: La base de datos `agro-extension-db` debe importarse en Terragrunt para gestión como infraestructura.

```bash
# Navegar al directorio del proyecto
cd /workspaces/agro_extension_digital_project

# Importar base de datos en desarrollo
./scripts/import-database.sh dev

# Verificar importación exitosa
cd cicd/stacks/dev/database
terragrunt state list
```

### 📊 Inicializar Datos de Prueba

Para desarrollo local, el proyecto incluye datos de muestra basados en el modelo de datos:

```bash
# Navegar al directorio de modelo de datos
cd /workspaces/agro_extension_digital_project/data_model

# Revisar estructura de datos de prueba
cat sample.json

# Inicializar Firestore con datos de muestra (desarrollo local)
./create_firestore_database.sh

# Alternativamente, usar el script de ingesta de datos
python3 ingest_data.py
```

#### 📋 Datos de Muestra Incluidos

**Business Profile de Ejemplo:**
- **RUT**: `76.432.187-4`
- **Empresa**: Exportadora de Ciruelas Paine
- **Ubicación**: Paine, Región Metropolitana
- **Tipo**: Producción Primaria
- **Propietario**: Juan Rojas

**Standards Templates:**
- **`ciruelas-aa`**: Estándares para producción y procesamiento de ciruelas agro-industriales
- **`produccion-primaria-pp`**: Estándares para producción primaria

**Códigos Estándar de Ejemplo:**
- **A001**: Gestión de recursos hídricos en plantas (verificación por bitácora)
- **A002**: Capacitación en gestión hídrica plantas (verificación por foto)
- **P001**: Registro de consumo de agua de riego (verificación por bitácora)
- **P002**: Capacitación en gestión hídrica predios (verificación por foto)

**Auditors:**
- Carlos Ruiz (`auditor_id: 1`)
- Ana Soto (`auditor_id: 2`)

#### 🧪 Testing con Datos de Muestra

```bash
# Verificar que los datos se cargaron correctamente
cd /workspaces/agro_extension_digital_project/data_model

# Listar todas las colecciones
python3 list_collections.py

# Verificar contenido de colecciones específicas
python3 debug_collections.py
```

**Ver documentación completa**: [🗄️ Gestión de Base de Datos](./06-database-management.md)

### 🔒 Configuración de Reglas de Seguridad

```bash
# Las reglas de seguridad se aplican automáticamente via Terragrunt
cd cicd/stacks/dev/database
terragrunt apply

# Para producción
cd ../../../prd/database
terragrunt apply
```

## 8. Validación Final

### 3. Scripts Disponibles
```bash
# Desarrollo con Turbopack (más rápido)
pnpm dev

# Desarrollo estándar
pnpm dev:standard

# Build para producción
pnpm build

# Iniciar en modo producción
pnpm start

# Linting
pnpm lint

# Type checking
pnpm type-check
```

## Estructura del Proyecto

```
frontend/
├── src/                      # Código fuente Next.js
│   ├── app/                  # App Router (Next.js 13+)
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── api/             # API Routes
│   ├── components/          # Componentes reutilizables
│   ├── contexts/           # React Contexts
│   ├── hooks/              # Custom Hooks
│   ├── lib/                # Librerías y configuraciones
│   │   └── firebase/       # Configuración Firebase
│   ├── types/              # Definiciones TypeScript
│   └── utils/              # Funciones auxiliares
├── public/                 # Archivos estáticos
├── docs/                   # Documentación específica
├── .env.local             # Variables de entorno locales
├── .env.example           # Ejemplo de variables de entorno
├── next.config.ts         # Configuración Next.js
├── package.json           # Dependencias y scripts
├── pnpm-lock.yaml        # Lock file de pnpm
├── tsconfig.json         # Configuración TypeScript
└── Dockerfile            # Configuración para Cloud Run

cicd/                      # Infraestructura como Código
├── modules/               # Módulos Terraform reutilizables
│   ├── backend/          # Infraestructura backend
│   └── frontend/         # Infraestructura frontend
│       ├── main.tf       # Recursos Cloud Run + Service Account
│       ├── variables.tf  # Variables del módulo
│       ├── outputs.tf    # Outputs del módulo
│       └── providers.tf  # Proveedores Terraform
├── stacks/               # Configuraciones por ambiente
│   ├── common.yaml       # Configuración compartida
│   ├── root.hcl         # Configuración base Terragrunt
│   ├── dev/             # Ambiente desarrollo
│   │   ├── env.yaml     # Variables específicas DEV
│   │   └── frontend/    # Stack frontend DEV
│   │       └── terragrunt.hcl
│   └── prd/             # Ambiente producción
│       ├── env.yaml     # Variables específicas PRD
│       └── frontend/    # Stack frontend PRD
│           └── terragrunt.hcl
└── docs/                # Documentación de infraestructura
```

## Tecnologías Principales

### Frontend Stack
- **Framework**: Next.js 15.4.6 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: CSS Modules + Globals CSS
- **State Management**: React Context API
- **Package Manager**: pnpm

### Firebase Integration
- **Authentication**: Firebase Auth
- **Database**: Cloud Firestore (`agro-extension-db`)
- **Storage**: Cloud Storage (configurado)
- **Admin SDK**: Para operaciones del servidor

### Data Model Structure

El proyecto utiliza un modelo de datos NoSQL optimizado para Firestore con las siguientes colecciones principales:

#### 📊 Colecciones Firestore

1. **`business_profiles`** - Perfiles de empresas
   - **Document ID**: RUT de la empresa (ej: `76.432.187-4`)
   - **Contenido**: Información básica de la empresa, propietario, ubicación y tamaño
   - **Ejemplo**: Exportadora de Ciruelas Paine

2. **`standards`** - Plantillas de estándares
   - **Document ID**: Nombre descriptivo (ej: `ciruelas-aa`, `produccion-primaria-pp`)
   - **Contenido**: Descripción y array de preguntas (`questions`) con códigos estándar
   - **Ejemplo**: Estándares para producción y procesamiento de ciruelas agro-industriales

3. **`auditors`** - Registro de auditores
   - **Document ID**: ID único del auditor
   - **Contenido**: Información de contacto y empresas asignadas

4. **`responses`** - Respuestas de empresas a estándares
   - **Document ID**: Auto-generado por Firestore
   - **Contenido**: Referencia a empresa, auditor, estado y array de respuestas (`answers`)

#### 🔗 Relaciones y Estructura de Datos

```typescript
// Estructura principal de una respuesta
interface Response {
  business_rut: string;           // Referencia a business_profiles
  auditor_id: number;             // Referencia a auditors
  is_completed: boolean;
  date: string;
  answers: Answer[];              // Array de respuestas embebidas
}

// Estructura de una respuesta individual
interface Answer {
  action: StandardAction;         // Copia embebida de la pregunta
  answer_value: string;           // Respuesta del usuario
  register?: Register;            // Evidencia (solo si se requiere verificación)
}

// Estructura para evidencia y verificación
interface Register {
  upload_timestamp: string;
  validation_status: 'pending' | 'validated' | 'rejected';
  auditor_comments?: string;
  
  // Campos condicionales según verification_type:
  image_url?: string;             // Para verification_type: 'image'
  document_url?: string;          // Para verification_type: 'document'
  logs?: LogEntry[];              // Para verification_type: 'log'
}

// Estructura para registros de bitácora
interface LogEntry {
  standard_code: string;          // Código del estándar (ej: "A001", "P001")
  data: Record<string, any>;      // Datos específicos según el código
}
```

#### 📝 Ejemplos de Códigos Estándar

**A001 - Consumo de Agua (Plantas Agroindustriales)**
```typescript
{
  standard_code: "A001",
  data: {
    supply_source: "Canal",
    monthly_consumption_m3: 150,
    process_use_type: "Irrigation"
  }
}
```

**P001 - Consumo de Agua de Riego (Producción Primaria)**
```typescript
{
  standard_code: "P001",
  data: {
    date: "2024-08-28",
    crop: "Ciruelas",
    sector: "Sector Norte",
    supply_source: "Pozo profundo",
    surface_area: 5.2,
    irrigation_time: 240,
    weekly_irrigation_days: 3,
    daily_water_volume_liters: 15000,
    accumulated_water_volume_liters: 45000
  }
}
```

#### 🎯 Tipos de Verificación

- **`Foto`**: Evidencia fotográfica almacenada en Cloud Storage
- **`Documento`**: PDFs, Word, etc. almacenados en Cloud Storage  
- **`Bitácora`**: Datos estructurados ingresados directamente en la aplicación

### Deployment
- **Platform**: Google Cloud Run
- **Project**: `agro-extension-digital-npe`
- **Container**: Docker (Dockerfile incluido)
- **Infrastructure**: Terraform + Terragrunt
- **Registry**: Google Artifact Registry
- **State Management**: GCS Backend (`agro-extension-digital-npe-tf-state-bucket`)

## Comandos Útiles con pnpm

### Gestión de Dependencias
```bash
# Agregar dependencia de producción
pnpm add package-name

# Agregar dependencia de desarrollo
pnpm add -D package-name

# Agregar dependencia específica de workspace
pnpm add package-name --workspace-root

# Actualizar dependencias
pnpm update

# Remover dependencia
pnpm remove package-name

# Limpiar node_modules
pnpm install --frozen-lockfile
```

### Scripts de Desarrollo
```bash
# Desarrollo con hot reload
pnpm dev

# Build optimizado
pnpm build

# Analizar bundle
pnpm build:analyze

# Test de tipos
pnpm type-check

# Linting y formato
pnpm lint
pnpm lint:fix
```

## Configuración de Firebase Local

### 1. Login en Firebase
```bash
firebase login
```

### 2. Inicializar proyecto local
```bash
# En el directorio frontend/
firebase init

# Seleccionar:
# - Firestore
# - Functions (si planeas usar)
# - Hosting (para desarrollo local)
```

### 3. Emuladores locales (opcional)
```bash
# Iniciar emuladores
firebase emulators:start

# Solo Firestore
firebase emulators:start --only firestore

# Solo Authentication
firebase emulators:start --only auth
```

## Desarrollo Local

### 🔧 Configuración de TypeScript Types

Para trabajar con el modelo de datos Firestore, crear el archivo `src/types/firestore.ts`:

```typescript
// src/types/firestore.ts

// === Colecciones principales ===

export interface BusinessProfile {
  rut: string;
  commune: string;
  digital_tools_used_at_work: string[];
  business_size: 'Microempresa' | 'Pequeña empresa' | 'Mediana empresa' | 'Gran empresa';
  legal_name: string;
  address: string;
  region: string;
  owner_phone: string;
  process_type: 'Producción Primaria' | 'Procesamiento Agroindustrial';
  owner_email: string;
  owner_role: string;
  digital_tools_experienced: string[];
  owner_name: string;
}

export interface StandardTemplate {
  template_name: string;
  description: string;
  questions: StandardAction[];
}

export interface StandardAction {
  standard_code: string;
  level: 'Fundamental' | 'Básico' | 'Avanzado';
  points: number;
  dimension: string;
  theme: string;
  good_practice: string;
  action: string;
  verification_medium: string;
  verification_type: 'Foto' | 'Documento' | 'Bitácora';
  resources?: Resource[];
}

export interface Resource {
  resource_code: string;
  type: 'Señalética' | 'TDR' | 'Guía' | 'Video' | 'Documento';
  detail: string;
  url: string;
}

export interface Auditor {
  auditor_id: number;
  auditor_name: string;
  auditor_email: string;
  assigned_businesses?: string[]; // Array de RUTs
}

// === Respuestas y Registros ===

export interface Response {
  id?: string; // Auto-generado por Firestore
  business_rut: string;
  standard_template: string;
  auditor_id?: number;
  is_completed: boolean;
  date: string;
  answers: Answer[];
}

export interface Answer {
  action: StandardAction; // Copia embebida de la pregunta
  answer_value: string;
  register?: Register;
}

export interface Register {
  upload_timestamp: string;
  validation_status: 'pending' | 'validated' | 'rejected';
  validation_timestamp?: string;
  auditor_comments?: string;
  
  // Campos condicionales según verification_type
  image_url?: string;      // Para 'Foto'
  document_url?: string;   // Para 'Documento'
  logs?: LogEntry[];       // Para 'Bitácora'
}

export interface LogEntry {
  standard_code: string;
  data: Record<string, any>;
}

// === Esquemas específicos para logs ===

export interface WaterConsumptionLog {
  supply_source: string;
  monthly_consumption_m3: number;
  process_use_type: string;
}

export interface IrrigationWaterLog {
  date: string;
  crop: string;
  sector: string;
  supply_source: string;
  surface_area: number;
  irrigation_time: number;
  weekly_irrigation_days: number;
  daily_water_volume_liters: number;
  accumulated_water_volume_liters: number;
}

export interface FertilizerApplicationLog {
  product_name: string;
  lot_number: number;
  application_date: string;
  dose_applied: number;
}

// === Utilidades de validación ===

export const VERIFICATION_TYPES = ['Foto', 'Documento', 'Bitácora'] as const;
export const VALIDATION_STATUSES = ['pending', 'validated', 'rejected'] as const;
export const BUSINESS_SIZES = ['Microempresa', 'Pequeña empresa', 'Mediana empresa', 'Gran empresa'] as const;
export const PROCESS_TYPES = ['Producción Primaria', 'Procesamiento Agroindustrial'] as const;

// === Helpers para el frontend ===

export function getLogDataSchema(standardCode: string): Record<string, any> {
  const schemas: Record<string, any> = {
    'A001': {
      supply_source: { type: 'string', required: true },
      monthly_consumption_m3: { type: 'number', required: true },
      process_use_type: { type: 'string', required: true }
    },
    'P001': {
      date: { type: 'string', required: true },
      crop: { type: 'string', required: true },
      sector: { type: 'string', required: true },
      supply_source: { type: 'string', required: true },
      surface_area: { type: 'number', required: true },
      irrigation_time: { type: 'number', required: true },
      weekly_irrigation_days: { type: 'number', required: true },
      daily_water_volume_liters: { type: 'number', required: true },
      accumulated_water_volume_liters: { type: 'number', required: true }
    },
    'A033': {
      product_name: { type: 'string', required: true },
      lot_number: { type: 'number', required: true },
      application_date: { type: 'string', required: true },
      dose_applied: { type: 'number', required: true }
    }
  };
  
  return schemas[standardCode] || {};
}
```

### 🔥 Configuración de Firestore Client

Crear `src/lib/firebase/firestore.ts`:

```typescript
// src/lib/firebase/firestore.ts
import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  addDoc, 
  updateDoc, 
  query, 
  where, 
  orderBy,
  Timestamp 
} from 'firebase/firestore';
import { db } from './config';
import type { 
  BusinessProfile, 
  StandardTemplate, 
  Response, 
  Auditor 
} from '@/types/firestore';

// === Operaciones Business Profiles ===

export async function getBusinessProfile(rut: string): Promise<BusinessProfile | null> {
  const docRef = doc(db, 'business_profiles', rut);
  const docSnap = await getDoc(docRef);
  
  if (docSnap.exists()) {
    return docSnap.data() as BusinessProfile;
  }
  return null;
}

export async function getAllBusinessProfiles(): Promise<BusinessProfile[]> {
  const querySnapshot = await getDocs(collection(db, 'business_profiles'));
  return querySnapshot.docs.map(doc => doc.data() as BusinessProfile);
}

// === Operaciones Standards ===

export async function getStandardTemplate(templateName: string): Promise<StandardTemplate | null> {
  const docRef = doc(db, 'standards', templateName);
  const docSnap = await getDoc(docRef);
  
  if (docSnap.exists()) {
    return docSnap.data() as StandardTemplate;
  }
  return null;
}

export async function getAllStandardTemplates(): Promise<StandardTemplate[]> {
  const querySnapshot = await getDocs(collection(db, 'standards'));
  return querySnapshot.docs.map(doc => ({
    ...doc.data(),
    template_name: doc.id
  })) as StandardTemplate[];
}

// === Operaciones Responses ===

export async function createResponse(response: Omit<Response, 'id'>): Promise<string> {
  const docRef = await addDoc(collection(db, 'responses'), {
    ...response,
    date: Timestamp.fromDate(new Date(response.date))
  });
  return docRef.id;
}

export async function getResponsesByBusiness(businessRut: string): Promise<Response[]> {
  const q = query(
    collection(db, 'responses'),
    where('business_rut', '==', businessRut),
    orderBy('date', 'desc')
  );
  
  const querySnapshot = await getDocs(q);
  return querySnapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data(),
    date: doc.data().date.toDate().toISOString()
  })) as Response[];
}

export async function updateResponseCompletion(responseId: string, isCompleted: boolean): Promise<void> {
  const docRef = doc(db, 'responses', responseId);
  await updateDoc(docRef, { is_completed: isCompleted });
}

// === Operaciones Auditors ===

export async function getAllAuditors(): Promise<Auditor[]> {
  const querySnapshot = await getDocs(collection(db, 'auditors'));
  return querySnapshot.docs.map(doc => ({
    ...doc.data(),
    auditor_id: doc.id
  })) as Auditor[];
}

export async function getAuditorById(auditorId: number): Promise<Auditor | null> {
  const docRef = doc(db, 'auditors', auditorId.toString());
  const docSnap = await getDoc(docRef);
  
  if (docSnap.exists()) {
    return docSnap.data() as Auditor;
  }
  return null;
}
```

### 1. Iniciar servidor de desarrollo
```bash
cd frontend/
pnpm dev
```

### 2. Acceder a la aplicación
- **Frontend**: http://localhost:3000
- **Firebase Emulators** (si están activos): http://localhost:4000

### ⚛️ Patrones de Desarrollo con el Modelo de Datos

#### 1. Componente para Mostrar Business Profile

```typescript
// src/components/BusinessProfile.tsx
import { useEffect, useState } from 'react';
import { getBusinessProfile } from '@/lib/firebase/firestore';
import type { BusinessProfile } from '@/types/firestore';

interface BusinessProfileProps {
  rut: string;
}

export function BusinessProfileComponent({ rut }: BusinessProfileProps) {
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await getBusinessProfile(rut);
        setProfile(data);
      } catch (error) {
        console.error('Error fetching business profile:', error);
      } finally {
        setLoading(false);
      }
    }
    
    fetchProfile();
  }, [rut]);

  if (loading) return <div>Cargando perfil...</div>;
  if (!profile) return <div>Perfil no encontrado</div>;

  return (
    <div className="business-profile">
      <h2>{profile.legal_name}</h2>
      <p><strong>RUT:</strong> {profile.rut}</p>
      <p><strong>Dirección:</strong> {profile.address}, {profile.commune}</p>
      <p><strong>Propietario:</strong> {profile.owner_name}</p>
      <p><strong>Tipo de Proceso:</strong> {profile.process_type}</p>
      <p><strong>Tamaño:</strong> {profile.business_size}</p>
    </div>
  );
}
```

#### 2. Componente para Formularios de Estándares

```typescript
// src/components/StandardForm.tsx
import { useState } from 'react';
import { getLogDataSchema } from '@/types/firestore';
import type { StandardAction, LogEntry } from '@/types/firestore';

interface StandardFormProps {
  action: StandardAction;
  onSubmit: (answer: string, logData?: LogEntry) => void;
}

export function StandardForm({ action, onSubmit }: StandardFormProps) {
  const [answer, setAnswer] = useState('');
  const [logData, setLogData] = useState<Record<string, any>>({});

  const isLogRequired = action.verification_type === 'Bitácora';
  const schema = isLogRequired ? getLogDataSchema(action.standard_code) : {};

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isLogRequired) {
      const logEntry: LogEntry = {
        standard_code: action.standard_code,
        data: logData
      };
      onSubmit(answer, logEntry);
    } else {
      onSubmit(answer);
    }
  };

  const renderLogForm = () => {
    if (!isLogRequired) return null;

    return (
      <div className="log-form">
        <h4>Registro de Datos - {action.standard_code}</h4>
        {Object.entries(schema).map(([field, config]: [string, any]) => (
          <div key={field} className="form-field">
            <label>
              {field.replace(/_/g, ' ').toUpperCase()}
              {config.required && ' *'}
            </label>
            <input
              type={config.type === 'number' ? 'number' : 'text'}
              required={config.required}
              value={logData[field] || ''}
              onChange={(e) => setLogData(prev => ({
                ...prev,
                [field]: config.type === 'number' ? Number(e.target.value) : e.target.value
              }))}
            />
          </div>
        ))}
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} className="standard-form">
      <div className="standard-info">
        <h3>{action.good_practice}</h3>
        <p><strong>Código:</strong> {action.standard_code}</p>
        <p><strong>Nivel:</strong> {action.level}</p>
        <p><strong>Puntos:</strong> {action.points}</p>
        <p><strong>Acción:</strong> {action.action}</p>
        <p><strong>Verificación:</strong> {action.verification_type}</p>
      </div>

      <div className="answer-section">
        <label>
          Respuesta:
          <select 
            value={answer} 
            onChange={(e) => setAnswer(e.target.value)}
            required
          >
            <option value="">Seleccionar...</option>
            <option value="Cumple">Cumple</option>
            <option value="No Cumple">No Cumple</option>
            <option value="En Proceso">En Proceso</option>
            <option value="No Aplica">No Aplica</option>
          </select>
        </label>
      </div>

      {renderLogForm()}

      <button type="submit">Guardar Respuesta</button>
    </form>
  );
}
```

#### 3. Hook Personalizado para Gestión de Respuestas

```typescript
// src/hooks/useStandardResponse.ts
import { useState, useCallback } from 'react';
import { createResponse, updateResponseCompletion } from '@/lib/firebase/firestore';
import type { Response, Answer, StandardAction } from '@/types/firestore';

export function useStandardResponse(businessRut: string, templateName: string) {
  const [currentResponse, setCurrentResponse] = useState<Response | null>(null);
  const [loading, setLoading] = useState(false);

  const initializeResponse = useCallback(async (auditorId?: number) => {
    setLoading(true);
    try {
      const newResponse: Omit<Response, 'id'> = {
        business_rut: businessRut,
        standard_template: templateName,
        auditor_id: auditorId,
        is_completed: false,
        date: new Date().toISOString(),
        answers: []
      };

      const responseId = await createResponse(newResponse);
      setCurrentResponse({ id: responseId, ...newResponse });
    } catch (error) {
      console.error('Error creating response:', error);
    } finally {
      setLoading(false);
    }
  }, [businessRut, templateName]);

  const addAnswer = useCallback((action: StandardAction, answerValue: string, register?: any) => {
    if (!currentResponse) return;

    const newAnswer: Answer = {
      action,
      answer_value: answerValue,
      register
    };

    setCurrentResponse(prev => ({
      ...prev!,
      answers: [...prev!.answers, newAnswer]
    }));
  }, [currentResponse]);

  const completeResponse = useCallback(async () => {
    if (!currentResponse?.id) return;

    setLoading(true);
    try {
      await updateResponseCompletion(currentResponse.id, true);
      setCurrentResponse(prev => ({ ...prev!, is_completed: true }));
    } catch (error) {
      console.error('Error completing response:', error);
    } finally {
      setLoading(false);
    }
  }, [currentResponse]);

  return {
    currentResponse,
    loading,
    initializeResponse,
    addAnswer,
    completeResponse
  };
}
```

### 3. Hot Reload
- Los cambios en archivos `.tsx`, `.ts`, `.css` se reflejan automáticamente
- Turbopack acelera significativamente el hot reload

### 🧪 Validación y Testing del Modelo de Datos

#### 1. Validación de Esquemas de Log

```typescript
// src/utils/validation.ts
import { getLogDataSchema } from '@/types/firestore';

export function validateLogData(standardCode: string, data: Record<string, any>): { isValid: boolean; errors: string[] } {
  const schema = getLogDataSchema(standardCode);
  const errors: string[] = [];

  for (const [field, config] of Object.entries(schema)) {
    const value = data[field];
    
    if (config.required && (value === undefined || value === null || value === '')) {
      errors.push(`El campo ${field} es requerido`);
      continue;
    }

    if (value !== undefined && value !== null && value !== '') {
      if (config.type === 'number' && isNaN(Number(value))) {
        errors.push(`El campo ${field} debe ser un número`);
      }
      
      if (config.type === 'string' && typeof value !== 'string') {
        errors.push(`El campo ${field} debe ser texto`);
      }
    }
  }

  return { isValid: errors.length === 0, errors };
}

// Ejemplo de uso
const waterLogData = {
  supply_source: "Canal",
  monthly_consumption_m3: 150,
  process_use_type: "Irrigation"
};

const validation = validateLogData('A001', waterLogData);
if (!validation.isValid) {
  console.error('Errores de validación:', validation.errors);
}
```

#### 2. Testing de Componentes con Datos de Muestra

```typescript
// src/__tests__/BusinessProfile.test.tsx
import { render, screen } from '@testing-library/react';
import { BusinessProfileComponent } from '@/components/BusinessProfile';

// Mock del servicio Firestore
jest.mock('@/lib/firebase/firestore', () => ({
  getBusinessProfile: jest.fn().mockResolvedValue({
    rut: "76.432.187-4",
    legal_name: "Exportadora de Ciruelas Paine",
    commune: "Paine",
    business_size: "Microempresa",
    address: "Av. Gral. Baquedano 108",
    region: "Metropolitana",
    owner_phone: "+56987654321",
    process_type: "Producción Primaria",
    owner_email: "contacto@exportadorapaine.cl",
    owner_role: "Dueño",
    owner_name: "Juan Rojas"
  })
}));

describe('BusinessProfile Component', () => {
  test('renders business profile correctly', async () => {
    render(<BusinessProfileComponent rut="76.432.187-4" />);
    
    expect(await screen.findByText('Exportadora de Ciruelas Paine')).toBeInTheDocument();
    expect(screen.getByText('RUT: 76.432.187-4')).toBeInTheDocument();
    expect(screen.getByText('Juan Rojas')).toBeInTheDocument();
    expect(screen.getByText('Producción Primaria')).toBeInTheDocument();
  });
});
```

#### 3. Simulación de Respuestas Completas

```typescript
// src/utils/mockData.ts
import type { Response, StandardAction } from '@/types/firestore';

export const mockStandardActions: StandardAction[] = [
  {
    standard_code: "A001",
    level: "Fundamental",
    points: 5,
    dimension: "Ambiente",
    theme: "Agua",
    good_practice: "Gestionar los recursos hídricos en la planta",
    action: "La planta registra mensualmente el consumo de agua...",
    verification_medium: "Registro de consumo de agua mensual...",
    verification_type: "Bitácora"
  },
  {
    standard_code: "A002",
    level: "Básico",
    points: 2,
    dimension: "Ambiente",
    theme: "Agua",
    good_practice: "Gestionar los recursos hídricos en la planta",
    action: "La planta capacita a las personas tomadoras de decisiones...",
    verification_medium: "Registro de ejecución de capacitaciones...",
    verification_type: "Foto"
  }
];

export const mockCompleteResponse: Response = {
  id: "mock-response-1",
  business_rut: "76.432.187-4",
  standard_template: "ciruelas-aa",
  auditor_id: 1,
  is_completed: true,
  date: "2024-08-10T10:00:00Z",
  answers: [
    {
      action: mockStandardActions[0],
      answer_value: "Cumple",
      register: {
        upload_timestamp: "2024-08-10T10:00:00Z",
        validation_status: "validated",
        validation_timestamp: "2024-08-10T15:00:00Z",
        auditor_comments: "Registro completo y consistente.",
        logs: [
          {
            standard_code: "A001",
            data: {
              supply_source: "Canal",
              monthly_consumption_m3: 150,
              process_use_type: "Irrigation"
            }
          }
        ]
      }
    },
    {
      action: mockStandardActions[1],
      answer_value: "En Proceso",
      register: {
        upload_timestamp: "2024-08-10T11:00:00Z",
        validation_status: "pending",
        image_url: "https://storage.googleapis.com/bucket/image.jpg"
      }
    }
  ]
};

// Función para generar datos de prueba
export function generateMockLogData(standardCode: string): Record<string, any> {
  const mockData: Record<string, Record<string, any>> = {
    'A001': {
      supply_source: "Canal",
      monthly_consumption_m3: Math.floor(Math.random() * 200) + 50,
      process_use_type: "Irrigation"
    },
    'P001': {
      date: new Date().toISOString().split('T')[0],
      crop: "Ciruelas",
      sector: `Sector ${Math.floor(Math.random() * 5) + 1}`,
      supply_source: "Pozo profundo",
      surface_area: Math.round((Math.random() * 10 + 1) * 10) / 10,
      irrigation_time: Math.floor(Math.random() * 300) + 120,
      weekly_irrigation_days: Math.floor(Math.random() * 7) + 1,
      daily_water_volume_liters: Math.floor(Math.random() * 20000) + 5000,
      accumulated_water_volume_liters: Math.floor(Math.random() * 100000) + 20000
    }
  };

  return mockData[standardCode] || {};
}
```

## Build y Deployment

### Configuración de Infraestructura

#### 1. Autenticación en Google Cloud
```bash
# Login en Google Cloud
gcloud auth login
gcloud auth application-default login

# Configurar proyecto
gcloud config set project agro-extension-digital-npe
```

#### 2. Validar Infraestructura con Terragrunt
```bash
# Navegar al directorio de infraestructura
cd cicd/stacks/dev/frontend/

# Validar configuración
terragrunt validate

# Planificar cambios
terragrunt plan

# Aplicar infraestructura (solo si es necesario)
terragrunt apply
```

### Build Local
```bash
# Crear build optimizado
pnpm build

# Probar build localmente
pnpm start
```

### Deployment a Cloud Run

### Deployment a Cloud Run

#### 🔐 Prerrequisitos de Deployment

**IMPORTANTE**: Antes de cualquier deployment, configure todos los secretos requeridos.

```bash
# 1. Verificar secretos están configurados
cd /workspaces/agro_extension_digital_project
./scripts/validate-secrets.sh

# 2. Autenticación Google Cloud
gcloud auth login
gcloud auth application-default login

# 3. Configurar proyecto
gcloud config set project agro-extension-digital-npe

# 4. Verificar permisos IAM
gcloud projects get-iam-policy agro-extension-digital-npe \
    --flatten="bindings[].members" \
    --format='table(bindings.role)' \
    --filter="bindings.members:$(gcloud config get-value account)"
```

#### Opción 1: Deployment Automatizado con Script (RECOMENDADO)

```bash
# Navegar al directorio del proyecto
cd /workspaces/agro_extension_digital_project

# Deploy a desarrollo (incluye build, tests, docker push y terragrunt apply)
./scripts/deploy-frontend.sh dev

# Deploy a producción  
./scripts/deploy-frontend.sh prd
```

**El script automatizado incluye**:
- ✅ Verificación de prerrequisitos y herramientas
- ✅ Validación de secretos configurados  
- ✅ Instalación de dependencias con pnpm
- ✅ Tests de TypeScript y linting
- ✅ Build optimizado de Next.js
- ✅ Build y push de imagen Docker
- ✅ Deployment con Terragrunt
- ✅ Verificación final y URL del servicio

#### Opción 2: Deployment Manual Paso a Paso

```bash
# Build de imagen Docker
cd frontend
docker build -t us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-frontend-app:latest .

# Push a Google Artifact Registry
docker push us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-frontend-app:latest

# Deploy con Terragrunt
cd ../cicd/stacks/dev/frontend
terragrunt apply

# Para producción
cd ../../../prd/frontend  
terragrunt apply
```

#### 🔄 Variables de Entorno en Cloud Run

Las variables de entorno se inyectan automáticamente usando `run_cmd` en Terragrunt:

```hcl
# Ejemplo de cómo Terragrunt inyecta las variables
inputs = {
  # Variables de Firebase obtenidas de Google Secret Manager
  firebase_api_key = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-api-key", "--project=${local.project_id}")
  firebase_auth_domain = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-auth-domain", "--project=${local.project_id}")
  # ... más variables
}
```

**⚠️ Importante**: 
- Las variables se obtienen en tiempo de `terragrunt apply`
- No se almacenan en archivos de configuración
- Se inyectan directamente en Cloud Run como variables de entorno

#### Opción 3: Deploy Directo con gcloud (solo para testing)
```bash
# Build de imagen Docker
docker build -t gcr.io/agro-extension-digital-npe/agent-frontend-app:latest .

# Push a Artifact Registry
docker push gcr.io/agro-extension-digital-npe/agent-frontend-app:latest

# La infraestructura Terragrunt se encarga del deployment automático
```

#### Opción 3: Deploy Directo con gcloud (solo para testing)

```bash
# Deploy directo (no recomendado para producción)
gcloud run deploy frontend-app-dev \
  --source . \
  --platform managed \
  --region us-central1 \
  --project agro-extension-digital-npe \
  --allow-unauthenticated
```

**⚠️ Nota**: Este método no incluye las variables de entorno de Firebase configuradas en Terragrunt.

### Variables de Entorno en Cloud Run

Las variables de entorno se gestionan a través de Terragrunt en el archivo de configuración del módulo frontend. Las principales variables son:

```yaml
# En cicd/stacks/dev/env.yaml o prd/env.yaml
environment:
  name: "dev"  # o "prd"
  min_scale: 0
  max_scale: 10

resources:
  cpu: "1000m"
  memory: "512Mi"
```

## Troubleshooting Común

### Problemas con pnpm
```bash
# Limpiar cache de pnpm
pnpm store prune

# Reinstalar dependencias
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Problemas con Firebase
```bash
# Verificar configuración
firebase projects:list
firebase use agro-extension-digital-npe

# Revisar reglas de Firestore
firebase firestore:rules:get
```

### Problemas con Infraestructura (Terragrunt/Terraform)
```bash
# Verificar estado de infraestructura
cd cicd/stacks/dev/frontend/
terragrunt show

# Refrescar estado
terragrunt refresh

# Re-importar recursos si es necesario
terragrunt import google_cloud_run_v2_service.frontend_service projects/agro-extension-digital-npe/locations/us-central1/services/frontend-app-dev

# Limpiar cache de Terragrunt
rm -rf .terragrunt-cache/
terragrunt init
```

## Gestión de Infraestructura con Terragrunt

### Arquitectura de Infraestructura

El proyecto utiliza una estructura Terragrunt que permite:
- **Separación por ambientes**: `dev/` y `prd/`
- **Reutilización de módulos**: Módulos Terraform en `modules/`
- **Configuración centralizada**: Variables compartidas en `common.yaml`
- **Estado remoto**: Backend GCS para state files

### Comandos Terragrunt Útiles

```bash
# Navegar al ambiente deseado
cd cicd/stacks/dev/frontend/  # o prd/frontend/

# Comandos básicos
terragrunt init     # Inicializar
terragrunt plan     # Planificar cambios
terragrunt apply    # Aplicar cambios
terragrunt destroy  # Destruir recursos (¡cuidado!)

# Comandos de diagnóstico
terragrunt show     # Mostrar estado actual
terragrunt output   # Mostrar outputs
terragrunt validate # Validar configuración

# Operaciones avanzadas
terragrunt state list                    # Listar recursos en state
terragrunt state show <resource_name>    # Mostrar recurso específico
terragrunt refresh                       # Actualizar state desde GCP
```

### Configuración por Ambientes

#### Desarrollo (dev)
- **Proyecto**: `agro-extension-digital-npe`
- **Región**: `us-central1`
- **Min Scale**: 0 (scale-to-zero habilitado)
- **Max Scale**: 10
- **Recursos**: CPU 1000m, Memory 512Mi

#### Producción (prd)
- **Proyecto**: `agro-extension-digital-npe`
- **Región**: `us-central1`
- **Min Scale**: 1 (siempre una instancia corriendo)
- **Max Scale**: 100
- **Recursos**: CPU 2000m, Memory 1Gi

### Modificar Configuración de Infraestructura

#### 1. Cambios en configuración de ambiente
```bash
# Editar variables específicas del ambiente
vim cicd/stacks/dev/env.yaml

# Aplicar cambios
cd cicd/stacks/dev/frontend/
terragrunt apply
```

#### 2. Cambios en módulos Terraform
```bash
# Editar módulo
vim cicd/modules/frontend/main.tf

# Aplicar en todos los ambientes que usen el módulo
cd cicd/stacks/dev/frontend/ && terragrunt apply
cd cicd/stacks/prd/frontend/ && terragrunt apply
```

#### 3. Agregar variables de entorno a Cloud Run
```bash
# Editar módulo para agregar env vars
vim cicd/modules/frontend/main.tf

# Agregar en la sección containers:
env {
  name  = "FIREBASE_PROJECT_ID"
  value = var.firebase_project_id
}
```

## Próximos Pasos

1. **Revisar documentación específica**:
   - `01-authN-authZ.md` - Autenticación y autorización
   - `02-implementation-plan-authN-authZ.md` - Plan de implementación

2. **Configurar Firebase** según la documentación de AuthN/AuthZ

3. **Implementar funcionalidades** siguiendo el plan detallado

4. **Testing** en ambiente local antes de deployment

---

**Nota**: Este proyecto utiliza pnpm como gestor de paquetes. Asegúrate de usar `pnpm` en lugar de `npm` o `yarn` para mantener consistencia con el lock file existente (`pnpm-lock.yaml`).
