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

### 1. Iniciar servidor de desarrollo
```bash
cd frontend/
pnpm dev
```

### 2. Acceder a la aplicación
- **Frontend**: http://localhost:3000
- **Firebase Emulators** (si están activos): http://localhost:4000

### 3. Hot Reload
- Los cambios en archivos `.tsx`, `.ts`, `.css` se reflejan automáticamente
- Turbopack acelera significativamente el hot reload

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
