include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../modules/database"
}

# Configuración del backend remoto específica para DEV Database
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
  
  # Configuración específica de DEV
  database_name               = "agro-extension-db"
  delete_protection_enabled   = false  # En DEV permitimos eliminar para testing
  enable_daily_backup        = false   # No necesario en DEV
  backup_retention_days      = 7       # Retención mínima en DEV
  
  # Usuarios admin para DEV (agregar emails según necesidad)
  firestore_admin_users = [
    # "admin@ciruelacertificada.cl"
  ]
  
  # Service accounts que necesitan acceso a Firestore
  firestore_user_service_accounts = [
    # Estos se obtienen de otros módulos de Terragrunt
    # En una implementación real, usarías dependency para obtener los emails
    # Por ahora los dejamos vacíos y se pueden agregar manualmente
  ]
  
  # Reglas de seguridad específicas para DEV (más permisivas para testing)
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

    // Colección de usuarios
    match /users/{userId} {
      allow read: if isAuthenticated() && (
        isAdmin() || 
        request.auth.uid == userId
      );
      allow write: if isAdmin() || (
        request.auth.uid == userId && 
        !('role' in request.resource.data)
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

    // Colección de registros (evidencias)
    match /registers/{registerId} {
      allow read: if isAuthenticated() && (
        isAdmin() || 
        isAuditor() ||
        (isBusinessOwner() && isOwner(resource.data))
      );
      allow create: if isAuthenticated() && isBusinessOwner();
      allow update: if isAuthenticated() && (
        isAdmin() || 
        (isBusinessOwner() && isOwner(resource.data))
      );
      allow delete: if isAdmin();
    }

    // Colección de recursos
    match /resources/{resourceId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }

    // Colección de respuestas estándar
    match /standard_responses/{responseId} {
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
EOF
}
