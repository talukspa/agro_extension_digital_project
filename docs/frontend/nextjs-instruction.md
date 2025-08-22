# Next.js Frontend Setup Guide - Agro Extension Digital Project

## Introducción

Esta guía proporciona instrucciones detalladas para configurar, desarrollar y desplegar el frontend de Next.js del proyecto Agro Extension Digital. El proyecto utiliza una arquitectura moderna con **Next.js 15.4.6**, **Firebase Authentication**, **Firestore**, y despliega en **Google Cloud Run** usando **Terragrunt** para gestión de infraestructura.

## Información del Proyecto

- **Proyecto**: `agro-extension-digital-npe`
- **Database**: `agro-extension-db`
- **Framework**: Next.js 15.4.6 (App Router)
- **Package Manager**: pnpm
- **Infrastructure**: Terraform + Terragrunt
- **Deployment**: Google Cloud Run

## Requisitos Previos

### Herramientas Necesarias
```bash
# Verificar instalaciones
node --version        # v18+
pnpm --version        # v8+
firebase --version    # Firebase CLI
gcloud --version      # Google Cloud CLI
tf --version          # v1.5+
tterragrunt --version  # v0.50+
```

### Configuración Inicial
```bash
# Autenticación Google Cloud
gcloud auth login
gcloud auth application-default login
gcloud config set project agro-extension-digital-npe

# Login Firebase
firebase login
firebase use agro-extension-digital-npe
```

## 1. Setup del Proyecto

### 1.1 Instalación de Dependencias
```bash
# Navegar al directorio frontend
cd frontend/

# Instalar dependencias con pnpm
pnpm install

# Verificar instalación
pnpm list
```

### 1.2 Variables de Entorno
Crear `.env.local` en el directorio `frontend/`:

```bash
# Firebase Client Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=agro-extension-digital-npe.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=agro-extension-digital-npe
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=agro-extension-digital-npe.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# Firebase Server Configuration
FIREBASE_PROJECT_ID=agro-extension-digital-npe
FIREBASE_CLIENT_EMAIL=your_service_account_email
FIREBASE_PRIVATE_KEY=your_private_key

# Database
FIRESTORE_DATABASE_ID=agro-extension-db

# Environment
NODE_ENV=development
NEXT_PUBLIC_APP_ENV=development
```

## 2. Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/                    # App Router Next.js 15
│   │   ├── (auth)/            # Grupo de rutas: autenticación
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/       # Grupo de rutas: dashboard protegido
│   │   │   ├── admin/
│   │   │   ├── business/
│   │   │   ├── audit/
│   │   │   └── layout.tsx
│   │   ├── api/               # API Routes
│   │   │   ├── auth/
│   │   │   ├── admin/
│   │   │   ├── business/
│   │   │   └── audit/
│   │   ├── globals.css
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   ├── components/
│   │   ├── auth/              # Componentes de autenticación
│   │   ├── dashboard/         # Componentes del dashboard
│   │   ├── ui/                # Componentes UI reutilizables
│   │   └── layout/            # Componentes de layout
│   ├── contexts/
│   │   ├── AuthContext.tsx    # Context de autenticación
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useAuth.ts         # Hook de autenticación
│   │   └── index.ts
│   ├── lib/
│   │   ├── firebase/          # Configuración Firebase
│   │   │   ├── config.ts      # Cliente Firebase
│   │   │   ├── server.ts      # Firebase Admin
│   │   │   └── index.ts
│   │   └── utils.ts           # Utilidades generales
│   ├── types/
│   │   ├── auth.ts            # Tipos de autenticación
│   │   ├── user.ts            # Tipos de usuario
│   │   └── index.ts
│   └── middleware.ts          # Middleware de autenticación
├── public/
│   └── assets/
├── Dockerfile                 # Para Cloud Run
├── next.config.ts
├── package.json
├── pnpm-lock.yaml
└── tsconfig.json

cicd/                          # Infraestructura como Código
├── modules/
│   └── frontend/
│       ├── main.tf            # Recursos Cloud Run
│       ├── variables.tf
│       ├── outputs.tf
│       └── providers.tf
└── stacks/
    ├── common.yaml            # Config compartida
    ├── root.hcl              # Config base Terragrunt
    ├── dev/
    │   ├── env.yaml          # Variables DEV
    │   └── frontend/
    │       └── terragrunt.hcl
    └── prd/
        ├── env.yaml          # Variables PRD
        └── frontend/
            └── terragrunt.hcl
```

## 3. Configuración de Firebase

### 3.1 Configuración del Cliente
Actualizar `src/lib/firebase/config.ts`:

```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export default app;
```

### 3.2 Configuración del Servidor
Actualizar `src/lib/firebase/server.ts`:

```typescript
import { initializeApp, getApps, cert } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';

if (!getApps().length) {
  initializeApp({
    credential: cert({
      projectId: process.env.FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\n/g, '\n'),
    }),
    databaseURL: `https://${process.env.FIREBASE_PROJECT_ID}.firebaseio.com`,
  });
}

export const adminAuth = getAuth();
export const adminDb = getFirestore();
```

## 4. Scripts de Desarrollo

### 4.1 Scripts Disponibles
```bash
# Desarrollo con Turbopack (recomendado)
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

### 4.2 Configuración de package.json
Actualizar scripts en `package.json`:

```json
{
  "scripts": {
    "dev": "next dev --turbopack",
    "dev:standard": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "build:analyze": "ANALYZE=true next build"
  }
}
```

## 5. Gestión de Infraestructura

### 5.1 Validar Infraestructura
```bash
# Navegar al ambiente deseado
cd cicd/stacks/dev/frontend/

# Validar configuración
tterragrunt validate

# Planificar cambios
tterragrunt plan

# Aplicar infraestructura
tterragrunt apply
```

### 5.2 Variables por Ambiente

#### Desarrollo (dev/env.yaml)
```yaml
environment:
  name: "dev"
  log_level: "DEBUG"
  min_scale: 0      # Scale-to-zero habilitado
  max_scale: 10

resources:
  cpu: "1000m"
  memory: "512Mi"

project:
  id: "agro-extension-digital-npe"
```

#### Producción (prd/env.yaml)
```yaml
environment:
  name: "prd"
  log_level: "INFO"
  min_scale: 1      # Siempre activo
  max_scale: 100

resources:
  cpu: "2000m"
  memory: "1Gi"

project:
  id: "agro-extension-digital-npe"
```

## 6. Deployment a Cloud Run

### 6.1 Build y Push de Imagen
```bash
# Build de imagen Docker
docker build -t gcr.io/agro-extension-digital-npe/agent-frontend-app:latest .

# Push a Artifact Registry
docker push gcr.io/agro-extension-digital-npe/agent-frontend-app:latest
```

### 6.2 Deploy con Terragrunt
```bash
# La infraestructura ya configurada se encarga del deployment
cd cicd/stacks/dev/frontend/
tterragrunt apply

# Para producción
cd cicd/stacks/prd/frontend/
tterragrunt apply
```

### 6.3 Deploy Manual (Testing)
```bash
# Deploy directo para testing rápido
gcloud run deploy frontend-app-dev \
  --source . \
  --platform managed \
  --region us-central1 \
  --project agro-extension-digital-npe \
  --allow-unauthenticated
```

## 7. Configuración Next.js

### 7.1 next.config.ts
```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', 'agro-extension-digital-npe.run.app'],
    },
  },
  env: {
    FIREBASE_PROJECT_ID: process.env.FIREBASE_PROJECT_ID,
    FIRESTORE_DATABASE_ID: process.env.FIRESTORE_DATABASE_ID,
  },
  images: {
    domains: ['firebasestorage.googleapis.com'],
  },
  async headers() {
    return [
      {
        source: '/api/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type,Authorization' },
        ],
      },
    ];
  },
};

export default nextConfig;
```

## 8. Testing y Desarrollo Local

### 8.1 Desarrollo Local
```bash
# Iniciar servidor de desarrollo
cd frontend/
pnpm dev

# Acceder a la aplicación
# http://localhost:3000
```

### 8.2 Emuladores Firebase (Opcional)
```bash
# Iniciar emuladores para desarrollo
firebase emulators:start

# Solo Firestore
firebase emulators:start --only firestore

# Solo Authentication
firebase emulators:start --only auth
```

### 8.3 Testing de Build
```bash
# Crear build de producción
pnpm build

# Probar build localmente
pnpm start
```

## 9. Troubleshooting

### 9.1 Problemas con pnpm
```bash
# Limpiar cache
pnpm store prune

# Reinstalar dependencias
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### 9.2 Problemas con Firebase
```bash
# Verificar proyecto activo
firebase projects:list
firebase use agro-extension-digital-npe

# Revisar configuración
firebase firestore:rules:get
```

### 9.3 Problemas con Infraestructura
```bash
# Verificar estado
cd cicd/stacks/dev/frontend/
tterragrunt show

# Refrescar estado
tterragrunt refresh

# Limpiar cache Terragrunt
rm -rf .terragrunt-cache/
tterragrunt init
```

## 10. Próximos Pasos

1. **Implementar Autenticación**: Seguir la guía en `01-authN-authZ.md`
2. **Plan de Implementación**: Revisar `02-implementation-plan-authN-authZ.md`
3. **Configurar Firebase**: Setup completo según documentación
4. **Testing**: Validar funcionalidades en ambiente local
5. **Deployment**: Desplegar a desarrollo y posteriormente a producción

## Recursos Adicionales

- [Documentación Next.js 15](https://nextjs.org/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Terragrunt Documentation](https://terragrunt.gruntwork.io/docs/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)

---

**Nota**: Esta guía está sincronizada con la documentación completa en `docs/frontend/` y refleja la arquitectura actual del proyecto `agro-extension-digital-project`.

1. Initial Project Setup
First, create the Next.js application. The following command sets up a new project with TypeScript, Tailwind CSS, and ESLint pre-configured.

npx create-next-app@latest ciruelacertificada --typescript --tailwind --eslint
cd ciruelacertificada

For a better developer experience when working with Tailwind CSS class names, it's highly recommended to install clsx and tailwind-merge.

npm install clsx tailwind-merge

clsx: A tiny utility for constructing className strings conditionally.

tailwind-merge: A utility to intelligently merge Tailwind CSS classes in JS without style conflicts.

2. Scaffolding and Theming
We will now structure the project and apply a custom plum color theme. A well-organized structure is key to a maintainable application.

2.1. Project Structure
Organize your app directory using route groups to distinguish between different sections of your app. Route groups, denoted by parentheses (group), organize your routes without affecting the URL path.

ciruelacertificada/
├── app/
│   ├── (auth)/             # Routes for authentication (e.g., login)
│   ├── (main)/             # Protected main application routes
│   ├── api/
│   ├── components/
│   └── ...
├── lib/
│   └── ...
├── infra/
│   ├── modules/
│   │   └── app/            # Reusable Terraform module for the app
│   │       ├── main.tf
│   │       └── variables.tf
│   ├── envs/
│   │   ├── dev/
│   │   │   └── terragrunt.hcl
│   │   └── prod/
│   │       └── terragrunt.hcl
│   └── terragrunt.hcl      # Root Terragrunt configuration
├── .github/
│   └── workflows/
│       └── deploy.yml
└── ...

2.2. Plum Theme with Tailwind CSS
Configure Tailwind to use a rich, plum-based color palette for a unique and consistent look.

tailwind.config.ts

import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        plum: {
          '50': '#f4e6ff',
          '100': '#e9d0ff',
          '200': '#d8aeff',
          '300': '#c080ff',
          '400': '#a74fff',
          '500': '#8f2aff', // Base Plum
          '600': '#7f1bfa',
          '700': '#6b14e0',
          '800': '#5811b8', // Medium Plum
          '900': '#480f94', // Dark Plum
          '950': '#2c0667',
        },
        neutral: {
          '50': '#f8f9fa',
          '100': '#e9ecef',
          '200': '#dee2e6',
          '300': '#ced4da',
          '400': '#adb5bd',
          '500': '#6c757d',
          '600': '#495057',
          '700': '#343a40', // Dark Gray
          '800': '#212529',
          '900': '#1a1d20',
        },
      },
    },
  },
  plugins: [],
}
export default config

app/globals.css

@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-neutral-50 text-neutral-800;
}

3. Core File Implementations
The core application files remain the same as in the previous version (Layout, Providers, Pages, etc.).

4. Authentication with NextAuth.js
The authentication setup using NextAuth.js and the Firebase Adapter also remains unchanged.

5. Infrastructure with Terraform and Terragrunt
Using Terragrunt as a wrapper for Terraform allows us to define our infrastructure once and deploy it across multiple environments (dev, prod) with different configurations. This is a best practice for managing Infrastructure as Code (IaC).

5.1. Terraform Module (infra/modules/app)
First, we convert our Terraform code into a reusable module.

infra/modules/app/variables.tf

variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region for resources."
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "The name of the application."
  type        = string
  default     = "ciruelacertificada"
}

infra/modules/app/main.tf
This file now uses variables instead of hardcoded values.

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "apis" {
  # ... (same as before)
}

resource "google_firestore_database" "database" {
  project      = var.project_id
  # ... (same as before)
}

resource "google_artifact_registry_repository" "registry" {
  project       = var.project_id
  location      = var.region
  repository_id = "${var.app_name}-registry"
  # ... (same as before)
}

resource "google_cloud_run_v2_service" "app_service" {
  project  = var.project_id
  name     = "${var.app_name}-app"
  location = var.region
  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.registry.repository_id}/${var.app_name}-app:latest"
    }
  }
  # ... (same as before)
}

# ... (other resources)

5.2. Terragrunt Configuration
Now, we configure Terragrunt to use this module.

infra/terragrunt.hcl (Root Configuration)
This file defines settings shared across all environments, like the remote state backend. This keeps your code DRY (Don't Repeat Yourself).

remote_state {
  backend = "gcs"
  config = {
    bucket = "your-terraform-state-bucket" // CHANGE THIS to your GCS bucket name
    prefix = "${path_relative_to_include()}/terraform.tfstate"
  }
}

infra/envs/dev/terragrunt.hcl (Development Environment)
This file tells Terragrunt to use our module and provides the specific variable values for the dev environment.

include {
  path = find_in_parent_folders()
}

terraform {
  source = "../../modules/app"
}

inputs = {
  project_id = "your-dev-gcp-project-id"
  app_name   = "ciruelacertificada-dev"
  region     = "us-central1"
}

To deploy to dev, you would navigate to infra/envs/dev and run terragrunt apply. To deploy to prod, you would create a similar file in infra/envs/prod with production values and run the command from there.

6. CI/CD with GitHub Actions
The CI/CD pipeline remains conceptually the same, but it would typically be configured to deploy to the dev environment. You might add triggers to deploy to prod based on creating a new git tag or merging to a release branch.

7. Refactoring an Existing Project
The prompt for refactoring is updated to include the new IaC structure.

Prompt for AI Code Refactoring
Role: You are an expert full-stack developer specializing in Next.js, Google Cloud, and modern architectural patterns.

Context: I will provide you with the complete codebase for an existing Next.js project.

Task: Your task is to analyze the provided codebase and refactor it to match the target architecture defined below. Do not use fallbacks; apply the new structure directly, migrating existing logic and features as needed.

Target Architecture
Project Structure: Reorganize the file system to use Next.js App Router with route groups ((auth), (main)).

Styling: Implement Tailwind CSS using the provided "plum" and "neutral" color palette.

Authentication: Refactor the authentication system to use NextAuth.js with the FirebaseAdapter.

Infrastructure & CI/CD: Generate the necessary infrastructure files using Terraform and Terragrunt. The structure should include a reusable Terraform module for the application and separate dev/prod environment configurations under envs/. Generate a corresponding GitHub Actions workflow for deployment. Ensure all placeholders are configured for the "ciruelacertificada" application.

Final Output Instructions:
Provide the complete, refactored codebase as a series of files. For each file, specify its full path. Start your response with a brief summary of the key changes you made based on your analysis of the original code.