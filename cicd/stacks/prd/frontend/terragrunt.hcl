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
    bucket   = "agro-extension-digital-prd-tf-state-bucket"
    prefix   = "${path_relative_to_include()}/terraform.tfstate"
    location = "us-central1"
    project  = "agro-extension-digital-prd"
  }
}

# Importar configuración común desde archivos yaml
locals {
  # Cargar configuración base desde archivos yaml
  common_vars = yamldecode(file(find_in_parent_folders("common.yaml")))
  env_vars    = yamldecode(file("../env.yaml"))
  
  # Valores base desde common.yaml
  project_id = local.env_vars.environment.name == "prd" ? local.common_vars.project.prd_id : local.common_vars.project.id
  region     = local.common_vars.gcp.default_region
  environment = local.env_vars.environment.name
  
  # URLs base para frontend
  gar_base_url = "${local.common_vars.containers.registry}/${local.project_id}/${local.common_vars.containers.repository}"
}

inputs = {
  # Configuración base
  project_id  = local.project_id
  environment = local.environment
  location    = local.region
  
  # Frontend configuración
  cloud_run_name_frontend = "frontend-app-${local.environment}"
  gar_image_location_frontend = "${local.gar_base_url}/agent-frontend-app:latest"
  
  # Configuración de recursos específica del entorno
  min_scale = local.env_vars.environment.min_scale
  max_scale = local.env_vars.environment.max_scale
  cpu_limit = local.env_vars.resources.cpu
  memory_limit = local.env_vars.resources.memory
}