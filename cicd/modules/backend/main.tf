resource "google_service_account" "agent_aa_app" {
  account_id   = var.service_account_id_agent_aa
  display_name = var.service_account_display_name_agent_aa
  project      = var.project_id
}

resource "google_service_account" "webhook_app_sa" {
  account_id   = var.service_account_webhook_app
  display_name = var.service_account_display_name_webhook_app
  project      = var.project_id
}

resource "google_project_iam_member" "agent_aa_sa_role" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_aa_app.email}"
}

resource "google_project_iam_member" "agent_aa_sa_role_discovery" {
  project = var.project_id
  role    = "roles/discoveryengine.user"
  member  = "serviceAccount:${google_service_account.agent_aa_app.email}"
}

# Los siguientes permisos de BigQuery no existen en el environment actual
# Se pueden habilitar si son necesarios
# resource "google_project_iam_member" "agent_aa_sa_role_bigquery" {
#   project = var.project_id
#   role    = "roles/bigquery.dataViewer"
#   member  = "serviceAccount:${google_service_account.agent_aa_app.email}"
# }

# resource "google_project_iam_member" "agent_aa_sa_role_bigquery_job" {
#   project = var.project_id
#   role    = "roles/bigquery.jobUser"
#   member  = "serviceAccount:${google_service_account.agent_aa_app.email}"
# }


resource "google_cloud_run_v2_service" "cloud_run_name_agent_aa" {
  name     = var.cloud_run_name_agent_aa
  location = var.region
  project  = var.project_id

  template {
    annotations = {
      "run.googleapis.com/minScale"          = tostring(var.min_scale)
      "run.googleapis.com/startup-cpu-boost" = tostring(var.startup_cpu_boost)
    }

    scaling {
      min_instance_count = var.min_scale
      max_instance_count = var.max_scale
    }

    containers {
      image = var.gar_image_location_agent_aa

      resources {
        limits = {
          memory = "1Gi"
        }
      }

      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = var.google_genai_use_vertexai
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.google_cloud_project
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.google_cloud_location
      }
      env {
        name  = "SERVICE_NAME"
        value = var.service_name
      }
      env {
        name  = "DATASTORE_AA_ID"
        value = var.datastore_aa_id
      }
      env {
        name  = "DATASTORE_PP_ID"
        value = var.datastore_pp_id
      }
      env {
        name  = "DATASTORE_GUIDES_ID"
        value = var.datastore_guides_id
      }
      env {
        name  = "DATASTORE_FAQ_ID"
        value = var.datastore_faq_id
      }
      env {
        name  = "DATASTORE_CHILEPRUNES_CL_ID"
        value = var.datastore_chileprunes_cl_id
      }
      env {
        name  = "BIGQUERY_DATASET"
        value = var.bigquery_dataset
      }
    }

    service_account = google_service_account.agent_aa_app.email
  }

  ingress = "INGRESS_TRAFFIC_ALL"

}

resource "google_cloud_run_v2_service" "cloud_run_name_webhook" {
  name     = var.cloud_run_name_webhook
  location = var.region
  project  = var.project_id

  template {
    annotations = {
      "run.googleapis.com/minScale"          = tostring(var.min_scale)
      "run.googleapis.com/startup-cpu-boost" = tostring(var.startup_cpu_boost)
    }

    scaling {
      min_instance_count = var.min_scale
      max_instance_count = var.max_scale
    }

    containers {
      image = var.gar_image_location_webhook

      env {
        name  = "APP_URL"
        value = google_cloud_run_v2_service.cloud_run_name_agent_aa.uri
      }
      env {
        name  = "AGENT_HTTP_TIMEOUT"
        value = var.agent_http_timeout
      }
      env {
        name  = "WHATSAPP_HTTP_TIMEOUT"
        value = var.whatsapp_http_timeout
      }
      env {
        name  = "ESTANDAR_AA_FACEBOOK_APP"
        value = var.estandar_aa_facebook_app
      }
      env {
        name  = "ESTANDAR_PP_FACEBOOK_APP"
        value = var.estandar_pp_facebook_app
      }
      env {
        name  = "VERIFY_TOKEN"
        value = var.verify_token
      }
      env {
        name  = "ESTANDAR_AA_APP_NAME"
        value = var.estandar_aa_app_name
      }
      env {
        name  = "ESTANDAR_PP_APP_NAME"
        value = var.estandar_pp_app_name
      }

      env {
        name  = "WSP_TOKEN"
        value = var.wsp_token
      }

      env {
        name  = "WHATSAPP_BASE_URL"
        value = var.whatsapp_base_url
      }

      env {
        name  = "LOG_LEVEL"
        value = var.log_level
      }
    }

    service_account = google_service_account.webhook_app_sa.email
  }

  ingress    = "INGRESS_TRAFFIC_ALL"
  depends_on = [google_cloud_run_v2_service.cloud_run_name_agent_aa]
}


resource "google_cloud_run_v2_service_iam_binding" "noauth_webhook" {
  name     = google_cloud_run_v2_service.cloud_run_name_webhook.name
  project  = var.project_id
  location = var.region
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}

resource "google_cloud_run_v2_service_iam_member" "webhook_invokes_agent_aa" {
  name     = google_cloud_run_v2_service.cloud_run_name_agent_aa.name
  project  = var.project_id
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.webhook_app_sa.email}"
}

terraform {
  backend "gcs" {}
}

output "agent_aa_service_url" {
  description = "The URL of the agent-aa Cloud Run service."
  value       = google_cloud_run_v2_service.cloud_run_name_agent_aa.uri
}
