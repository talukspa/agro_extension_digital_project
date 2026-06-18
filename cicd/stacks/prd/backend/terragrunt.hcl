include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../modules/backend"
}

# Configuración del backend remoto específico para PRD
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

  # Valores base desde env.yaml - configuración específica de PRD
  project_id  = local.env_vars.project.id
  region      = local.common_vars.gcp.default_region
  environment = local.env_vars.environment.name

  # URLs base para PRD
  facebook_aa_url = "https://graph.facebook.com/${local.common_vars.facebook.graph_api_version}/${local.env_vars.facebook.aa_app_id}"
  facebook_pp_url = "https://graph.facebook.com/${local.common_vars.facebook.graph_api_version}/${local.env_vars.facebook.pp_app_id}"
}

inputs = {
  # Configuración base
  project_id  = local.project_id
  environment = local.environment
  location    = local.region
  region      = local.region

  # Agent AA / PP — solo el app_name (target del webhook) y la facebook app
  estandar_aa_app_name     = "agent_aa_app"
  estandar_aa_facebook_app = local.facebook_aa_url
  estandar_pp_app_name     = "agent_pp_app"
  estandar_pp_facebook_app = local.facebook_pp_url

  # Webhook
  cloud_run_name_webhook                   = "agent-webhook-${local.environment}"
  service_account_webhook_app              = "agent-webhook-sa-${local.environment}"
  service_account_display_name_webhook_app = "Agent Webhook Service Account PRD"
  gar_image_location_webhook               = "us-central1-docker.pkg.dev/${local.project_id}/agro-extension-digital/webhook:latest"

  # Secrets y tokens (proyecto PRD)
  wsp_token         = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=wsp-token", "--project=${local.project_id}")
  verify_token      = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=webhook-verify-token", "--project=${local.project_id}")
  whatsapp_base_url = local.common_vars.urls.whatsapp_base

  # Configuración específica del entorno desde env.yaml
  log_level         = local.env_vars.environment.log_level
  min_scale         = local.env_vars.environment.min_scale
  max_scale         = local.env_vars.environment.max_scale
  startup_cpu_boost = true

  # Timeouts HTTP (solo WhatsApp; agent_http_timeout fue removido en la
  # migración a Agent Runtime — el SDK gestiona sus propios timeouts).
  whatsapp_http_timeout = local.env_vars.timeouts.whatsapp_http
}
