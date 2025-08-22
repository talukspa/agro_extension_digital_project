# Configuración de Terragrunt para gestión de secretos en DEV

include "root" {
  path = find_in_parent_folders("root.hcl")
}

# Dependencias: requiere que la base de datos esté desplegada
dependency "database" {
  config_path = "../database"
  
  mock_outputs = {
    database_name = "agro-extension-db"
    database_location = "us-central1"
    database_project = "agro-extension-digital-npe"
  }
}

terraform {
  source = "../../../modules/secrets"
}

# Configuración del backend remoto específica para DEV Secrets
remote_state {
  backend = "gcs"
  config = {
    bucket   = yamldecode(file("../env.yaml")).terraform_state.bucket
    project  = yamldecode(file("../env.yaml")).project.id
    prefix   = "${path_relative_to_include()}/terraform.tfstate"
    location = yamldecode(file(find_in_parent_folders("common.yaml"))).gcp.default_region
  }
}

inputs = {
  project_id        = "agro-extension-digital-npe"
  environment       = "dev"
  database_name     = dependency.database.outputs.database_name
  database_location = dependency.database.outputs.database_location
  
  # API Keys (estas se deben configurar desde variables de entorno)
  firebase_api_key = get_env("FIREBASE_API_KEY", "placeholder-firebase-key")
  whatsapp_api_token = get_env("WHATSAPP_API_TOKEN", "placeholder-whatsapp-token")
  openai_api_key = get_env("OPENAI_API_KEY", "")
  
  # Firebase Admin SDK (se debe configurar desde variable de entorno)
  firebase_admin_sdk_key = get_env("FIREBASE_ADMIN_SDK_KEY", "{\"type\": \"service_account\", \"placeholder\": true}")
  
  # Configuración de aplicación para DEV
  cors_origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost:8080",
    "https://agro-extension-dev.web.app"
  ]
  log_level = "debug"
  session_timeout = 7200  # 2 horas para desarrollo
}
