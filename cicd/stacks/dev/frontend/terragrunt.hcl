include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../modules/frontend"
}

# Configuración del backend remoto específico para DEV Frontend
remote_state {
  backend = "gcs"
  config = {
    bucket   = yamldecode(file("../env.yaml")).terraform_state.bucket
    project  = yamldecode(file("../env.yaml")).project.id
    prefix   = "${path_relative_to_include()}/terraform.tfstate"
    location = yamldecode(file(find_in_parent_folders("common.yaml"))).gcp.default_region
  }
}

# El frontend ya no depende del backend: el agente AA es ahora un Agent Engine
# (sin URL de Cloud Run) y la URL del webhook se fija abajo. Se eliminó el bloque
# `dependency "backend"` porque ninguna salida del backend se consume aquí.

# Importar configuración común desde archivos yaml
locals {
  # Cargar configuración base desde archivos yaml
  common_vars = yamldecode(file(find_in_parent_folders("common.yaml")))
  env_vars    = yamldecode(file("../env.yaml"))

  # Valores base desde env.yaml (específicos del ambiente)
  project_id  = local.env_vars.project.id
  region      = local.common_vars.gcp.default_region
  environment = local.env_vars.environment.name

  # URL base del registro de imágenes (mismo path al que CI empuja; las imágenes
  # viven en el proyecto NPE para ambos entornos — ver common.yaml).
  gar_base_url = "${local.common_vars.containers.registry}/${local.common_vars.containers.project}/${local.common_vars.containers.repository}"

  # Firebase configuration específica de DEV
  firebase_config = {
    api_key             = "AIzaSyD0nFbsMt_TaEJ-qRTodXEWF9ZdF6Ka0_M"
    auth_domain         = "${local.project_id}.firebaseapp.com"
    storage_bucket      = "${local.project_id}.firebasestorage.app"
    messaging_sender_id = "890639421110"
    app_id              = "1:890639421110:web:aeabdca529fefeb64aa017"
    measurement_id      = "G-TZBH5RVGBW"
  }
}

inputs = {
  # Configuración base
  project_id  = local.project_id
  environment = local.environment
  location    = local.region

  # Frontend Service Configuration
  cloud_run_name_frontend               = "frontend-${local.environment}"
  service_account_id_frontend           = "frontend-sa-${local.environment}"
  service_account_display_name_frontend = "Frontend Service Account DEV"
  gar_image_location_frontend           = "${local.gar_base_url}/agent-frontend-app:latest"

  # Scaling Configuration
  min_scale         = 0 # DEV puede bajar a 0
  max_scale         = 5 # Límite para DEV
  startup_cpu_boost = true

  # Resource Configuration
  cpu_limit    = "1000m"
  memory_limit = "2Gi"

  # Firebase Configuration
  firebase_api_key             = local.firebase_config.api_key
  firebase_auth_domain         = local.firebase_config.auth_domain
  firebase_storage_bucket      = local.firebase_config.storage_bucket
  firebase_messaging_sender_id = local.firebase_config.messaging_sender_id
  firebase_app_id              = local.firebase_config.app_id
  firebase_measurement_id      = local.firebase_config.measurement_id

  # Backend Services URLs
  webhook_service_url = "https://agent-webhook-dev-c2udweuoga-uc.a.run.app"

  # Database Configuration
  firestore_database_id = "agro-extension-db"
}