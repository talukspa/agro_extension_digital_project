include "root" {
  path = find_in_parent_folders("root.hcl")
}

remote_state {
  backend = "gcs"
  config = {
    bucket  = "agro-extension-digital-prd-tf-state-bucket"
    project = "agro-extension-digital-prd"
    prefix  = "${path_relative_to_include()}/terraform.tfstate"
    location = "us-central1"
  }
}

inputs = {
  project_id = "agro-extension-digital-prd" # Verified
  environment = "prd" # Changed from dev
  location = "us-central1"
  cloud_run_name_agent_aa = "agent-aa-prd" # Added -prd
  cloud_run_name_agent_pp = "agent-pp-prd" # Added -prd
  service_account_id_agent_aa = "agent-aa-sa-prd" # Added -prd
  service_account_display_name_agent_aa = "Agent AA Service Account PRD" # Added PRD
  service_account_id_agent_pp = "agent-pp-sa-prd" # Added -prd
  service_account_display_name_agent_pp = "Agent PP Service Account PRD" # Added PRD
  region = "us-central1"
  # GAR image locations can remain the same if :latest is used for PRD, or be different if specific PRD tags are used. Assuming same for now.
  gar_image_location_agent_aa = "us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-aa-app:latest"
  gar_image_location_agent_pp = "us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-pp-app:latest"
  google_genai_use_vertexai = "TRUE"
  google_cloud_project = "agro-extension-digital-prd" # Verified
  google_cloud_location = "us-central1"
  service_name = "agent-prd" # Changed from agent-dev

  # Datastore IDs from dev are preserved as per instruction (these might need real PRD values later)
  datastore_aa_id = "projects/agro-extension-digital-prd/locations/global/collections/default_collection/dataStores/0001-adecuacion-agroindustrial_1749006214130"
  datastore_pp_id = "projects/agro-extension-digital-prd/locations/global/collections/default_collection/dataStores/0001-produccion-primaria_1749005766833"
  datastore_guides_id = "projects/agro-extension-digital-prd/locations/global/collections/default_collection/dataStores/0001-guias_1749005972756"
  datastore_faq_id = "projects/agro-extension-digital-prd/locations/global/collections/default_collection/dataStores/0001-faq_1749006101377"
  datastore_chileprunes_cl_id = "projects/agro-extension-digital-prd/locations/global/collections/default_collection/dataStores/0001-chileprunes-cl_1749005569113"

  service_account_webhook_app = "agent-webhook-sa-prd" # Added -prd
  service_account_display_name_webhook_app = "Agent Webhook Service Account PRD" # Added PRD

  # Secrets - set to placeholder values for PRD
  estandar_aa_facebook_app = "https://graph.facebook.com/v22.0/692894087240362"
  estandar_pp_facebook_app = "https://graph.facebook.com/v22.0/619189944620159"
  verify_token = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=webhook-verify-token", "--project=agro-extension-digital-prd")

  # GAR image for webhook - assuming same :latest tag for now
  gar_image_location_webhook = "us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-webhook-app:latest"
  cloud_run_name_webhook = "agent-webhook-prd" # Added -prd

  estandar_aa_app_name = "agent_aa_app" # Added _prd
  estandar_pp_app_name = "agent_pp_app" # Added _prd

  wsp_token = run_cmd("gcloud", "secrets", "versions", "access", "latest", "--secret=wsp-token", "--project=agro-extension-digital-prd")
  whatsapp_base_url = "https://graph.facebook.com/v22.0"
  log_level = "INFO"  # Production environment uses INFO level for performance and log volume control
  bigquery_dataset = "agro_extension_digital_prd_dataset"  # BigQuery dataset for production environment
  
  # Cloud Run min instances for PRD (avoid cold starts)
  min_scale = 1
  # Cloud Run max instances for PRD (capacity cap)
  max_scale = 20

  # HTTP timeouts (seconds) for webhook outbound calls
  agent_http_timeout = "90"
  whatsapp_http_timeout = "90"
}

terraform {
  source = "../modules/agent"
}
