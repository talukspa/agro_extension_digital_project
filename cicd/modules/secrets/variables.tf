# Variables para el módulo de gestión de secretos

variable "project_id" {
  description = "ID del proyecto de Google Cloud"
  type        = string
}

variable "environment" {
  description = "Entorno de despliegue (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "firebase_api_key" {
  description = "API Key de Firebase para el frontend"
  type        = string
  sensitive   = true
}

variable "whatsapp_api_token" {
  description = "Token de API de WhatsApp Business"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "API Key de OpenAI para agentes inteligentes"
  type        = string
  sensitive   = true
  default     = ""
}

variable "jwt_secret" {
  description = "Secreto para firma de JWT tokens"
  type        = string
  sensitive   = true
  default     = ""
}

variable "firebase_admin_sdk_key" {
  description = "Clave JSON del Firebase Admin SDK"
  type        = string
  sensitive   = true
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

variable "cors_origins" {
  description = "Orígenes permitidos para CORS"
  type        = list(string)
  default     = ["http://localhost:3000", "https://localhost:3000"]
}

variable "log_level" {
  description = "Nivel de logging de la aplicación"
  type        = string
  default     = "info"
}

variable "session_timeout" {
  description = "Timeout de sesión en segundos"
  type        = number
  default     = 3600
}
