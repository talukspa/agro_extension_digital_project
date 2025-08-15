include "root" {
  path = find_in_parent_folders("root.hcl")
}

remote_state {
  backend = "gcs"
  config = {
    bucket  = "agro-extension-digital-npe-tf-state-bucket"
    project = "agro-extension-digital-npe"
    prefix  = "${path_relative_to_include()}/terraform.tfstate"
    location = "us-central1"
  }
}

inputs = {
  project_id = "agro-extension-digital-npe"
  environment = "dev"
  location = "us-central1"
  cloud_run_name_agent_aa = "agent-dev"
  cloud_run_name_agent_pp = "agent-pp-dev"
  service_account_id_agent_aa = "agent-aa-sa-dev"
  service_account_display_name_agent_aa = "Agent AA Service Account"
  service_account_id_agent_pp = "agent-pp-sa-dev"
  service_account_display_name_agent_pp = "Agent PP Service Account"
  region = "us-central1"
  gar_image_location_agent_aa = "us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-aa-app:latest"
  gar_image_location_agent_pp = "us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-pp-app:latest"
  google_genai_use_vertexai = "TRUE"
  google_cloud_project = "agro-extension-digital-npe"
  google_cloud_location = "us-central1"
  service_name = "agent-dev"
  datastore_aa_id = "projects/agro-extension-digital-npe/locations/global/collections/default_collection/dataStores/0001-adecuacion-agroindustrial_1745450263959"
  datastore_pp_id = "projects/agro-extension-digital-npe/locations/global/collections/default_collection/dataStores/0001-produccion-primaria_1745450565038"
  datastore_guides_id = "projects/agro-extension-digital-npe/locations/global/collections/default_collection/dataStores/0001-guias_1745450505033"
  datastore_faq_id = "projects/agro-extension-digital-npe/locations/global/collections/default_collection/dataStores/0001-faq_1745450327301"
  datastore_chileprunes_cl_id = "projects/agro-extension-digital-npe/locations/global/collections/default_collection/dataStores/0001-chileprunes-cl_1748096068703"
  service_account_webhook_app = "agent-webhook-sa-dev"
  service_account_display_name_webhook_app = "Agent Webhook Service Account"
  estandar_aa_facebook_app = "https://graph.facebook.com/v22.0/586486637888050"
  estandar_pp_facebook_app = "https://graph.facebook.com/v22.0/586486637888050"
  verify_token = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=webhook-verify-token", "--project=agro-extension-digital-npe")
  gar_image_location_webhook = "us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-webhook-app:latest"
  cloud_run_name_webhook = "agent-webhook-dev"
  estandar_aa_app_name = "agent_aa_app"
  estandar_pp_app_name = "agent_pp_app"
  wsp_token = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=wsp-token", "--project=agro-extension-digital-npe")
  whatsapp_base_url = "https://graph.facebook.com/v22.0"
  log_level = "DEBUG"  # Development environment uses DEBUG level for detailed logging
  bigquery_dataset = "sandbox_rsolar"  # BigQuery dataset for development environment
  
  # Cloud Run min instances for DEV (allow scale-to-zero)
  min_scale = 0

  # HTTP timeouts (seconds) for webhook outbound calls
  agent_http_timeout = "30"
  whatsapp_http_timeout = "30"
}

terraform {
  source = "../modules/agent"
}
