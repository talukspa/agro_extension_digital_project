# Variables para el módulo de base de datos Firestore

variable "project_id" {
  description = "ID del proyecto de Google Cloud"
  type        = string
}

variable "database_name" {
  description = "Nombre de la base de datos Firestore"
  type        = string
  default     = "agro-extension-db"
}

variable "database_location" {
  description = "Ubicación de la base de datos Firestore"
  type        = string
  default     = "us-central1"
}

variable "delete_protection_enabled" {
  description = "Habilitar protección contra eliminación de la base de datos"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Días de retención para backups automáticos"
  type        = number
  default     = 30
}

variable "firestore_security_rules" {
  description = "Reglas de seguridad de Firestore en formato string"
  type        = string
  default     = <<EOF
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir lectura y escritura solo a usuarios autenticados
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
EOF
}

variable "enable_daily_backup" {
  description = "Habilitar backup diario automático"
  type        = bool
  default     = true
}

variable "environment" {
  description = "Ambiente de deployment (dev, prd)"
  type        = string
  validation {
    condition     = contains(["dev", "prd"], var.environment)
    error_message = "Environment debe ser 'dev' o 'prd'."
  }
}
