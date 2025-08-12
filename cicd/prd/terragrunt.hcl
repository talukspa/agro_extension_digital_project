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
  
  # Performance optimization variables for agent AA (Production environment)
  min_instance_count_agent_aa = 1  # Higher minimum for production availability
  max_instance_count_agent_aa = 20  # Higher maximum for production scaling
  memory_limit_agent_aa = "4Gi"  # More memory for production workloads
  cpu_limit_agent_aa = "4"  # More CPU for production workloads
  cpu_idle_agent_aa = true  # Keep CPU allocated for better response times in production
  startup_cpu_boost_agent_aa = true
  max_concurrency_agent_aa = 80  # Optimal concurrency for production
  session_affinity_agent_aa = false
  request_timeout_agent_aa = "300s"
  container_port_agent_aa = 8080
  
  # Performance optimization variables for webhook (Production environment)
  min_instance_count_webhook = 1  # Higher minimum for production availability
  max_instance_count_webhook = 10  # Higher maximum for production scaling
  memory_limit_webhook = "2Gi"  # More memory for production
  cpu_limit_webhook = "2"  # More CPU for production
  cpu_idle_webhook = true  # Keep CPU allocated for better response times in production
  startup_cpu_boost_webhook = true
  max_concurrency_webhook = 100  # Higher concurrency for webhook in production
  session_affinity_webhook = false
  request_timeout_webhook = "60s"
  container_port_webhook = 8080
  
  # Execution environment (Gen2 for better performance)
  execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
}

terraform {
  source = "../modules/agent"
}
