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
  project_id = local.env_vars.project.id
  region     = local.common_vars.gcp.default_region
  environment = local.env_vars.environment.name
  
  # URLs base para PRD
  facebook_aa_url = "https://graph.facebook.com/${local.common_vars.facebook.graph_api_version}/${local.env_vars.facebook.aa_app_id}"
  facebook_pp_url = "https://graph.facebook.com/${local.common_vars.facebook.graph_api_version}/${local.env_vars.facebook.pp_app_id}"
  gar_base_url    = "${local.common_vars.containers.registry}/${local.common_vars.containers.project}/${local.common_vars.containers.repository}"
  
  # Datastores específicos de PRD
  datastores = {
    for k, v in local.env_vars.datastores : k => "projects/${local.project_id}/locations/global/collections/default_collection/dataStores/${v}"
  }
}

inputs = {
  # Configuración base
  project_id  = local.project_id
  environment = local.environment
  location    = local.region
  region      = local.region
  
  # Google Cloud configuración
  google_genai_use_vertexai = "TRUE"
  google_cloud_project      = local.project_id
  google_cloud_location     = local.region
  
  # Agent AA configuración
  cloud_run_name_agent_aa           = try(local.env_vars.service_names.agent_aa, "agent-aa-${local.environment}")
  service_account_id_agent_aa       = "agent-aa-sa-${local.environment}"
  service_account_display_name_agent_aa     = "Agent AA Service Account PRD"
  gar_image_location_agent_aa       = "${local.gar_base_url}/agent-aa-app:latest"
  estandar_aa_app_name                = "agent_aa_app"
  estandar_aa_facebook_app = local.facebook_aa_url
  
  # Agent PP configuración
  cloud_run_name_agent_pp           = "agent-pp-${local.environment}"
  service_account_id_agent_pp       = "agent-pp-sa-${local.environment}"
  service_account_display_name_agent_pp     = "Agent PP Service Account PRD"
  gar_image_location_agent_pp       = "${local.gar_base_url}/agent-pp-app:latest"
  estandar_pp_app_name                = "agent_pp_app"
  estandar_pp_facebook_app   = local.facebook_pp_url
  
  # Webhook configuración
  cloud_run_name_webhook           = try(local.env_vars.service_names.webhook, "agent-webhook-${local.environment}")
  service_account_webhook_app       = "agent-webhook-sa-${local.environment}"
  service_account_display_name_webhook_app     = "Agent Webhook Service Account PRD"
  gar_image_location_webhook       = "${local.gar_base_url}/agent-webhook-app:latest"
  
  # Service name
  service_name = "agent-${local.environment}"
  
  # Datastores específicos de PRD
  datastore_aa_id          = local.datastores.aa
  datastore_pp_id          = local.datastores.pp
  datastore_guides_id      = local.datastores.guides
  datastore_faq_id         = local.datastores.faq
  datastore_chileprunes_cl_id = local.datastores.chileprunes
  
  # Secrets y tokens (proyecto PRD)
  wsp_token                = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=wsp-token", "--project=${local.project_id}")
  verify_token            = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=webhook-verify-token", "--project=${local.project_id}")
  whatsapp_base_url        = local.common_vars.urls.whatsapp_base
  
  # Configuración específica del entorno desde env.yaml
  log_level                = local.env_vars.environment.log_level
  bigquery_dataset         = local.env_vars.bigquery.dataset
  min_scale               = local.env_vars.environment.min_scale
  max_scale               = local.env_vars.environment.max_scale
  
  # Timeouts HTTP desde env.yaml
  agent_http_timeout       = local.env_vars.timeouts.agent_http
  whatsapp_http_timeout    = local.env_vars.timeouts.whatsapp_http
}
