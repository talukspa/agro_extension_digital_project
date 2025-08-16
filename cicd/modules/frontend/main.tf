resource "google_service_account" "frontend_app_sa" {
  account_id   = "${var.cloud_run_name_frontend}-sa"
  display_name = "${var.cloud_run_name_frontend} Service Account"
  project      = var.project_id
}

resource "google_cloud_run_v2_service" "frontend_service" {
  name     = var.cloud_run_name_frontend
  location = var.location
  project  = var.project_id

  template {
    containers {
      image = var.gar_image_location_frontend
    }
    service_account = google_service_account.frontend_app_sa.email
  }

  ingress = "INGRESS_TRAFFIC_ALL"
}

resource "google_cloud_run_v2_service_iam_binding" "noauth_frontend" {
  name     = google_cloud_run_v2_service.frontend_service.name
  project  = var.project_id
  location = var.location
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}