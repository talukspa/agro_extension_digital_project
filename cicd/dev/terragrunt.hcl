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
  
  # Performance optimization variables for agent AA (Development environment)
  min_instance_count_agent_aa = 1
  max_instance_count_agent_aa = 5
  memory_limit_agent_aa = "2Gi"
  cpu_limit_agent_aa = "2"
  cpu_idle_agent_aa = false
  startup_cpu_boost_agent_aa = true
  max_concurrency_agent_aa = 50  # Lower for dev environment
  session_affinity_agent_aa = false
  request_timeout_agent_aa = "300s"
  container_port_agent_aa = 8080
  
  # Performance optimization variables for webhook (Development environment)
  min_instance_count_webhook = 1
  max_instance_count_webhook = 3
  memory_limit_webhook = "1Gi"
  cpu_limit_webhook = "1"
  cpu_idle_webhook = false
  startup_cpu_boost_webhook = true
  max_concurrency_webhook = 80  # Higher concurrency for webhook
  session_affinity_webhook = false
  request_timeout_webhook = "60s"
  container_port_webhook = 8080
  
  # Execution environment (Gen2 for better performance)
  execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
}

terraform {
  source = "../modules/agent"
}
