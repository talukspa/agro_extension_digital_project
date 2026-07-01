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
  description = <<-DESC
    Firestore security rules (CEL source string). Each stack MUST pass its
    per-environment RBAC ruleset. Defaults to empty so an omission falls back
    to the explicit minimal fallback file in the module (a single greppable
    place) rather than silently deploying a wide-open "any authenticated user"
    default — that permissive default was the prod-authz footgun this replaces.
  DESC
  type        = string
  default     = ""
}

variable "enable_daily_backup" {
  description = "Habilitar backup diario automático"
  type        = bool
  default     = true
}

# Kept as a validated input contract: both database stacks pass `environment`
# and the validation fails fast on anything but dev/prd. No resource references
# it directly, so tflint flags it as unused — that's expected here.
# tflint-ignore: terraform_unused_declarations
variable "environment" {
  description = "Ambiente de deployment (dev, prd)"
  type        = string
  validation {
    condition     = contains(["dev", "prd"], var.environment)
    error_message = "Environment debe ser 'dev' o 'prd'."
  }
}
