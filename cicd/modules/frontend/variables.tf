variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
}

variable "environment" {
  description = "The environment name"
  type        = string
}

variable "location" {
  description = "The Google Cloud location"
  type        = string
}

variable "cloud_run_name_frontend" {
  description = "The name of the frontend Cloud Run service"
  type        = string
}

variable "gar_image_location_frontend" {
  description = "The location of the frontend container image in GAR"
  type        = string
}

variable "min_scale" {
  description = "The minimum number of instances"
  type        = number
  default     = 0
}

variable "max_scale" {
  description = "The maximum number of instances"
  type        = number
  default     = 10
}

variable "cpu_limit" {
  description = "The CPU limit for the container"
  type        = string
  default     = "1000m"
}

variable "memory_limit" {
  description = "The memory limit for the container"
  type        = string
  default     = "2Gi"
}

# Service Account Configuration
variable "service_account_id_frontend" {
  description = "Service account ID for frontend"
  type        = string
}

variable "service_account_display_name_frontend" {
  description = "Display name for frontend service account"
  type        = string
}

# Startup Configuration
variable "startup_cpu_boost" {
  description = "Enable startup CPU boost"
  type        = bool
  default     = true
}

# Firebase Configuration
variable "firebase_api_key" {
  description = "Firebase API Key"
  type        = string
}

variable "firebase_auth_domain" {
  description = "Firebase Auth Domain"
  type        = string
}

variable "firebase_storage_bucket" {
  description = "Firebase Storage Bucket"
  type        = string
}

variable "firebase_messaging_sender_id" {
  description = "Firebase Messaging Sender ID"
  type        = string
}

variable "firebase_app_id" {
  description = "Firebase App ID"
  type        = string
}

variable "firebase_measurement_id" {
  description = "Firebase Measurement ID"
  type        = string
  default     = ""
}

# Backend Services URLs
variable "agent_aa_service_url" {
  description = "URL of the Agent AA service"
  type        = string
}

variable "webhook_service_url" {
  description = "URL of the Webhook service"
  type        = string
}

# Database Configuration
variable "firestore_database_id" {
  description = "Firestore database ID"
  type        = string
  default     = "agro-extension-db"
}