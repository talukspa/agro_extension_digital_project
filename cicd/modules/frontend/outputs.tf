output "frontend_service_url" {
  description = "The URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend_service.uri
}

output "frontend_service_name" {
  description = "The name of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend_service.name
}

output "frontend_service_account_email" {
  description = "The email of the frontend service account"
  value       = google_service_account.frontend_app_sa.email
}
