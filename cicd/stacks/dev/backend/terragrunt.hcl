include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../modules/backend"
}

# Configuración del backend remoto específico para DEV
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

  # Valores base desde env.yaml (específicos del ambiente)
  project_id  = local.env_vars.project.id
  region      = local.common_vars.gcp.default_region # Común para todos
  environment = local.env_vars.environment.name

  # URLs base para DEV
  facebook_base_url = "https://graph.facebook.com/${local.common_vars.facebook.graph_api_version}/${local.env_vars.facebook.app_id}"

  # Datastores específicos de DEV (resueltos a su path completo)
  datastores = {
    for k, v in local.env_vars.datastores :
    k => "projects/${local.project_id}/locations/global/collections/default_collection/dataStores/${v}"
  }
}

inputs = {
  # Configuración base
  project_id  = local.project_id
  environment = local.environment
  location    = local.region
  region      = local.region

  # Agent AA / PP — solo el app_name (target del webhook) y la facebook app
  estandar_aa_app_name     = "agent_aa_app"
  estandar_aa_facebook_app = local.facebook_base_url
  estandar_pp_app_name     = "agent_pp_app"
  estandar_pp_facebook_app = local.facebook_base_url

  # Webhook
  cloud_run_name_webhook                   = "agent-webhook-${local.environment}"
  service_account_webhook_app              = "agent-webhook-sa-${local.environment}"
  service_account_display_name_webhook_app = "Agent Webhook Service Account DEV"
  # La imagen del webhook vive en el proyecto NPE para ambos entornos
  # (common.containers.project); source explícito para mantener consistencia con PRD.
  gar_image_location_webhook = "${local.common_vars.containers.registry}/${local.common_vars.containers.project}/agro-extension-digital/webhook:latest"

  # CI/CD deployer SA (the identity behind GCP_SA_KEY in deploy-agents.yml).
  # Set cicd.deployer_sa_email in env.yaml to have Terraform grant the deploy
  # IAM; absent/empty → deployer bindings are skipped.
  deployer_sa_email = try(local.env_vars.cicd.deployer_sa_email, "")

  # Agent Runtime config — populated into Secret Manager by the backend
  # module; read by deploy-agents.yml and injected into the engines as env.
  bigquery_dataset            = local.env_vars.bigquery.dataset
  datastore_aa_id             = local.datastores.aa
  datastore_pp_id             = local.datastores.pp
  datastore_guides_id         = local.datastores.guides
  datastore_faq_id            = local.datastores.faq
  datastore_chileprunes_cl_id = local.datastores.chileprunes

  # Secrets y tokens
  # NOTA: estos secrets deben existir en Secret Manager del proyecto antes del
  # primer apply (se leen con run_cmd al evaluar la config). AA y PP son apps de
  # Meta distintas (WABAs distintas) con App Secret propio (inbound) Y access
  # token propio (outbound):
  #   - whatsapp-app-secret-aa / -pp : firma X-Hub-Signature-256 (inbound).
  #     Sin ellos el webhook rechaza los POST de esa app con 403 (fail-closed).
  #   - wsp-token-aa / -pp : Bearer token para enviar (outbound). El token de
  #     una app da 401 contra el número de la otra, por eso es per-app.
  verify_token           = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=webhook-verify-token", "--project=${local.project_id}")
  whatsapp_app_secret_aa = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=whatsapp-app-secret-aa", "--project=${local.project_id}")
  whatsapp_app_secret_pp = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=whatsapp-app-secret-pp", "--project=${local.project_id}")
  wsp_token_aa           = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=wsp-token-aa", "--project=${local.project_id}")
  wsp_token_pp           = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=wsp-token-pp", "--project=${local.project_id}")
  whatsapp_base_url      = local.common_vars.urls.whatsapp_base

  # Configuración específica del entorno desde env.yaml
  log_level         = local.env_vars.environment.log_level
  min_scale         = 0  # Mínimo para dev
  max_scale         = 10 # Máximo para dev
  startup_cpu_boost = true

  # Timeouts HTTP (solo el del cliente WhatsApp ahora; el de agent fue removido
  # en la migración a Agent Runtime — el SDK gestiona sus propios timeouts).
  whatsapp_http_timeout = local.env_vars.timeouts.whatsapp_http
}
