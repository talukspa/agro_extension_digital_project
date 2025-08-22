# Outputs para el módulo de gestión de secretos

output "api_keys_secret_id" {
  description = "ID del secreto de API keys"
  value       = google_secret_manager_secret.api_keys.secret_id
}

output "api_keys_secret_name" {
  description = "Nombre completo del secreto de API keys"
  value       = google_secret_manager_secret.api_keys.name
}

output "jwt_secret_id" {
  description = "ID del secreto JWT"
  value       = google_secret_manager_secret.jwt_secret.secret_id
}

output "jwt_secret_name" {
  description = "Nombre completo del secreto JWT"
  value       = google_secret_manager_secret.jwt_secret.name
}

output "firebase_admin_sdk_secret_id" {
  description = "ID del secreto de Firebase Admin SDK"
  value       = google_secret_manager_secret.firebase_admin_sdk.secret_id
}

output "firebase_admin_sdk_secret_name" {
  description = "Nombre completo del secreto de Firebase Admin SDK"
  value       = google_secret_manager_secret.firebase_admin_sdk.name
}

output "database_config_secret_id" {
  description = "ID del secreto de configuración de base de datos"
  value       = google_secret_manager_secret.database_config.secret_id
}

output "database_config_secret_name" {
  description = "Nombre completo del secreto de configuración de base de datos"
  value       = google_secret_manager_secret.database_config.name
}

output "app_config_secret_id" {
  description = "ID del secreto de configuración de aplicación"
  value       = google_secret_manager_secret.app_config.secret_id
}

output "app_config_secret_name" {
  description = "Nombre completo del secreto de configuración de aplicación"
  value       = google_secret_manager_secret.app_config.name
}

output "secrets_summary" {
  description = "Resumen de secretos creados"
  value = {
    api_keys_secret         = google_secret_manager_secret.api_keys.secret_id
    jwt_secret             = google_secret_manager_secret.jwt_secret.secret_id
    firebase_admin_sdk     = google_secret_manager_secret.firebase_admin_sdk.secret_id
    database_config        = google_secret_manager_secret.database_config.secret_id
    app_config            = google_secret_manager_secret.app_config.secret_id
  }
}
