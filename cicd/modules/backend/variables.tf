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

variable "whatsapp_app_secret_aa" {
  description = "Meta App Secret de la app AA, usado para validar la firma X-Hub-Signature-256 de los webhooks AA entrantes. AA y PP son apps de Meta distintas con secrets propios. El webhook rechaza (403) todo POST AA si no está seteado (fail-closed)."
  type        = string
  sensitive   = true
}

variable "whatsapp_app_secret_pp" {
  description = "Meta App Secret de la app PP, usado para validar la firma X-Hub-Signature-256 de los webhooks PP entrantes. El webhook rechaza (403) todo POST PP si no está seteado (fail-closed)."
  type        = string
  sensitive   = true
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

variable "webhook_cpu" {
  description = "Límite de CPU del contenedor del webhook."
  type        = string
  default     = "1"
}

variable "webhook_memory" {
  # El default histórico de Cloud Run (512Mi) NO alcanza: tras la migración a
  # Agent Runtime el webhook importa el SDK de Vertex AI (google-cloud-aiplatform),
  # cuyo footprint en el arranque supera 512Mi (~536Mi observado), y Cloud Run
  # mata la instancia en el startup probe. 1Gi da headroom cómodo.
  description = "Límite de memoria del contenedor del webhook."
  type        = string
  default     = "1Gi"
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

# --------------------------------------------------------------------
# Agent Runtime config — surfaced to deploy.py via Secret Manager.
# Per-env values come from cicd/stacks/<env>/env.yaml -> terragrunt.hcl.
# --------------------------------------------------------------------
variable "bigquery_dataset" {
  description = "BigQuery dataset name; surfaced via Secret Manager secret 'bigquery-dataset'."
  type        = string
}

variable "datastore_aa_id" {
  description = "Full Vertex AI Search datastore resource path for AA. Surfaced via 'datastore-aa-id' secret."
  type        = string
}

variable "datastore_pp_id" {
  description = "Full Vertex AI Search datastore resource path for PP. Surfaced via 'datastore-pp-id' secret."
  type        = string
}

variable "datastore_guides_id" {
  description = "Datastore path for guides. Surfaced via 'datastore-guides-id' secret."
  type        = string
}

variable "datastore_faq_id" {
  description = "Datastore path for FAQ. Surfaced via 'datastore-faq-id' secret."
  type        = string
}

variable "datastore_chileprunes_cl_id" {
  description = "Datastore path for chileprunes-cl. Surfaced via 'datastore-chileprunes-cl-id' secret."
  type        = string
}

variable "deployer_sa_email" {
  description = <<-EOT
    Email of the CI/CD deployer service account (the identity behind
    secrets.GCP_SA_KEY in deploy-agents.yml). When non-empty, Terraform grants
    it everything deploy.py needs: iam.serviceAccountUser (actAs) on the two
    runtime SAs, storage.objectAdmin on the staging bucket, project
    aiplatform.user, secretmanager.secretVersionAdder on the engine-name
    secrets, and secretmanager.secretAccessor on the runtime-config secrets.
    Leave empty to skip these bindings (e.g. if the deployer already holds
    broader project grants out of band).
  EOT
  type        = string
  default     = ""
}
