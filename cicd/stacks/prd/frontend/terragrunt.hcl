include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../modules/frontend"
}

# Configuración del backend remoto específica para PRD Frontend
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
  
  # Valores base desde env.yaml (específicos del ambiente PRD)
  project_id  = local.env_vars.project.id
  region      = local.common_vars.gcp.default_region
  environment = local.env_vars.environment.name
  
  # URLs base para frontend
  gar_base_url = "${local.common_vars.containers.registry}/${local.common_vars.containers.project}/${local.common_vars.containers.repository}"
}

inputs = {
  # Configuración base
  project_id  = local.project_id
  environment = local.environment
  location    = local.region
  
  # Frontend configuración
  cloud_run_name_frontend = "frontend-app-${local.environment}"
  gar_image_location_frontend = "${local.gar_base_url}/agent-frontend-app:latest"
  
  # Variables de entorno de Firebase (usando Google Secrets Manager)
  firebase_api_key = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-api-key", "--project=${local.project_id}")
  firebase_auth_domain = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-auth-domain", "--project=${local.project_id}")
  firebase_project_id = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-project-id", "--project=${local.project_id}")
  firebase_storage_bucket = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-storage-bucket", "--project=${local.project_id}")
  firebase_messaging_sender_id = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-messaging-sender-id", "--project=${local.project_id}")
  firebase_app_id = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-app-id", "--project=${local.project_id}")
  firebase_measurement_id = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=firebase-measurement-id", "--project=${local.project_id}", "--quiet", "||", "echo", "''")
  
  # Configuración de recursos específica del entorno
  min_scale = local.env_vars.environment.min_scale
  max_scale = local.env_vars.environment.max_scale
  cpu_limit = local.env_vars.resources.cpu
  memory_limit = local.env_vars.resources.memory
}