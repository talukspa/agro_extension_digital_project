variable "project_id" {
  description = "ID del proyecto de Google Cloud"
  type        = string
}

variable "region" {
  description = "Ubicación de los servicios"
  type        = string
}

variable "cloud_run_name_webhook" {
  description = "Nombre del servicio de Cloud Run para el webhook"
  type        = string
}

variable "gar_image_location_webhook" {
  description = "Ubicación de la imagen del servicio de Cloud Run"
  type        = string
}

variable "estandar_aa_facebook_app" {
  description = "URL del servicio de Facebook para AA"
  type        = string
}

variable "estandar_pp_facebook_app" {
  description = "URL del servicio de Facebook para PP"
  type        = string
}

variable "verify_token" {
  description = "Token de verificación"
  type        = string
}

variable "service_account_webhook_app" {
  description = "Cuenta de servicio para el webhook"
  type        = string
}

variable "service_account_display_name_webhook_app" {
  description = "Nombre para mostrar de la cuenta de servicio del webhook"
  type        = string
}

variable "estandar_aa_app_name" {
  description = "Nombre del app AA (entrega target agent al webhook)"
  type        = string
}

variable "estandar_pp_app_name" {
  description = "Nombre del app PP (entrega target agent al webhook)"
  type        = string
}

variable "wsp_token" {
  description = "Token de WhatsApp"
  type        = string
}

variable "whatsapp_base_url" {
  description = "Base URL for WhatsApp Graph API"
  type        = string
  default     = "https://graph.facebook.com/v22.0"
}

variable "log_level" {
  description = "Nivel de logging para la aplicación webhook (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
  type        = string
  default     = "INFO"
}

variable "whatsapp_http_timeout" {
  description = "Timeout en segundos para llamadas HTTP del webhook a WhatsApp Graph API"
  type        = string
  default     = "30"
}

variable "startup_cpu_boost" {
  description = "Habilita Startup CPU Boost en Cloud Run para acelerar el arranque"
  type        = bool
  default     = true
}

variable "min_scale" {
  description = "Cantidad mínima de instancias para los servicios de Cloud Run (run.googleapis.com/minScale)"
  type        = number
  default     = 1
}

variable "max_scale" {
  description = "Cantidad máxima de instancias para los servicios de Cloud Run (debe ser >= min_scale)"
  type        = number
  default     = 10
}
