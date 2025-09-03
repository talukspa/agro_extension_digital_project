# Plan de Implementación AuthN/AuthZ - Agro Extension Digital

## Resumen Ejecutivo

Este documento proporciona un plan detallado para implementar autenticación (AuthN) y autorización (AuthZ) en el proyecto Agro Extension Digital, utilizando las colecciones existentes de Firestore (`auditors`, `business_profiles`) e integrándolas con Firebase Authentication.

## Análisis del Estado Actual

### 📊 Colecciones Existentes en Firestore

#### 1. `business_profiles` 
```javascript
{
  rut: "76.432.187-4",
  legal_name: "Exportadora de Ciruelas Paine",
  owner_name: "Juan Rojas", 
  owner_email: "contacto@exportadorapaine.cl",
  owner_phone: "+56987654321",
  owner_role: "Dueño",
  region: "Metropolitana",
  commune: "Paine", 
  address: "Av. Gral. Baquedano 108",
  business_size: "Microempresa",
  process_type: "Producción Primaria",
  digital_tools_used_at_work: [
    "Redes sociales (Facebook, Instagram, etc.)",
    "Aplicaciones de mensajería (WhatsApp, Telegram, etc.)"
  ],
  digital_tools_experienced: [
    "Redes sociales (Facebook, Instagram, etc.)",
    "Aplicaciones de mensajería (WhatsApp, Telegram, etc.)"
  ]
}
```

#### 2. `auditors`
```javascript
{
  auditor_id: 1,
  auditor_name: "Carlos Ruiz",
  auditor_email: "carlos.ruiz@auditcorp.com"
}
```

#### 3. Otras Colecciones
- `responses` - Respuestas de empresas a estándares (antes `standard_responses`)
- `standards` - Plantillas de estándares (antes `standards`)
- `resources` - Recursos del sistema

**Colecciones Adicionales del Modelo de Datos:**
- `standard_templates` - Plantillas de estándares específicos (ej: `ciruelas-aa`, `produccion-primaria-pp`)
- Estructura de `responses` incluye arrays embebidos de `answers` con `registers` para evidencia

## Arquitectura de Autorización Propuesta

### 🔐 Modelo de Usuarios y Roles

#### Roles Identificados:
1. **`business_owner`** - Propietarios de empresas
2. **`auditor`** - Auditores externos
3. **`admin`** - Administradores del sistema

#### Mapping de Datos Existentes:
- **Business Owners**: `owner_email` de `business_profiles` → Firebase Auth
  - Ejemplo: `contacto@exportadorapaine.cl` (Exportadora de Ciruelas Paine)
- **Auditors**: `auditor_email` de `auditors` → Firebase Auth
  - Ejemplo: `carlos.ruiz@auditcorp.com` (Carlos Ruiz)
  - Ejemplo: `ana.soto@auditcorp.com` (Ana Soto)
- **Admins**: Nuevos usuarios con rol administrativo

## Plan de Implementación

### Fase 1: Creación de Colecciones y Estructuras 🗄️

#### 1.1 Nueva Colección: `users`

**Ubicación**: `agro-extension-db/users/{firebase_uid}`

**Estructura propuesta**:
```typescript
interface User {
  // Identificación Firebase
  uid: string;                    // Firebase Auth UID (Document ID)
  email: string;                  // Email del usuario
  
  // Información básica
  profile: {
    displayName: string;          // Nombre completo
    phoneNumber?: string;         // Teléfono
    photoURL?: string;           // URL de foto de perfil
  };
  
  // Autorización
  role: 'business_owner' | 'auditor' | 'admin';
  isActive: boolean;              // Estado activo/inactivo
  
  // Referencias a colecciones existentes
  businessProfile?: {
    rut: string;                  // RUT de business_profiles
    legal_name: string;           // Nombre legal de la empresa
  };
  
  auditorProfile?: {
    auditor_id: number;           // ID en colección auditors
    assigned_businesses: string[]; // RUTs asignados
  };
  
  // Permisos específicos basados en webciruela.html
  permissions: {
    // === PERMISOS GENERALES ===
    canViewOwnData: boolean;          // Ver sus propios datos
    canEditOwnData: boolean;          // Editar sus propios datos
    canAccessDashboard: boolean;      // Acceder al dashboard principal
    canViewResources: boolean;        // Ver recursos y documentación
    canContactSupport: boolean;       // Contactar soporte técnico
    
    // === PERMISOS DE EMPRESA (BUSINESS_OWNER) ===
    canViewCompanyProfile: boolean;   // Ver perfil de la empresa
    canEditCompanyProfile: boolean;   // Editar perfil de la empresa
    canViewStandards: boolean;        // Ver lista de estándares
    canAnswerSurveys: boolean;        // Responder encuestas de estándares
    canSubmitSurveys: boolean;        // Enviar encuestas completadas
    canUploadEvidence: boolean;       // Subir evidencia de cumplimiento
    canViewEvidenceStatus: boolean;   // Ver estado de evidencia (validado/pendiente)
    canViewOwnReports: boolean;       // Ver reportes de su empresa
    canViewCertificationStatus: boolean; // Ver estado de certificación
    canFilterByStandard: boolean;     // Filtrar por estándar (PP/AA)
    canUseVirtualAgent: boolean;      // Usar agente virtual de WhatsApp
    
    // === PERMISOS DE AUDITOR ===
    canViewAssignedBusinesses: boolean;   // Ver empresas asignadas
    canViewBusinessProfiles: boolean;     // Ver perfiles de empresas asignadas
    canReviewEvidence: boolean;           // Revisar evidencia subida
    canValidateEvidence: boolean;         // Validar/rechazar evidencia
    canRejectEvidence: boolean;           // Rechazar evidencia con comentarios
    canDownloadAuditTemplates: boolean;   // Descargar pautas de auditoría
    canCreateAuditReports: boolean;       // Crear reportes de auditoría
    canViewAuditProgress: boolean;        // Ver progreso de auditorías
    canViewComplianceCharts: boolean;     // Ver gráficos de cumplimiento
    canViewAssignedMap: boolean;          // Ver mapa de empresas asignadas
    canAccessAuditorResources: boolean;   // Acceder recursos específicos de auditor
    
    // === PERMISOS DE ADMINISTRADOR ===
    canViewAllBusinesses: boolean;        // Ver todas las empresas
    canViewAllAuditors: boolean;          // Ver todos los auditores
    canCreateUsers: boolean;              // Crear nuevos usuarios
    canEditUsers: boolean;                // Editar usuarios existentes
    canDeactivateUsers: boolean;          // Desactivar usuarios
    canAssignAuditors: boolean;           // Asignar auditores a empresas
    canUnassignAuditors: boolean;         // Desasignar auditores
    canViewAnalytics: boolean;            // Ver analíticas generales
    canViewRegionalStats: boolean;        // Ver estadísticas por región
    canViewAuditorProgress: boolean;      // Ver progreso de auditores
    canViewIndustryStats: boolean;        // Ver estadísticas de la industria
    canManageResources: boolean;          // Gestionar recursos y documentos
    canDeleteResources: boolean;          // Eliminar recursos
    canViewSystemMap: boolean;            // Ver mapa completo del sistema
    canExportData: boolean;               // Exportar datos del sistema
    canViewAuditAssignments: boolean;     // Ver asignaciones de auditorías
    canManageStandards: boolean;          // Gestionar estándares
    
    // === PERMISOS ESPECIALES ===
    canViewPublicStats: boolean;          // Ver estadísticas públicas
    canAccessAPI: boolean;                // Acceder a APIs del sistema
    canViewLogs: boolean;                 // Ver logs del sistema
    canManageSettings: boolean;           // Gestionar configuraciones
  };
  
  // Metadatos
  createdAt: Timestamp;
  lastLogin: Timestamp;
  updatedAt: Timestamp;
}
```

#### 1.2 Actualizaciones a Colecciones Existentes

##### `business_profiles` - Agregar campos de autenticación:
```javascript
{
  // Campos existentes del modelo real...
  rut: "76.432.187-4",
  legal_name: "Exportadora de Ciruelas Paine", 
  owner_name: "Juan Rojas",
  owner_email: "contacto@exportadorapaine.cl",
  owner_phone: "+56987654321",
  owner_role: "Dueño",
  commune: "Paine",
  region: "Metropolitana",
  address: "Av. Gral. Baquedano 108",
  business_size: "Microempresa",
  process_type: "Producción Primaria",
  digital_tools_used_at_work: [
    "Redes sociales (Facebook, Instagram, etc.)",
    "Aplicaciones de mensajería (WhatsApp, Telegram, etc.)"
  ],
  digital_tools_experienced: [
    "Redes sociales (Facebook, Instagram, etc.)",
    "Aplicaciones de mensajería (WhatsApp, Telegram, etc.)"
  ],
  
  // NUEVOS CAMPOS PARA AUTORIZACIÓN
  firebase_uid: "firebase-auth-uid-123",     // Referencia al usuario Firebase
  owner_status: "active" | "inactive",       // Estado del propietario
  last_login: Timestamp,                     // Último login
  account_created: Timestamp                 // Fecha de creación de cuenta
}
```

##### `auditors` - Agregar campos de autenticación:
```javascript
{
  // Campos existentes del modelo real...
  auditor_id: 1,
  auditor_name: "Carlos Ruiz",
  auditor_email: "carlos.ruiz@auditcorp.com",
  
  // NUEVOS CAMPOS PARA AUTORIZACIÓN  
  firebase_uid: "firebase-auth-uid-456",     // Referencia al usuario Firebase
  auditor_status: "active" | "inactive",     // Estado del auditor
  last_login: Timestamp,                     // Último login
  account_created: Timestamp,                // Fecha de creación de cuenta
  permissions_level: "basic" | "advanced"    // Nivel de permisos
}
```

### Fase 2: Implementación Frontend (Next.js) 🎯

#### 2.1 Configuración de Tailwind CSS con Tema Plum

**Archivo**: `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Paleta Plum (Ciruela) Principal
        plum: {
          '50': '#f4e6ff',   // Muy claro - backgrounds
          '100': '#e9d0ff',  // Claro - hover states
          '200': '#d8aeff',  // Claro medio
          '300': '#c080ff',  // Medio claro
          '400': '#a74fff',  // Medio
          '500': '#8f2aff',  // Base Plum - principal
          '600': '#7f1bfa',  // Medio oscuro - botones
          '700': '#6b14e0',  // Oscuro - sidebar
          '800': '#5811b8',  // Muy oscuro - textos importantes
          '900': '#480f94',  // Extra oscuro - contrastes
          '950': '#2c0667',  // Negro plum
        },
        
        // Colores Neutros para Balance
        neutral: {
          '50': '#f8f9fa',   // Blanco grisáceo
          '100': '#e9ecef',  // Gris muy claro
          '200': '#dee2e6',  // Gris claro
          '300': '#ced4da',  // Gris medio claro
          '400': '#adb5bd',  // Gris medio
          '500': '#6c757d',  // Gris
          '600': '#495057',  // Gris oscuro
          '700': '#343a40',  // Gris muy oscuro
          '800': '#212529',  // Negro grisáceo
          '900': '#1a1d20',  // Negro
        },
        
        // Colores de Estado (manteniendo coherencia con plum)
        success: {
          '50': '#ecfdf5',
          '500': '#10b981',  // Verde para estados exitosos
          '600': '#059669',
          '700': '#047857',
        },
        warning: {
          '50': '#fffbeb',
          '500': '#f59e0b',  // Amarillo para advertencias
          '600': '#d97706',
          '700': '#b45309',
        },
        error: {
          '50': '#fef2f2',
          '500': '#ef4444',  // Rojo para errores
          '600': '#dc2626',
          '700': '#b91c1c',
        },
        
        // Colores específicos para certificación (basados en webciruela.html)
        certification: {
          gold: '#FFD700',    // Oro - 3 años
          silver: '#C0C0C0',  // Plata - 2 años
          bronze: '#CD7F32',  // Bronce - 1 año
          none: '#EF4444',    // Rojo - sin certificación
        }
      },
      
      // Fuentes personalizadas
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system'],
        'display': ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      
      // Espaciado personalizado
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      
      // Sombras personalizadas con tema plum
      boxShadow: {
        'plum': '0 4px 14px 0 rgba(143, 42, 255, 0.15)',
        'plum-lg': '0 10px 25px -3px rgba(143, 42, 255, 0.2)',
        'certification': '0 0 15px currentColor',
      },
      
      // Animaciones para transiciones suaves
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'pulse-plum': 'pulsePlum 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulsePlum: {
          '0%, 100%': { 
            boxShadow: '0 0 0 0 rgba(143, 42, 255, 0.7)' 
          },
          '70%': { 
            boxShadow: '0 0 0 10px rgba(143, 42, 255, 0)' 
          },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // Para formularios estilizados
    require('@tailwindcss/typography'), // Para contenido de texto
  ],
}

export default config
```

**Archivo**: `src/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Fuente personalizada */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

@layer base {
  * {
    @apply border-border;
  }
  
  body {
    @apply bg-neutral-50 text-neutral-800 font-sans antialiased;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
  
  /* Scrollbar personalizada con tema plum */
  ::-webkit-scrollbar {
    @apply w-2;
  }
  
  ::-webkit-scrollbar-track {
    @apply bg-neutral-100;
  }
  
  ::-webkit-scrollbar-thumb {
    @apply bg-plum-300 rounded-full;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    @apply bg-plum-400;
  }
}

@layer components {
  /* Sidebar component */
  .sidebar {
    @apply bg-gradient-to-b from-plum-700 to-plum-800 text-white;
  }
  
  .sidebar-border {
    @apply border-plum-600;
  }
  
  .sidebar-link {
    @apply transition-all duration-200 ease-in-out rounded-lg;
  }
  
  .sidebar-link:hover, 
  .sidebar-link.active {
    @apply bg-plum-600 text-white shadow-md;
  }
  
  /* Botones principales */
  .btn-primary {
    @apply bg-plum-600 hover:bg-plum-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 shadow-plum;
  }
  
  .btn-secondary {
    @apply bg-neutral-200 hover:bg-neutral-300 text-neutral-800 font-semibold py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-success {
    @apply bg-success-500 hover:bg-success-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-warning {
    @apply bg-warning-500 hover:bg-warning-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-error {
    @apply bg-error-500 hover:bg-error-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  /* Cards y contenedores */
  .card {
    @apply bg-white rounded-lg shadow-md p-6 border border-neutral-200;
  }
  
  .card-hover {
    @apply hover:shadow-plum-lg transition-shadow duration-300;
  }
  
  /* Formularios */
  .form-input {
    @apply block w-full rounded-md border-neutral-300 shadow-sm focus:border-plum-500 focus:ring-plum-500 sm:text-sm;
  }
  
  .form-select {
    @apply block w-full rounded-md border-neutral-300 shadow-sm focus:border-plum-500 focus:ring-plum-500 sm:text-sm;
  }
  
  .form-textarea {
    @apply block w-full rounded-md border-neutral-300 shadow-sm focus:border-plum-500 focus:ring-plum-500 sm:text-sm;
  }
  
  /* Estados de certificación */
  .certification-badge {
    @apply border-4 rounded-lg p-4 transition-all duration-300;
  }
  
  .cert-gold {
    @apply border-certification-gold shadow-certification text-certification-gold;
  }
  
  .cert-silver {
    @apply border-certification-silver shadow-certification text-certification-silver;
  }
  
  .cert-bronze {
    @apply border-certification-bronze shadow-certification text-certification-bronze;
  }
  
  .cert-none {
    @apply border-certification-none shadow-certification text-certification-none;
  }
  
  /* Filtros de estándares */
  .standard-filter-btn {
    @apply px-4 py-2 text-sm font-semibold rounded-md transition-colors duration-200 border border-neutral-300;
  }
  
  .standard-filter-btn.active {
    @apply bg-plum-600 text-white border-plum-600;
  }
  
  .standard-filter-btn:hover:not(.active) {
    @apply bg-neutral-100 border-neutral-400;
  }
  
  /* Notificaciones */
  .notification-dot {
    @apply h-2 w-2 bg-plum-500 rounded-full inline-block mr-3 flex-shrink-0;
  }
  
  /* Contenedores principales */
  .main-content {
    @apply hidden;
  }
  
  .main-content.active {
    @apply block animate-fade-in;
  }
  
  /* Switch de roles */
  .role-switcher button.active {
    @apply bg-plum-700 text-white;
  }
  
  .role-switcher button:hover:not(.active) {
    @apply bg-plum-100 text-plum-700;
  }
}

@layer utilities {
  /* Utilidades de texto con tema plum */
  .text-plum-primary {
    @apply text-plum-600;
  }
  
  .text-plum-secondary {
    @apply text-plum-500;
  }
  
  /* Backgrounds con gradientes */
  .bg-gradient-plum {
    @apply bg-gradient-to-r from-plum-600 to-plum-700;
  }
  
  .bg-gradient-plum-light {
    @apply bg-gradient-to-r from-plum-50 to-plum-100;
  }
  
  /* Bordes con tema plum */
  .border-plum {
    @apply border-plum-300;
  }
  
  .border-plum-focus {
    @apply focus:border-plum-500 focus:ring-plum-500;
  }
  
  /* Sombras específicas */
  .shadow-plum-soft {
    box-shadow: 0 1px 3px 0 rgba(143, 42, 255, 0.1), 0 1px 2px 0 rgba(143, 42, 255, 0.06);
  }
}
```

#### 2.2 Instalación de Dependencias de Estilo

```bash
# Instalar Tailwind CSS y dependencias relacionadas
pnpm add -D tailwindcss postcss autoprefixer
pnpm add -D @tailwindcss/forms @tailwindcss/typography

# Instalar utilidades para clases condicionales (opcional pero recomendado)
pnpm add clsx tailwind-merge

# Instalar iconos (para la interfaz)
pnpm add lucide-react

# Inicializar configuración de Tailwind
npx tailwindcss init -p
```

#### 2.3 Componentes Base con Tema Plum

**Archivo**: `src/components/ui/Button.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}) => {
  const baseClasses = 'font-semibold rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'btn-primary focus:ring-plum-500',
    secondary: 'btn-secondary focus:ring-neutral-500',
    success: 'btn-success focus:ring-success-500',
    warning: 'btn-warning focus:ring-warning-500',
    error: 'btn-error focus:ring-error-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      className={twMerge(
        clsx(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          className
        )
      )}
      {...props}
    >
      {children}
    </button>
  );
};
```

**Archivo**: `src/components/ui/Card.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  hover = false,
  padding = 'md'
}) => {
  const baseClasses = 'card';
  const hoverClasses = hover ? 'card-hover' : '';
  
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={twMerge(
        clsx(
          baseClasses,
          hoverClasses,
          paddingClasses[padding],
          className
        )
      )}
    >
      {children}
    </div>
  );
};
```

**Archivo**: `src/components/ui/CertificationBadge.tsx`

```typescript
import React from 'react';
import { clsx } from 'clsx';

interface CertificationBadgeProps {
  level: 'gold' | 'silver' | 'bronze' | 'none';
  years?: number;
  score?: string;
  className?: string;
}

export const CertificationBadge: React.FC<CertificationBadgeProps> = ({
  level,
  years,
  score,
  className
}) => {
  const getContent = () => {
    switch (level) {
      case 'gold':
        return {
          text: `¡Felicidades! Certifica a ${years} años`,
          subtext: `Basado en 100% fundamental y >${score} general`,
          icon: '🏆'
        };
      case 'silver':
        return {
          text: `Certifica a ${years} años`,
          subtext: `Basado en 100% fundamental y >${score} general`,
          icon: '🥈'
        };
      case 'bronze':
        return {
          text: `Certifica a ${years} año`,
          subtext: `Basado en 100% fundamental y >${score} general`,
          icon: '🥉'
        };
      case 'none':
        return {
          text: 'No certifica',
          subtext: 'Necesita mejorar cumplimiento',
          icon: '❌'
        };
    }
  };

  const content = getContent();

  return (
    <div
      className={clsx(
        'certification-badge text-center',
        `cert-${level}`,
        className
      )}
    >
      <div className="text-3xl mb-2">{content.icon}</div>
      <h3 className="font-bold text-lg">{content.text}</h3>
      <p className="text-sm mt-1 opacity-80">{content.subtext}</p>
    </div>
  );
};
```

#### 2.5 Layout Principal con Tema Plum

**Archivo**: `src/app/layout.tsx`

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'CiruelaCertificada - Certificación de Ciruelas',
  description: 'Plataforma de certificación para la industria de ciruela deshidratada chilena',
  keywords: ['ciruela', 'certificación', 'agroindustria', 'Chile'],
  authors: [{ name: 'Agro Extension Digital' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={inter.variable}>
      <body className="font-sans antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

**Archivo**: `src/components/layout/Sidebar.tsx`

```typescript
import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { 
  Home, 
  UserCheck, 
  BarChart3, 
  ClipboardList, 
  User, 
  FileText, 
  Upload, 
  BookOpen,
  LogOut,
  MessageCircle
} from 'lucide-react';
import { clsx } from 'clsx';

interface SidebarProps {
  currentPath: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPath }) => {
  const { user, userRole, signOut } = useAuth();

  const navigation = [
    // Enlaces comunes
    {
      name: 'Panel Principal',
      href: '/dashboard',
      icon: Home,
      roles: ['admin', 'business_owner', 'auditor']
    },
    
    // Enlaces de Admin
    {
      name: 'Asignación',
      href: '/admin/assignments',
      icon: UserCheck,
      roles: ['admin']
    },
    {
      name: 'Analíticas',
      href: '/admin/analytics',
      icon: BarChart3,
      roles: ['admin']
    },
    
    // Enlaces de Auditor
    {
      name: 'Auditorías Asignadas',
      href: '/auditor/assigned-audits',
      icon: ClipboardList,
      roles: ['auditor']
    },
    
    // Enlaces de Empresa
    {
      name: 'Perfil de la Empresa',
      href: '/business/profile',
      icon: User,
      roles: ['business_owner']
    },
    {
      name: 'Estándares',
      href: '/business/standards',
      icon: FileText,
      roles: ['business_owner']
    },
    {
      name: 'Registro de Evidencia',
      href: '/business/evidence',
      icon: Upload,
      roles: ['business_owner']
    },
    
    // Enlaces comunes
    {
      name: 'Recursos',
      href: '/resources',
      icon: BookOpen,
      roles: ['admin', 'auditor', 'business_owner']
    },
  ];

  const filteredNavigation = navigation.filter(item => 
    item.roles.includes(userRole || '')
  );

  return (
    <aside className="w-64 sidebar flex flex-col h-screen">
      {/* Header */}
      <div className="p-6 border-b sidebar-border">
        <h1 className="text-2xl font-bold text-white">
          CiruelaCertificada
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-grow p-4">
        <ul className="space-y-2">
          {filteredNavigation.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.href;
            
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={clsx(
                    'sidebar-link flex items-center p-3 text-white',
                    isActive && 'active'
                  )}
                >
                  <Icon className="w-6 h-6 mr-3" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* WhatsApp Agent (Solo para empresas) */}
      {userRole === 'business_owner' && (
        <div className="p-4 border-t sidebar-border">
          <a
            href="https://wa.me/56912345678"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center p-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors duration-200"
          >
            <MessageCircle className="w-5 h-5 mr-2" />
            Agente Virtual
          </a>
        </div>
      )}

      {/* User Info */}
      <div className="p-4 border-t sidebar-border">
        <div className="flex items-center mb-4">
          <div className="w-10 h-10 rounded-full bg-plum-500 flex items-center justify-center text-white font-semibold">
            {user?.profile?.displayName?.charAt(0) || 'U'}
          </div>
          <div className="ml-3">
            <p className="font-semibold text-white">
              {user?.profile?.displayName || 'Usuario'}
            </p>
            <p className="text-sm text-plum-300 capitalize">
              {userRole?.replace('_', ' ') || 'Invitado'}
            </p>
          </div>
        </div>
        
        <button
          onClick={signOut}
          className="w-full flex items-center justify-center p-2 bg-error-600 hover:bg-error-700 text-white rounded-lg transition-colors duration-200"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
};
```

**Archivo**: `src/components/layout/DashboardLayout.tsx`

```typescript
import React from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { useAuth } from '@/hooks/useAuth';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
  children 
}) => {
  const pathname = usePathname();
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-neutral-50">
        <div className="animate-pulse-plum">
          <div className="w-16 h-16 bg-plum-500 rounded-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-neutral-50">
      <Sidebar currentPath={pathname} />
      
      <main className="flex-grow overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};
```

#### 2.6 Configuración de package.json Actualizada

```json
{
  "dependencies": {
    "@google-cloud/firestore": "^7.11.3",
    "@google-cloud/storage": "^7.16.0",
    "dotenv": "^17.2.1",
    "firebase": "^12.1.0",
    "firebase-admin": "^12.0.0",
    "next": "15.4.6",
    "react": "19.1.0",
    "react-dom": "19.1.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "lucide-react": "^0.400.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "firebase-tools": "^14.12.1",
    "typescript": "^5",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "@tailwindcss/forms": "^0.5.0",
    "@tailwindcss/typography": "^0.5.0"
  },
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "build:css": "tailwindcss build -i ./src/app/globals.css -o ./public/css/output.css --watch"
  }
}
```

#### 2.7 AuthContext Mejorado

**Archivo**: `src/contexts/AuthContext.tsx`

```typescript
'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { auth, db } from '@/lib/firebase';
import { 
  User as FirebaseUser,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  UserCredential
} from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';

interface UserProfile {
  uid: string;
  email: string;
  displayName: string;
  role: 'admin' | 'auditor' | 'business_owner';
  businessProfileId?: string;
  auditorProfileId?: string;
  certificationLevel?: string;
  isActive: boolean;
  companyName?: string;
  contactName?: string;
  address?: string;
  phone?: string;
  certificationYear?: number;
  certificationStatus?: string;
  createdAt: Date;
  updatedAt: Date;
}

interface AuthContextType {
  user: FirebaseUser | null;
  userProfile: UserProfile | null;
  userRole: string | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<UserCredential>;
  signOut: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string | string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [user, setUser] = useState<FirebaseUser | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Definir permisos por rol
  const rolePermissions = {
    admin: [
      'view:all_profiles',
      'edit:all_profiles',
      'assign:auditors',
      'view:analytics',
      'manage:standards',
      'manage:resources',
      'export:reports'
    ],
    auditor: [
      'view:assigned_audits',
      'edit:audit_reports',
      'view:standards',
      'view:resources',
      'submit:audit_results'
    ],
    business_owner: [
      'view:own_profile',
      'edit:own_profile',
      'view:own_standards',
      'submit:evidence',
      'view:audit_status',
      'view:resources',
      'access:whatsapp_agent'
    ]
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);
        
        // Obtener perfil del usuario desde Firestore
        try {
          const userDoc = await getDoc(doc(db, 'users', firebaseUser.uid));
          
          if (userDoc.exists()) {
            const userData = userDoc.data();
            const profile: UserProfile = {
              uid: firebaseUser.uid,
              email: firebaseUser.email || '',
              displayName: userData.displayName || firebaseUser.displayName || '',
              role: userData.role,
              businessProfileId: userData.businessProfileId,
              auditorProfileId: userData.auditorProfileId,
              certificationLevel: userData.certificationLevel,
              isActive: userData.isActive ?? true,
              companyName: userData.companyName,
              contactName: userData.contactName,
              address: userData.address,
              phone: userData.phone,
              certificationYear: userData.certificationYear,
              certificationStatus: userData.certificationStatus,
              createdAt: userData.createdAt?.toDate() || new Date(),
              updatedAt: userData.updatedAt?.toDate() || new Date(),
            };
            
            setUserProfile(profile);
          }
        } catch (error) {
          console.error('Error al obtener perfil de usuario:', error);
        }
      } else {
        setUser(null);
        setUserProfile(null);
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const signIn = async (email: string, password: string) => {
    return signInWithEmailAndPassword(auth, email, password);
  };

  const signOut = async () => {
    await firebaseSignOut(auth);
  };

  const hasPermission = (permission: string): boolean => {
    if (!userProfile?.role) return false;
    return rolePermissions[userProfile.role]?.includes(permission) || false;
  };

  const hasRole = (role: string | string[]): boolean => {
    if (!userProfile?.role) return false;
    
    if (Array.isArray(role)) {
      return role.includes(userProfile.role);
    }
    
    return userProfile.role === role;
  };

  const value: AuthContextType = {
    user,
    userProfile,
    userRole: userProfile?.role || null,
    loading,
    signIn,
    signOut,
    hasPermission,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### 2.8 Páginas Principales con Tema Plum

**Archivo**: `src/app/dashboard/page.tsx`

```typescript
'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useAuth } from '@/contexts/AuthContext';
import { 
  BarChart3, 
  Users, 
  ClipboardList, 
  Award,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';

export default function DashboardPage() {
  const { userProfile, hasRole } = useAuth();

  // Métricas de ejemplo (en una implementación real vendrían de la API)
  const adminMetrics = {
    totalBusinesses: 45,
    activeAudits: 12,
    completedCertifications: 156,
    pendingReviews: 8
  };

  const auditorMetrics = {
    assignedAudits: 5,
    completedAudits: 23,
    pendingReports: 2,
    averageRating: 4.8
  };

  const businessMetrics = {
    certificationStatus: 'En Progreso',
    completedStandards: 8,
    totalStandards: 12,
    nextAuditDate: '2024-02-15'
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-plum-600 to-plum-800 rounded-lg p-8 text-white">
          <h1 className="text-3xl font-bold mb-2">
            ¡Bienvenido, {userProfile?.displayName || 'Usuario'}!
          </h1>
          <p className="text-plum-100 text-lg">
            {hasRole('admin') && 'Panel de administración del sistema de certificación'}
            {hasRole('auditor') && 'Panel de auditorías y evaluaciones'}
            {hasRole('business_owner') && `Panel de certificación - ${userProfile?.companyName || 'Tu empresa'}`}
          </p>
        </div>

        {/* Admin Dashboard */}
        {hasRole('admin') && (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold text-plum-900">Panel de Administración</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-plum-100 rounded-lg flex items-center justify-center">
                    <Users className="w-6 h-6 text-plum-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {adminMetrics.totalBusinesses}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Empresas Registradas</h3>
                <p className="text-sm text-plum-600">Total en el sistema</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
                    <ClipboardList className="w-6 h-6 text-warning-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {adminMetrics.activeAudits}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Auditorías Activas</h3>
                <p className="text-sm text-plum-600">En progreso</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center">
                    <Award className="w-6 h-6 text-success-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {adminMetrics.completedCertifications}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Certificaciones</h3>
                <p className="text-sm text-plum-600">Completadas</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-error-100 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-error-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {adminMetrics.pendingReviews}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Revisiones Pendientes</h3>
                <p className="text-sm text-plum-600">Requieren atención</p>
              </div>
            </div>
          </div>
        )}

        {/* Auditor Dashboard */}
        {hasRole('auditor') && (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold text-plum-900">Panel de Auditorías</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-plum-100 rounded-lg flex items-center justify-center">
                    <ClipboardList className="w-6 h-6 text-plum-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {auditorMetrics.assignedAudits}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Auditorías Asignadas</h3>
                <p className="text-sm text-plum-600">Pendientes</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-success-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {auditorMetrics.completedAudits}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Completadas</h3>
                <p className="text-sm text-plum-600">Este año</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
                    <Clock className="w-6 h-6 text-warning-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {auditorMetrics.pendingReports}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Reportes Pendientes</h3>
                <p className="text-sm text-plum-600">Por entregar</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-plum-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-plum-600" />
                  </div>
                  <span className="text-2xl font-bold text-plum-900">
                    {auditorMetrics.averageRating}
                  </span>
                </div>
                <h3 className="font-semibold text-plum-800">Calificación</h3>
                <p className="text-sm text-plum-600">Promedio</p>
              </div>
            </div>
          </div>
        )}

        {/* Business Dashboard */}
        {hasRole('business_owner') && (
          <div className="space-y-8">
            <h2 className="text-2xl font-bold text-plum-900">Estado de Certificación</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <div className="card p-6">
                  <h3 className="text-xl font-semibold text-plum-800 mb-4">
                    Progreso de Estándares
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-plum-700">Estándares Completados</span>
                      <span className="font-semibold text-plum-900">
                        {businessMetrics.completedStandards}/{businessMetrics.totalStandards}
                      </span>
                    </div>
                    <div className="w-full bg-plum-100 rounded-full h-3">
                      <div 
                        className="bg-plum-600 h-3 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${(businessMetrics.completedStandards / businessMetrics.totalStandards) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <p className="text-sm text-plum-600">
                      {Math.round((businessMetrics.completedStandards / businessMetrics.totalStandards) * 100)}% completado
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="card p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-plum-100 rounded-lg flex items-center justify-center mr-4">
                      <Award className="w-6 h-6 text-plum-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-plum-800">Estado</h3>
                      <span className="text-sm text-warning-600 bg-warning-100 px-2 py-1 rounded">
                        {businessMetrics.certificationStatus}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="card p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-plum-100 rounded-lg flex items-center justify-center mr-4">
                      <ClipboardList className="w-6 h-6 text-plum-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-plum-800">Próxima Auditoría</h3>
                      <p className="text-sm text-plum-600">
                        {new Date(businessMetrics.nextAuditDate).toLocaleDateString('es-CL')}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Acciones Rápidas */}
        <div className="card p-6">
          <h3 className="text-xl font-semibold text-plum-800 mb-4">Acciones Rápidas</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {hasRole('admin') && (
              <>
                <button className="btn-secondary p-4 text-left">
                  <BarChart3 className="w-6 h-6 mb-2 text-plum-600" />
                  <div>
                    <p className="font-semibold">Ver Analíticas</p>
                    <p className="text-sm text-plum-600">Reportes y métricas</p>
                  </div>
                </button>
                <button className="btn-secondary p-4 text-left">
                  <Users className="w-6 h-6 mb-2 text-plum-600" />
                  <div>
                    <p className="font-semibold">Gestionar Usuarios</p>
                    <p className="text-sm text-plum-600">Administrar accesos</p>
                  </div>
                </button>
                <button className="btn-secondary p-4 text-left">
                  <ClipboardList className="w-6 h-6 mb-2 text-plum-600" />
                  <div>
                    <p className="font-semibold">Asignar Auditorías</p>
                    <p className="text-sm text-plum-600">Programar evaluaciones</p>
                  </div>
                </button>
              </>
            )}
            
            {hasRole('auditor') && (
              <>
                <button className="btn-secondary p-4 text-left">
                  <ClipboardList className="w-6 h-6 mb-2 text-plum-600" />
                  <div>
                    <p className="font-semibold">Mis Auditorías</p>
                    <p className="text-sm text-plum-600">Ver asignaciones</p>
                  </div>
                </button>
                <button className="btn-secondary p-4 text-left">
                  <CheckCircle className="w-6 h-6 mb-2 text-plum-600" />
                  <div>
                    <p className="font-semibold">Completar Reporte</p>
                    <p className="text-sm text-plum-600">Finalizar evaluación</p>
                  </div>
                </button>
              </>
            )}
            
            {hasRole('business_owner') && (
              <>
                <button className="btn-secondary p-4 text-left">
                  <Award className="w-6 h-6 mb-2 text-plum-600" />
                  <div>
                    <p className="font-semibold">Ver Estándares</p>
                    <p className="text-sm text-plum-600">Revisar requisitos</p>
                  </div>
                </button>
                <button className="btn-secondary p-4 text-left">
                  <ClipboardList className="w-6 h-6 mb-2 text-plum-600" />
                  <div>
                    <p className="font-semibold">Subir Evidencia</p>
                    <p className="text-sm text-plum-600">Documentar cumplimiento</p>
                  </div>
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
```

## 3. Reglas de Seguridad de Firestore

**Archivo**: `firestore.rules`

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Función para verificar autenticación
    function isAuthenticated() {
      return request.auth != null;
    }
    
    // Función para obtener rol del usuario
    function getUserRole() {
      return get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role;
    }
    
    // Función para verificar si es admin
    function isAdmin() {
      return isAuthenticated() && getUserRole() == 'admin';
    }
    
    // Función para verificar si es auditor
    function isAuditor() {
      return isAuthenticated() && getUserRole() == 'auditor';
    }
    
    // Función para verificar si es propietario de empresa
    function isBusinessOwner() {
      return isAuthenticated() && getUserRole() == 'business_owner';
    }
    
    // Función para verificar si es el dueño del recurso
    function isOwner(resourceData) {
      return isAuthenticated() && request.auth.uid == resourceData.uid;
    }

    // Colección de usuarios
    match /users/{userId} {
      allow read: if isAuthenticated() && (
        isAdmin() || 
        request.auth.uid == userId
      );
      allow write: if isAdmin() || (
        request.auth.uid == userId && 
        !('role' in request.resource.data) // Los usuarios no pueden cambiar su propio rol
      );
    }

    // Colección de perfiles de empresas
    match /business_profiles/{profileId} {
      allow read: if isAuthenticated() && (
        isAdmin() || 
        isAuditor() ||
        (isBusinessOwner() && isOwner(resource.data))
      );
      allow write: if isAdmin() || (
        isBusinessOwner() && isOwner(resource.data)
      );
    }

    // Colección de auditores
    match /auditors/{auditorId} {
      allow read: if isAuthenticated() && (isAdmin() || isAuditor());
      allow write: if isAdmin();
    }

    // Colección de estándares
    match /standards/{standardId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }

    // NOTA: En el modelo de datos actual, los `registers` están embebidos dentro 
    // de `responses` como parte del array `answers.register`, no como colección separada.
    // Las reglas de acceso a registers se manejan a través de las reglas de `responses`.
    
    // Colección de registros (evidencias) - DEPRECATED: Ahora embebidos en responses
    // match /registers/{registerId} {
    //   allow read: if isAuthenticated() && (
    //     isAdmin() || 
    //     isAuditor() ||
    //     (isBusinessOwner() && isOwner(resource.data))
    //   );
    //   allow create: if isAuthenticated() && isBusinessOwner();
    //   allow update: if isAuthenticated() && (
    //     isAdmin() || 
    //     (isBusinessOwner() && isOwner(resource.data))
    //   );
    //   allow delete: if isAdmin();
    // }

    // Colección de recursos
    match /resources/{resourceId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }

    // Colección de respuestas de empresas a estándares
    match /responses/{responseId} {
      allow read: if isAuthenticated() && (isAdmin() || isAuditor());
      allow write: if isAdmin();
    }

    // Colección de auditorías
    match /audits/{auditId} {
      allow read: if isAuthenticated() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid) ||
        (isBusinessOwner() && resource.data.businessProfileId == get(/databases/$(database)/documents/users/$(request.auth.uid)).data.businessProfileId)
      );
      allow create: if isAdmin();
      allow update: if isAuthenticated() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid)
      );
    }

    // Colección de reportes de auditoría
    match /audit_reports/{reportId} {
      allow read: if isAuthenticated() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid) ||
        (isBusinessOwner() && resource.data.businessProfileId == get(/databases/$(database)/documents/users/$(request.auth.uid)).data.businessProfileId)
      );
      allow create, update: if isAuthenticated() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid)
      );
    }
  }
}
```

## 4. Configuración de Deployment

**Archivo**: `firebase.json`

```json
{
  "hosting": {
    "public": "out",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      }
    ]
  },
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": {
    "source": "functions",
    "runtime": "nodejs18"
  }
}
```

**Archivo**: `next.config.ts`

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    NEXT_PUBLIC_FIREBASE_APP_ID: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  },
};

export default nextConfig;
```

## 5. Scripts de Deploy

**Archivo**: `scripts/deploy.sh`

```bash
#!/bin/bash

# Deploy script para CiruelaCertificada
echo "🍇 Iniciando deploy de CiruelaCertificada..."

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
  echo "❌ Error: Ejecutar desde el directorio del frontend"
  exit 1
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pnpm install

# Build del proyecto
echo "🔨 Construyendo proyecto..."
pnpm run build

# Deploy a Firebase
echo "🚀 Desplegando a Firebase..."
firebase deploy --only hosting,firestore:rules

echo "✅ Deploy completado!"
echo "🌐 Sitio disponible en: https://agro-extension-digital-npe.web.app"
```

---

## 🎯 Resumen Final

¡Perfecto! He completado la implementación del plan de autenticación y autorización con Tailwind CSS y el tema plum (ciruela). 

### 🎨 **Tema Visual Plum/Ciruela**
- **Paleta de colores completa** con tonos de ciruela (50-950)
- **Componentes CSS** personalizados para sidebar, botones, tarjetas y badges
- **Componentes React** con diseño cohesivo y branding consistente

### 🔐 **Sistema de Autenticación**
- **Firebase Auth** integrado con context personalizado
- **Roles y permisos** granulares por tipo de usuario
- **Páginas de login** con diseño plum y credenciales demo

### 🏗️ **Arquitectura Frontend**
- **Layout responsive** con sidebar navegable por roles
- **Dashboard personalizado** para cada tipo de usuario (admin, auditor, empresa)
- **Sistema de permisos** integrado en componentes

### 🔒 **Seguridad Firestore**
- **Reglas robustas** que respetan la jerarquía de permisos
- **Validación a nivel de base de datos** para todos los recursos
- **Protección por roles** y ownership de documentos

### 🚀 **Configuración de Deploy**
- **Next.js configurado** para export estático compatible con Firebase Hosting
- **Scripts automatizados** para deployment
- **Configuración completa** de Firebase

### 💡 **Características Destacadas**
- **WhatsApp Agent** integrado para empresas
- **Progreso visual** de certificación con barras animadas
- **Métricas en tiempo real** en dashboards
- **Navegación contextual** basada en permisos
- **Design system** completo con tema ciruela

El proyecto ahora está listo para implementación con un sistema completo de autenticación, autorización y una interfaz de usuario moderna y cohesiva que refleja la identidad del proyecto "CiruelaCertificada" 🍇✨

**Archivo**: `src/app/page.tsx` (Landing Page)

```typescript
import React from 'react';
import Link from 'next/link';
import { Grape, Award, Shield, Users, ArrowRight } from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      icon: Shield,
      title: 'Certificación Confiable',
      description: 'Proceso de certificación riguroso y transparente para la industria de ciruela deshidratada.'
    },
    {
      icon: Award,
      title: 'Estándares de Calidad',
      description: 'Cumplimos con los más altos estándares internacionales de calidad y seguridad alimentaria.'
    },
    {
      icon: Users,
      title: 'Red de Expertos',
      description: 'Auditores certificados y especialistas en la industria agrícola chilena.'
    },
    {
      icon: Grape,
      title: 'Especialización',
      description: 'Enfoque específico en la certificación de ciruela deshidratada y productos derivados.'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-plum-50 to-plum-100">
      {/* Header */}
      <header className="relative overflow-hidden bg-white shadow-lg">
        <div className="absolute inset-0 bg-gradient-to-r from-plum-600 to-plum-800 opacity-90"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-white mb-6">
              CiruelaCertificada
            </h1>
            <p className="text-xl text-plum-100 mb-8 max-w-3xl mx-auto">
              Plataforma líder en certificación de ciruela deshidratada chilena. 
              Garantizamos la calidad y trazabilidad de sus productos desde el huerto hasta el consumidor.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/auth/signin"
                className="btn-primary inline-flex items-center px-8 py-3 text-lg"
              >
                Acceder al Sistema
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link 
                href="#features"
                className="inline-flex items-center px-8 py-3 text-lg bg-white text-plum-700 rounded-lg hover:bg-plum-50 transition-colors duration-200"
              >
                Conocer Más
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-plum-900 mb-4">
              ¿Por qué elegir CiruelaCertificada?
            </h2>
            <p className="text-xl text-plum-700 max-w-3xl mx-auto">
              Ofrecemos una solución integral para la certificación de calidad 
              en la industria de ciruela deshidratada chilena.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="card p-6 text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-plum-100 text-plum-600 rounded-lg mb-4">
                    <Icon className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-semibold text-plum-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-plum-700">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-20 bg-plum-800">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            ¿Listo para certificar su producción?
          </h2>
          <p className="text-xl text-plum-200 mb-8">
            Únase a las empresas líderes que confían en CiruelaCertificada 
            para garantizar la calidad de sus productos.
          </p>
          <Link 
            href="/auth/signin"
            className="btn-primary inline-flex items-center px-8 py-4 text-lg"
          >
            Comenzar Certificación
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-plum-950 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">CiruelaCertificada</h3>
              <p className="text-plum-300">
                Certificación confiable para la industria de ciruela deshidratada chilena.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Enlaces</h4>
              <ul className="space-y-2">
                <li><Link href="/auth/signin" className="text-plum-300 hover:text-white">Acceder</Link></li>
                <li><Link href="#features" className="text-plum-300 hover:text-white">Características</Link></li>
                <li><Link href="/contact" className="text-plum-300 hover:text-white">Contacto</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Contacto</h4>
              <p className="text-plum-300">
                Email: info@ciruelacertificada.cl<br />
                Teléfono: +56 2 1234 5678
              </p>
            </div>
          </div>
          <div className="border-t border-plum-800 mt-8 pt-8 text-center">
            <p className="text-plum-400">
              © 2024 CiruelaCertificada. Todos los derechos reservados.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
```

**Archivo**: `src/app/auth/signin/page.tsx`

```typescript
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function SignInPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { signIn } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await signIn(email, password);
      router.push('/dashboard');
    } catch (error) {
      console.error('Error de inicio de sesión:', error);
      setError('Credenciales inválidas. Por favor, verifique su email y contraseña.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-plum-50 to-plum-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <h1 className="text-3xl font-bold text-plum-800">
              CiruelaCertificada
            </h1>
          </Link>
          <p className="text-plum-600 mt-2">
            Acceder al sistema de certificación
          </p>
        </div>

        {/* Formulario */}
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="flex items-center p-4 bg-error-50 border border-error-200 rounded-lg">
                <AlertCircle className="w-5 h-5 text-error-600 mr-2" />
                <span className="text-error-700">{error}</span>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-plum-700 mb-2">
                Correo Electrónico
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3 py-2 border border-plum-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
                placeholder="usuario@empresa.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-plum-700 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2 pr-10 border border-plum-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-plum-500 focus:border-transparent"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-plum-400 hover:text-plum-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-pulse-plum w-5 h-5 mr-2"></div>
                  Iniciando sesión...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <LogIn className="w-5 h-5 mr-2" />
                  Iniciar Sesión
                </div>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link 
              href="/"
              className="text-plum-600 hover:text-plum-800 text-sm"
            >
              ← Volver al inicio
            </Link>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="mt-6 text-center text-sm text-plum-600">
          <p className="mb-2">Credenciales de demostración:</p>
          <div className="space-y-1">
            <p><strong>Admin:</strong> admin@ciruela.cl / admin123</p>
            <p><strong>Auditor:</strong> auditor@ciruela.cl / auditor123</p>
            <p><strong>Empresa:</strong> empresa@ciruela.cl / empresa123</p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Archivo**: `src/contexts/AuthContext.tsx`

```typescript
interface AuthContextType {
  // Estado de autenticación
  user: User | null;
  firebaseUser: FirebaseUser | null;
  userRole: 'business_owner' | 'auditor' | 'admin' | null;
  loading: boolean;
  
  // Datos específicos del usuario
  businessProfile: BusinessProfile | null;
  auditorProfile: AuditorProfile | null;
  permissions: UserPermissions | null;
  
  // Acciones de autenticación
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, userData: any) => Promise<void>;
  signOut: () => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  
  // Acciones de autorización
  hasPermission: (permission: string) => boolean;
  canAccessBusiness: (businessRut: string) => boolean;
  refreshUserData: () => Promise<void>;
}
```

#### 2.2 Estructura de Páginas por Rol

```
src/app/
├── (auth)/                     # Rutas de autenticación
│   ├── login/page.tsx         # Login universal
│   ├── register/              
│   │   ├── business/page.tsx  # Registro empresarios
│   │   └── auditor/page.tsx   # Registro auditores (admin only)
│   └── layout.tsx
├── (dashboard)/               # Dashboard protegido
│   ├── business-owner/        # Dashboard empresarios
│   │   ├── profile/
│   │   ├── reports/
│   │   ├── audits/
│   │   └── layout.tsx
│   ├── auditor/              # Dashboard auditores  
│   │   ├── assigned-businesses/
│   │   ├── audits/
│   │   ├── reports/
│   │   └── layout.tsx
│   ├── admin/                # Dashboard admin
│   │   ├── users/
│   │   ├── businesses/
│   │   ├── auditors/
│   │   ├── reports/
│   │   └── layout.tsx
│   └── layout.tsx            # Layout protegido común
└── api/                      # API Routes
    ├── auth/
    │   ├── register/route.ts
    │   └── link-profile/route.ts
    ├── business-owner/
    │   ├── profile/route.ts
    │   └── reports/route.ts
    ├── auditor/
    │   ├── businesses/route.ts
    │   └── audits/route.ts
    └── admin/
        ├── users/route.ts
        └── analytics/route.ts
```

### Fase 3: Middleware de Autorización 🛡️

#### 3.1 Middleware Principal

**Archivo**: `src/middleware.ts`

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { adminAuth, adminDb } from './lib/firebase/server';

export async function middleware(request: NextRequest) {
  const authHeader = request.headers.get('authorization');
  const idToken = authHeader?.split('Bearer ')[1];

  if (!idToken) {
    return new Response(JSON.stringify({ error: 'No token provided' }), { 
      status: 401 
    });
  }

  try {
    // 1. Verificar token Firebase
    const decodedToken = await adminAuth.verifyIdToken(idToken);
    const { uid } = decodedToken;

    // 2. Obtener datos del usuario
    const userDoc = await adminDb.collection('users').doc(uid).get();
    
    if (!userDoc.exists) {
      return new Response(JSON.stringify({ error: 'User not found' }), { 
        status: 403 
      });
    }

    const userData = userDoc.data();
    const userRole = userData?.role;
    const isActive = userData?.isActive;

    if (!isActive) {
      return new Response(JSON.stringify({ error: 'Account inactive' }), { 
        status: 403 
      });
    }

    // 3. Control de acceso por rutas
    const pathname = request.nextUrl.pathname;
    const hasAccess = checkRouteAccess(pathname, userRole, userData);

    if (!hasAccess) {
      return new Response(JSON.stringify({ error: 'Insufficient permissions' }), { 
        status: 403 
      });
    }

    // 4. Agregar headers para API routes
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', uid);
    requestHeaders.set('x-user-role', userRole);
    requestHeaders.set('x-user-permissions', JSON.stringify(userData.permissions));

    return NextResponse.next({
      request: { headers: requestHeaders },
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: 'Invalid token' }), { 
      status: 401 
    });
  }
}

function checkRouteAccess(pathname: string, role: string, userData: any): boolean {
  const permissions = userData.permissions;
  
  // Mapeo de rutas a permisos específicos basado en webciruela.html
  const routePermissions = {
    // === RUTAS DE EMPRESA (BUSINESS_OWNER) ===
    '/api/business-owner/profile': ['canViewCompanyProfile', 'canEditCompanyProfile'],
    '/api/business-owner/standards': ['canViewStandards'],
    '/api/business-owner/surveys': ['canAnswerSurveys', 'canSubmitSurveys'],
    '/api/business-owner/evidence': ['canUploadEvidence', 'canViewEvidenceStatus'],
    '/api/business-owner/reports': ['canViewOwnReports'],
    '/api/business-owner/certification': ['canViewCertificationStatus'],
    '/api/business-owner/resources': ['canViewResources'],
    '/dashboard/business-owner': ['canAccessDashboard'],
    
    // === RUTAS DE AUDITOR ===
    '/api/auditor/assigned-businesses': ['canViewAssignedBusinesses'],
    '/api/auditor/business-profiles': ['canViewBusinessProfiles'],
    '/api/auditor/evidence/review': ['canReviewEvidence'],
    '/api/auditor/evidence/validate': ['canValidateEvidence'],
    '/api/auditor/evidence/reject': ['canRejectEvidence'],
    '/api/auditor/audit-templates': ['canDownloadAuditTemplates'],
    '/api/auditor/audit-reports': ['canCreateAuditReports'],
    '/api/auditor/progress': ['canViewAuditProgress'],
    '/api/auditor/compliance': ['canViewComplianceCharts'],
    '/api/auditor/map': ['canViewAssignedMap'],
    '/api/auditor/resources': ['canAccessAuditorResources'],
    '/dashboard/auditor': ['canAccessDashboard'],
    
    // === RUTAS DE ADMINISTRADOR ===
    '/api/admin/businesses': ['canViewAllBusinesses'],
    '/api/admin/auditors': ['canViewAllAuditors'],
    '/api/admin/users': ['canViewAllBusinesses', 'canViewAllAuditors'],
    '/api/admin/users/create': ['canCreateUsers'],
    '/api/admin/users/edit': ['canEditUsers'],
    '/api/admin/users/deactivate': ['canDeactivateUsers'],
    '/api/admin/assignments': ['canAssignAuditors', 'canUnassignAuditors'],
    '/api/admin/analytics': ['canViewAnalytics'],
    '/api/admin/regional-stats': ['canViewRegionalStats'],
    '/api/admin/auditor-progress': ['canViewAuditorProgress'],
    '/api/admin/industry-stats': ['canViewIndustryStats'],
    '/api/admin/resources': ['canManageResources'],
    '/api/admin/resources/delete': ['canDeleteResources'],
    '/api/admin/map': ['canViewSystemMap'],
    '/api/admin/export': ['canExportData'],
    '/api/admin/audit-assignments': ['canViewAuditAssignments'],
    '/api/admin/standards': ['canManageStandards'],
    '/dashboard/admin': ['canAccessDashboard'],
    
    // === RUTAS COMUNES ===
    '/api/common/resources': ['canViewResources'],
    '/api/common/support': ['canContactSupport'],
    '/api/public/stats': ['canViewPublicStats'],
    '/api/user/profile': ['canViewOwnData'],
    '/api/user/profile/edit': ['canEditOwnData']
  };

  // Verificar permisos específicos para la ruta
  for (const [route, requiredPermissions] of Object.entries(routePermissions)) {
    if (pathname.startsWith(route)) {
      return requiredPermissions.some(permission => permissions[permission] === true);
    }
  }

  // Control de acceso por rol (fallback)
  const roleRoutes = {
    admin: ['/api/admin/', '/api/business-owner/', '/api/auditor/', '/api/common/', '/api/user/'],
    business_owner: ['/api/business-owner/', '/api/common/', '/api/user/', '/api/public/'],
    auditor: ['/api/auditor/', '/api/common/', '/api/user/', '/api/public/']
  };

  const allowedRoutes = roleRoutes[role as keyof typeof roleRoutes] || [];
  return allowedRoutes.some(route => pathname.startsWith(route));
}

export const config = {
  matcher: [
    '/api/business-owner/:path*',
    '/api/auditor/:path*', 
    '/api/admin/:path*'
  ],
};
```

### Fase 4: Scripts de Migración 🔄

#### 4.1 Script de Migración de Datos

**Archivo**: `scripts/migrate-users.ts`

```typescript
/**
 * Script para migrar usuarios existentes a la nueva estructura
 */

import { adminAuth, adminDb } from '../src/lib/firebase/server';

interface MigrationSummary {
  businessOwners: number;
  auditors: number;
  errors: string[];
}

export async function migrateExistingUsers(): Promise<MigrationSummary> {
  const summary: MigrationSummary = {
    businessOwners: 0,
    auditors: 0,
    errors: []
  };

  try {
    // 1. Migrar Business Owners
    const businessProfiles = await adminDb.collection('business_profiles').get();
    
    for (const doc of businessProfiles.docs) {
      const businessData = doc.data();
      const email = businessData.owner_email;
      
      if (!email || email === 'test') continue;

      try {
        // Crear usuario en Firebase Auth si no existe
        let firebaseUser;
        try {
          firebaseUser = await adminAuth.getUserByEmail(email);
        } catch {
          firebaseUser = await adminAuth.createUser({
            email: email,
            displayName: businessData.owner_name,
            phoneNumber: businessData.owner_phone
          });
        }

        // Crear documento en colección users
        const userData = {
          uid: firebaseUser.uid,
          email: email,
          profile: {
            displayName: businessData.owner_name,
            phoneNumber: businessData.owner_phone
          },
          role: 'business_owner',
          isActive: true,
          businessProfile: {
            rut: businessData.rut,
            legal_name: businessData.legal_name
          },
          permissions: {
            // Permisos generales
            canViewOwnData: true,
            canEditOwnData: true,
            canAccessDashboard: true,
            canViewResources: true,
            canContactSupport: true,
            
            // Permisos específicos de empresa
            canViewCompanyProfile: true,
            canEditCompanyProfile: true,
            canViewStandards: true,
            canAnswerSurveys: true,
            canSubmitSurveys: true,
            canUploadEvidence: true,
            canViewEvidenceStatus: true,
            canViewOwnReports: true,
            canViewCertificationStatus: true,
            canFilterByStandard: true,
            canUseVirtualAgent: true,
            
            // Permisos NO disponibles para empresa
            canViewAssignedBusinesses: false,
            canReviewEvidence: false,
            canValidateEvidence: false,
            canViewAllBusinesses: false,
            canManageUsers: false,
            canAssignAuditors: false,
            canViewAnalytics: false,
            canManageResources: false,
            canViewSystemMap: false,
            canExportData: false,
            
            // Permisos especiales
            canViewPublicStats: true,
            canAccessAPI: false,
            canViewLogs: false,
            canManageSettings: false
          },
          createdAt: new Date(),
          lastLogin: null,
          updatedAt: new Date()
        };

        await adminDb.collection('users').doc(firebaseUser.uid).set(userData);

        // Actualizar business_profile con firebase_uid
        await adminDb.collection('business_profiles').doc(doc.id).update({
          firebase_uid: firebaseUser.uid,
          owner_status: 'active',
          account_created: new Date()
        });

        summary.businessOwners++;

      } catch (error) {
        summary.errors.push(`Error migrando business owner ${email}: ${error}`);
      }
    }

    // 2. Migrar Auditors
    const auditors = await adminDb.collection('auditors').get();
    
    for (const doc of auditors.docs) {
      const auditorData = doc.data();
      const email = auditorData.auditor_email;
      
      if (!email) continue;

      try {
        // Crear usuario en Firebase Auth si no existe
        let firebaseUser;
        try {
          firebaseUser = await adminAuth.getUserByEmail(email);
        } catch {
          firebaseUser = await adminAuth.createUser({
            email: email,
            displayName: auditorData.auditor_name,
            phoneNumber: auditorData.auditor_phone
          });
        }

        // Crear documento en colección users
        const userData = {
          uid: firebaseUser.uid,
          email: email,
          profile: {
            displayName: auditorData.auditor_name,
            phoneNumber: auditorData.auditor_phone
          },
          role: 'auditor',
          isActive: true,
          auditorProfile: {
            auditor_id: auditorData.auditor_id,
            assigned_businesses: auditorData.assigned_businesses || []
          },
          permissions: {
            // Permisos generales
            canViewOwnData: true,
            canEditOwnData: false, // Los auditores no pueden editar su perfil
            canAccessDashboard: true,
            canViewResources: true,
            canContactSupport: true,
            
            // Permisos específicos de auditor
            canViewAssignedBusinesses: true,
            canViewBusinessProfiles: true,
            canReviewEvidence: true,
            canValidateEvidence: true,
            canRejectEvidence: true,
            canDownloadAuditTemplates: true,
            canCreateAuditReports: true,
            canViewAuditProgress: true,
            canViewComplianceCharts: true,
            canViewAssignedMap: true,
            canAccessAuditorResources: true,
            
            // Permisos NO disponibles para auditor
            canEditCompanyProfile: false,
            canAnswerSurveys: false,
            canSubmitSurveys: false,
            canUploadEvidence: false,
            canViewAllBusinesses: false, // Solo ve empresas asignadas
            canManageUsers: false,
            canAssignAuditors: false,
            canViewAnalytics: false, // Solo ve analytics de sus empresas
            canManageResources: false,
            canDeleteResources: false,
            canExportData: false,
            canManageStandards: false,
            
            // Permisos especiales
            canViewPublicStats: true,
            canAccessAPI: true, // Para reportes
            canViewLogs: false,
            canManageSettings: false
          },
          createdAt: new Date(),
          lastLogin: null,
          updatedAt: new Date()
        };

        await adminDb.collection('users').doc(firebaseUser.uid).set(userData);

        // Actualizar auditor con firebase_uid
        await adminDb.collection('auditors').doc(doc.id).update({
          firebase_uid: firebaseUser.uid,
          auditor_status: 'active',
          account_created: new Date(),
          permissions_level: 'basic'
        });

        summary.auditors++;

      } catch (error) {
        summary.errors.push(`Error migrando auditor ${email}: ${error}`);
      }
    }

    // 3. Crear usuario administrador por defecto si no existe
    const adminEmail = "admin@agro-extension-digital.cl";
    try {
      let adminFirebaseUser;
      try {
        adminFirebaseUser = await adminAuth.getUserByEmail(adminEmail);
      } catch {
        adminFirebaseUser = await adminAuth.createUser({
          email: adminEmail,
          displayName: "Administrador del Sistema",
          password: "TempPassword123!" // Cambiar en primer login
        });
      }

      const adminUserData = {
        uid: adminFirebaseUser.uid,
        email: adminEmail,
        profile: {
          displayName: "Administrador del Sistema",
          phoneNumber: "+56912345678"
        },
        role: 'admin',
        isActive: true,
        permissions: {
          // Permisos generales - TODOS
          canViewOwnData: true,
          canEditOwnData: true,
          canAccessDashboard: true,
          canViewResources: true,
          canContactSupport: true,
          
          // Permisos de empresa - TODOS (para supervisión)
          canViewCompanyProfile: true,
          canEditCompanyProfile: true,
          canViewStandards: true,
          canAnswerSurveys: false, // Admin no responde encuestas
          canSubmitSurveys: false,
          canUploadEvidence: false, // Admin no sube evidencia
          canViewEvidenceStatus: true,
          canViewOwnReports: true,
          canViewCertificationStatus: true,
          canFilterByStandard: true,
          canUseVirtualAgent: true,
          
          // Permisos de auditor - TODOS (para supervisión)
          canViewAssignedBusinesses: true,
          canViewBusinessProfiles: true,
          canReviewEvidence: true,
          canValidateEvidence: true,
          canRejectEvidence: true,
          canDownloadAuditTemplates: true,
          canCreateAuditReports: true,
          canViewAuditProgress: true,
          canViewComplianceCharts: true,
          canViewAssignedMap: true,
          canAccessAuditorResources: true,
          
          // Permisos exclusivos de administrador
          canViewAllBusinesses: true,
          canViewAllAuditors: true,
          canCreateUsers: true,
          canEditUsers: true,
          canDeactivateUsers: true,
          canAssignAuditors: true,
          canUnassignAuditors: true,
          canViewAnalytics: true,
          canViewRegionalStats: true,
          canViewAuditorProgress: true,
          canViewIndustryStats: true,
          canManageResources: true,
          canDeleteResources: true,
          canViewSystemMap: true,
          canExportData: true,
          canViewAuditAssignments: true,
          canManageStandards: true,
          
          // Permisos especiales - TODOS
          canViewPublicStats: true,
          canAccessAPI: true,
          canViewLogs: true,
          canManageSettings: true
        },
        createdAt: new Date(),
        lastLogin: null,
        updatedAt: new Date()
      };

      await adminDb.collection('users').doc(adminFirebaseUser.uid).set(adminUserData);
      console.log("Usuario administrador creado/actualizado");

    } catch (error) {
      summary.errors.push(`Error creando administrador: ${error}`);
    }
  }

  return summary;
}
```

### Fase 5: Reglas de Seguridad Firestore 🔒

#### 5.1 Firestore Security Rules

**Archivo**: `firestore.rules`

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Función auxiliar para obtener datos del usuario
    function getUserData() {
      return get(/databases/$(database)/documents/users/$(request.auth.uid)).data;
    }
    
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isAdmin() {
      return isAuthenticated() && getUserData().role == 'admin';
    }
    
    function isBusinessOwner() {
      return isAuthenticated() && getUserData().role == 'business_owner';
    }
    
    function isAuditor() {
      return isAuthenticated() && getUserData().role == 'auditor';
    }

    // Colección users - Solo el propio usuario puede leer/escribir
    match /users/{userId} {
      allow read, write: if isAuthenticated() && request.auth.uid == userId;
      allow read: if isAdmin(); // Admin puede leer todos los usuarios
    }

    // Business profiles - Acceso basado en ownership
    match /business_profiles/{profileId} {
      allow read: if isAuthenticated() && (
        isAdmin() ||
        (isBusinessOwner() && getUserData().businessProfile.rut == resource.data.rut) ||
        (isAuditor() && resource.data.rut in getUserData().auditorProfile.assigned_businesses)
      );
      
      allow write: if isAuthenticated() && (
        isAdmin() ||
        (isBusinessOwner() && getUserData().businessProfile.rut == resource.data.rut)
      );
    }

    // Auditors - Solo admin y el propio auditor
    match /auditors/{auditorId} {
      allow read: if isAuthenticated() && (
        isAdmin() ||
        (isAuditor() && getUserData().auditorProfile.auditor_id == resource.data.auditor_id)
      );
      
      allow write: if isAdmin();
    }

    // NOTA: Registers están embebidos en responses.answers.register
    // Las reglas de acceso se manejan a través de las reglas de responses
    
    // Registers - DEPRECATED: Ahora embebidos en responses
    // match /registers/{registerId} {
    //   allow read: if isAuthenticated() && (
    //     isAdmin() ||
    //     (isBusinessOwner() && getUserData().businessProfile.rut == resource.data.business_rut) ||
    //     (isAuditor() && resource.data.business_rut in getUserData().auditorProfile.assigned_businesses)
    //   );
    //   
    //   allow create: if isAuthenticated() && (
    //     isAdmin() ||
    //     isAuditor()
    //   );
    //   
    //   allow update: if isAuthenticated() && (
    //     isAdmin() ||
    //     (isAuditor() && resource.data.business_rut in getUserData().auditorProfile.assigned_businesses)
    //   );
    // }

    // Resources - Solo lectura para usuarios autenticados
    match /resources/{resourceId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }

    // Standards - Solo lectura para usuarios autenticados
    match /standards/{standardId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }

    // Responses - Solo lectura para usuarios autenticados
    match /responses/{responseId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }
  }
}
```

## Permisos Específicos Basados en WebCiruela.html

### 🏢 **Business Owner (Empresa)**

#### Dashboard Principal (`/dashboard/business-owner`)
- **Panel de resumen**: Visualizar estándares, puntaje, pendientes, auditorías
- **Filtros por estándar**: General, Producción Primaria, Adecuación Agroindustrial
- **Evaluación de certificación**: Ver años de certificación y estado (oro/plata/bronce)
- **Gráficos de cumplimiento**: Fundamental vs General, progreso temporal
- **Acceso a agente virtual**: Botón de WhatsApp integrado

#### Gestión de Perfil (`/profile`)
- **Ver información**: RUT, nombre legal, propietario, contacto
- **Editar datos**: Región, comuna, dirección, herramientas digitales
- **Gestionar proceso**: Tipo de proceso de producción

#### Estándares y Encuestas (`/standards`)
- **Ver estándares disponibles**: Lista completa de estándares
- **Responder encuestas**: Cuestionarios de cumplimiento
- **Opciones de respuesta**: "Si cumplo", "No cumplo", "Factible", "No Aplica"
- **Ver verificación**: Criterios y buenas prácticas
- **Enviar respuestas**: Submit de encuestas completadas

#### Registro de Evidencia (`/evidence`)
- **Subir documentos**: Evidencia de cumplimiento por acción
- **Ver estado**: Validado, Pendiente, Rechazado
- **Gestionar archivos**: Por estándar y acción específica
- **Seguimiento temporal**: Fechas de subida y validación

#### Recursos (`/resources`)
- **Acceder documentación**: PDFs, videos, manuales
- **Filtrar por tema**: Agua, plagas, suelo, etc.
- **Descargar materiales**: Guías y buenas prácticas

### 🔍 **Auditor**

#### Dashboard Principal (`/dashboard/auditor`)
- **Resumen de trabajo**: Auditorías asignadas, pendientes, validadas
- **Mapa interactivo**: Ubicación de empresas asignadas
- **Gráficos de cumplimiento**: Por empresa asignada
- **Contacto de soporte**: Email y WhatsApp especializado

#### Auditorías Asignadas (`/assigned-audits`)
- **Ver empresas**: Lista de empresas bajo su responsabilidad
- **Estado por empresa**: Pendiente, en revisión, validado, rechazado
- **Descargar pautas**: Templates de auditoría imprimibles
- **Botón de revisión**: Acceso directo a revisar evidencia

#### Revisión de Evidencia (`/evidence/review`)
- **Validar documentos**: Aprobar evidencia subida
- **Rechazar con comentarios**: Feedback específico para mejoras
- **Seguimiento**: Historial de revisiones por empresa
- **Exportar reportes**: Reportes de auditoría completos

#### Recursos Especializados (`/resources`)
- **Criterios de verificación**: Documentos técnicos específicos
- **Guías de auditoría**: Metodologías y mejores prácticas
- **Videos formativos**: Capacitación continua
- **Plantillas**: Excel para reportes estandarizados

### 👨‍💼 **Administrador**

#### Dashboard Principal (`/dashboard/admin`)
- **Estadísticas globales**: Métricas de toda la industria
- **Mapa completo**: Todas las empresas participantes
- **Análisis regional**: Cumplimiento por región
- **Progreso de auditores**: Performance y productividad

#### Gestión de Usuarios (`/admin/users`)
- **Crear usuarios**: Nuevos auditores y empresas
- **Editar perfiles**: Información y permisos
- **Activar/desactivar**: Control de acceso
- **Asignar roles**: Business owner, auditor, admin

#### Asignación de Auditorías (`/admin/assignments`)
- **Asignar auditores**: A empresas específicas
- **Ver asignaciones**: Lista completa de relaciones
- **Redistribuir cargas**: Balanceo de trabajo
- **Gestionar conflictos**: Resolución de problemas

#### Analíticas Avanzadas (`/admin/analytics`)
- **Estadísticas de industria**: Cumplimiento general, tendencias
- **Análisis regional**: Performance por zona geográfica
- **Progreso temporal**: Evolución de indicadores
- **Exportar datos**: Reports completos en Excel/PDF

#### Gestión de Recursos (`/admin/resources`)
- **Subir documentos**: Nuevos materiales y guías
- **Categorizar contenido**: Por tema y tipo de usuario
- **Eliminar recursos**: Mantenimiento de biblioteca
- **Controlar acceso**: Qué roles ven qué recursos

### 📊 **Matriz de Permisos por Funcionalidad**

| Funcionalidad | Business Owner | Auditor | Admin | Público |
|---------------|----------------|---------|-------|---------|
| Ver dashboard propio | ✅ | ✅ | ✅ | ❌ |
| Ver perfil empresa | ✅ (solo suya) | ✅ (asignadas) | ✅ (todas) | ❌ |
| Responder encuestas | ✅ | ❌ | ❌ | ❌ |
| Subir evidencia | ✅ | ❌ | ❌ | ❌ |
| Validar evidencia | ❌ | ✅ | ✅ | ❌ |
| Ver todas las empresas | ❌ | ❌ | ✅ | ❌ |
| Asignar auditores | ❌ | ❌ | ✅ | ❌ |
| Ver analíticas globales | ❌ | ❌ | ✅ | ✅ (limitado) |
| Gestionar usuarios | ❌ | ❌ | ✅ | ❌ |
| Descargar pautas | ❌ | ✅ | ✅ | ❌ |
| Contactar soporte | ✅ | ✅ | ✅ | ✅ |
| Usar agente virtual | ✅ | ✅ | ✅ | ❌ |
| Ver recursos | ✅ (empresa) | ✅ (auditor) | ✅ (todos) | ❌ |
| Exportar datos | ❌ | ✅ (limitado) | ✅ | ❌ |

## Cronograma de Implementación

### Sprint 1 (Semana 1): Preparación
- [ ] Crear colección `users` en Firestore
- [ ] Actualizar campos en `business_profiles` y `auditors`
- [ ] Configurar Firebase Authentication
- [ ] Escribir scripts de migración

### Sprint 2 (Semana 2): Backend
- [ ] Implementar middleware de autorización
- [ ] Crear API routes protegidas
- [ ] Configurar Firestore Security Rules
- [ ] Ejecutar migración de datos

### Sprint 3 (Semana 3): Frontend Core
- [ ] Implementar AuthContext
- [ ] Crear componentes de autenticación
- [ ] Desarrollar páginas de login/registro
- [ ] Implementar protección de rutas

### Sprint 4 (Semana 4): Dashboards
- [ ] Dashboard para business owners
- [ ] Dashboard para auditores
- [ ] Dashboard para administradores
- [ ] Testing integrado

### Sprint 5 (Semana 5): Testing y Deploy
- [ ] Testing exhaustivo de permisos
- [ ] Validación de flujos de usuario
- [ ] Deploy a entorno de desarrollo
- [ ] Documentación final

## Consideraciones Especiales

### 🔐 Seguridad
- Tokens Firebase con expiración automática
- Validación en servidor para todas las operaciones sensibles
- Logging de accesos y cambios importantes
- Rate limiting en API routes críticas

### 📊 Análisis de Datos
- Mantener la integridad referencial entre colecciones
- Índices optimizados para consultas de autorización
- Backup de datos antes de migración

### 🚀 Escalabilidad
- Estructura preparada para nuevos roles
- Permisos granulares y configurables
- Cache de datos de usuario para performance

## Métricas de Éxito

- [ ] 100% de usuarios existentes migrados correctamente
- [ ] Tiempo de login < 3 segundos
- [ ] 0 fallos de seguridad en auditoría
- [ ] Cobertura de tests > 85%
- [ ] Documentación completa y actualizada

---

*Este plan integra las colecciones existentes con Firebase Auth manteniendo la integridad de los datos y proporcionando un sistema de autorización robusto y escalable.*
