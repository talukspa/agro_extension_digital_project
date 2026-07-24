include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../modules/database"
}

# Configuración del backend remoto específica para PRD Database
remote_state {
  backend = "gcs"
  config = {
    bucket   = yamldecode(file("../env.yaml")).terraform_state.bucket
    project  = yamldecode(file("../env.yaml")).project.id
    prefix   = "${path_relative_to_include()}/terraform.tfstate"
    location = yamldecode(file(find_in_parent_folders("common.yaml"))).gcp.default_region
  }
}

# Importar configuración común desde archivos yaml
locals {
  # Cargar configuración base desde archivos yaml
  common_vars = yamldecode(file(find_in_parent_folders("common.yaml")))
  env_vars    = yamldecode(file("../env.yaml"))

  # Valores base desde env.yaml (específicos del ambiente)
  project_id  = local.env_vars.project.id
  region      = local.common_vars.gcp.default_region
  environment = local.env_vars.environment.name
}

inputs = {
  # Configuración base
  project_id        = local.project_id
  environment       = local.environment
  database_location = local.region

  # Configuración específica de PRD (más restrictiva)
  database_name             = "agro-extension-db"
  delete_protection_enabled = true # En PRD protegemos contra eliminación
  enable_daily_backup       = true # Backup automático habilitado
  backup_retention_days     = 90   # Retención extendida en PRD

  # Reglas de seguridad para PRD (más estrictas)
  firestore_security_rules = <<EOF
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
    
    // Función para verificar si el usuario está activo
    function isActiveUser() {
      return isAuthenticated() && get(/databases/$(database)/documents/users/$(request.auth.uid)).data.isActive == true;
    }

    // Colección de usuarios - Más restrictiva en PRD
    match /users/{userId} {
      allow read: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        request.auth.uid == userId
      );
      allow write: if isAdmin() || (
        request.auth.uid == userId && 
        isActiveUser() &&
        !('role' in request.resource.data) &&
        !('isActive' in request.resource.data)
      );
    }

    // Colección de perfiles de empresas - Con validación de usuario activo
    match /business_profiles/{profileId} {
      allow read: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        isAuditor() ||
        (isBusinessOwner() && isOwner(resource.data))
      );
      allow write: if isActiveUser() && (
        isAdmin() || 
        (isBusinessOwner() && isOwner(resource.data))
      );
    }

    // Colección de auditores - Solo lectura para auditores activos
    match /auditors/{auditorId} {
      allow read: if isAuthenticated() && isActiveUser() && (isAdmin() || isAuditor());
      allow write: if isAdmin();
    }

    // Colección de estándares - Solo lectura general
    match /standards/{standardId} {
      allow read: if isAuthenticated() && isActiveUser();
      allow write: if isAdmin();
    }

    // Colección de registros (evidencias) - Con logging de auditoría
    match /registers/{registerId} {
      allow read: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        isAuditor() ||
        (isBusinessOwner() && isOwner(resource.data))
      );
      allow create: if isAuthenticated() && isActiveUser() && isBusinessOwner() &&
        request.resource.data.keys().hasAll(['businessProfileId', 'standardId', 'createdAt', 'status']);
      allow update: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        (isBusinessOwner() && isOwner(resource.data) && 
         resource.data.status != 'approved') // No permitir modificar registros aprobados
      );
      allow delete: if isAdmin();
    }

    // Colección de recursos
    match /resources/{resourceId} {
      allow read: if isAuthenticated() && isActiveUser();
      allow write: if isAdmin();
    }

    // Colección de respuestas estándar
    match /standard_responses/{responseId} {
      allow read: if isAuthenticated() && isActiveUser() && (isAdmin() || isAuditor());
      allow write: if isAdmin();
    }

    // Colección de auditorías - Con restricciones adicionales
    match /audits/{auditId} {
      allow read: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid) ||
        (isBusinessOwner() && resource.data.businessProfileId == get(/databases/$(database)/documents/users/$(request.auth.uid)).data.businessProfileId)
      );
      allow create: if isAdmin();
      allow update: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid &&
         resource.data.status != 'completed') // No modificar auditorías completadas
      );
    }

    // Colección de reportes de auditoría - Solo escritura por auditor asignado
    match /audit_reports/{reportId} {
      allow read: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid) ||
        (isBusinessOwner() && resource.data.businessProfileId == get(/databases/$(database)/documents/users/$(request.auth.uid)).data.businessProfileId)
      );
      allow create, update: if isAuthenticated() && isActiveUser() && (
        isAdmin() || 
        (isAuditor() && resource.data.auditorId == request.auth.uid)
      );
    }
  }
}
EOF
}
