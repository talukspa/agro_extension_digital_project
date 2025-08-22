# Frontend Module - Cloud Run Deployment
# Despliega la aplicación Next.js del frontend en Cloud Run

resource "google_service_account" "frontend_app_sa" {
  account_id   = var.service_account_id_frontend
  display_name = var.service_account_display_name_frontend
  project      = var.project_id
  description  = "Service Account for Frontend Cloud Run service - ${var.environment}"
}

# IAM roles para el service account del frontend
resource "google_project_iam_member" "frontend_sa_roles" {
  for_each = toset([
    "roles/storage.objectViewer",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.frontend_app_sa.email}"
}

resource "google_cloud_run_v2_service" "frontend_service" {
  name     = var.cloud_run_name_frontend
  location = var.location
  project  = var.project_id

  template {
    service_account = google_service_account.frontend_app_sa.email

    annotations = {
      "run.googleapis.com/minScale"          = tostring(var.min_scale)
      "run.googleapis.com/startup-cpu-boost" = tostring(var.startup_cpu_boost)
    }
    
    containers {
      image = var.gar_image_location_frontend
      
      # Variables de entorno para Firebase Auth
      env {
        name  = "NODE_ENV"
        value = "production"
      }

      env {
        name  = "NEXT_PUBLIC_APP_ENV"
        value = var.environment
      }

      env {
        name  = "NEXT_PUBLIC_FIREBASE_API_KEY"
        value = var.firebase_api_key
      }

      env {
        name  = "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN"
        value = var.firebase_auth_domain
      }

      env {
        name  = "NEXT_PUBLIC_FIREBASE_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET"
        value = var.firebase_storage_bucket
      }

      env {
        name  = "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID"
        value = var.firebase_messaging_sender_id
      }

      env {
        name  = "NEXT_PUBLIC_FIREBASE_APP_ID"
        value = var.firebase_app_id
      }

      env {
        name  = "NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID"
        value = var.firebase_measurement_id
      }

      # URLs de los servicios backend
      env {
        name  = "NEXT_PUBLIC_AGENT_AA_URL"
        value = var.agent_aa_service_url
      }

      env {
        name  = "NEXT_PUBLIC_WEBHOOK_URL"
        value = var.webhook_service_url
      }

      env {
        name  = "FIRESTORE_DATABASE_ID"
        value = var.firestore_database_id
      }
      
      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
        cpu_idle = true
      }
      
      ports {
        container_port = 3000
        name          = "http1"
      }

      # Health checks
      startup_probe {
        http_get {
          path = "/"
          port = 3000
        }
        initial_delay_seconds = 10
        timeout_seconds      = 5
        period_seconds       = 10
        failure_threshold    = 3
      }

      liveness_probe {
        http_get {
          path = "/"
          port = 3000
        }
        initial_delay_seconds = 30
        timeout_seconds      = 5
        period_seconds       = 30
        failure_threshold    = 3
      }
    }
    
    scaling {
      min_instance_count = var.min_scale
      max_instance_count = var.max_scale
    }
  }

  ingress = "INGRESS_TRAFFIC_ALL"
  
  labels = {
    environment = var.environment
    component   = "frontend"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_iam_member.frontend_sa_roles
  ]
}

resource "google_cloud_run_v2_service_iam_binding" "noauth_frontend" {
  name     = google_cloud_run_v2_service.frontend_service.name
  project  = var.project_id
  location = var.location
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}