# Outputs del módulo de base de datos

output "database_name" {
  description = "Nombre de la base de datos Firestore creada"
  value       = google_firestore_database.agro_extension_db.name
}

output "database_id" {
  description = "ID completo de la base de datos Firestore"
  value       = google_firestore_database.agro_extension_db.id
}

output "database_location" {
  description = "Ubicación de la base de datos Firestore"
  value       = google_firestore_database.agro_extension_db.location_id
}

output "database_project" {
  description = "Proyecto donde se creó la base de datos"
  value       = google_firestore_database.agro_extension_db.project
}

output "database_app_engine_integration_mode" {
  description = "Modo de integración con App Engine"
  value       = google_firestore_database.agro_extension_db.app_engine_integration_mode
}

output "database_type" {
  description = "Tipo de base de datos Firestore"
  value       = google_firestore_database.agro_extension_db.type
}

output "database_connection_string" {
  description = "String de conexión para la base de datos"
  value       = "projects/${google_firestore_database.agro_extension_db.project}/databases/${google_firestore_database.agro_extension_db.name}"
}
