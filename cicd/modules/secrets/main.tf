# Módulo para gestión de secretos en Secret Manager
# Este módulo gestiona los secretos necesarios para AuthN/AuthZ

terraform {
  backend "gcs" {}
}

# API Keys Secret for external services
resource "google_secret_manager_secret" "api_keys" {
  project   = var.project_id
  secret_id = "agro-extension-api-keys"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    component   = "auth"
    managed_by  = "terraform"
  }
}

resource "google_secret_manager_secret_version" "api_keys" {
  secret = google_secret_manager_secret.api_keys.name

  secret_data = jsonencode({
    firebase_api_key    = var.firebase_api_key
    whatsapp_api_token = var.whatsapp_api_token
    openai_api_key     = var.openai_api_key != "" ? var.openai_api_key : "placeholder"
  })

  depends_on = [google_secret_manager_secret.api_keys]
}

# JWT Secret for token signing
resource "google_secret_manager_secret" "jwt_secret" {
  project   = var.project_id
  secret_id = "agro-extension-jwt-secret"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    component   = "auth"
    managed_by  = "terraform"
  }
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret = google_secret_manager_secret.jwt_secret.name

  secret_data = var.jwt_secret != "" ? var.jwt_secret : random_password.jwt_secret.result

  depends_on = [google_secret_manager_secret.jwt_secret]
}

# Generate JWT secret if not provided
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Firebase Admin SDK Secret
resource "google_secret_manager_secret" "firebase_admin_sdk" {
  project   = var.project_id
  secret_id = "agro-extension-firebase-admin-sdk"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    component   = "auth"
    managed_by  = "terraform"
  }
}

resource "google_secret_manager_secret_version" "firebase_admin_sdk" {
  secret = google_secret_manager_secret.firebase_admin_sdk.name

  secret_data = var.firebase_admin_sdk_key

  depends_on = [google_secret_manager_secret.firebase_admin_sdk]
}

# Database Connection Secret
resource "google_secret_manager_secret" "database_config" {
  project   = var.project_id
  secret_id = "agro-extension-database-config"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    component   = "database"
    managed_by  = "terraform"
  }
}

resource "google_secret_manager_secret_version" "database_config" {
  secret = google_secret_manager_secret.database_config.name

  secret_data = jsonencode({
    project_id    = var.project_id
    database_name = var.database_name
    location      = var.database_location
  })

  depends_on = [google_secret_manager_secret.database_config]
}

# Application Configuration Secret
resource "google_secret_manager_secret" "app_config" {
  project   = var.project_id
  secret_id = "agro-extension-app-config"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    component   = "app"
    managed_by  = "terraform"
  }
}

resource "google_secret_manager_secret_version" "app_config" {
  secret = google_secret_manager_secret.app_config.name

  secret_data = jsonencode({
    environment     = var.environment
    app_name       = "agro-extension-digital"
    cors_origins   = var.cors_origins
    log_level      = var.log_level
    session_timeout = var.session_timeout
  })

  depends_on = [google_secret_manager_secret.app_config]
}
