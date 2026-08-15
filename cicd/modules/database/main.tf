# Módulo para gestión de base de datos Firestore
# Este módulo gestiona la base de datos agro-extension-db y sus colecciones

terraform {
  backend "gcs" {}
}

# Recurso principal de Firestore Database
resource "google_firestore_database" "agro_extension_db" {
  project                           = var.project_id
  name                              = var.database_name
  location_id                       = var.database_location
  type                              = "FIRESTORE_NATIVE"
  concurrency_mode                  = "OPTIMISTIC"
  app_engine_integration_mode       = "DISABLED"
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state           = var.delete_protection_enabled ? "DELETE_PROTECTION_ENABLED" : "DELETE_PROTECTION_DISABLED"

  lifecycle {
    prevent_destroy = true
  }
}

# Firestore Security Rules
#
# AUTHZ-CRITICAL: the deployed ruleset is the per-environment RBAC ruleset
# passed via var.firestore_security_rules (the CEL rules text defined inline in
# each stack's terragrunt.hcl). The minimal file is only a fallback for when the
# variable is empty (it grants any authenticated user full read/write and must
# NOT be what reaches prd). Previously this resource hard-coded the minimal file,
# so prod ran effectively wide-open regardless of the per-env rules.
#
# OPERATOR NOTE: `terraform apply` on the database stack changes the LIVE
# Firestore security rules. Validate the resulting ruleset in dev first
# (e.g. Firestore Rules Playground / emulator) before applying to prd.
resource "google_firebaserules_ruleset" "agro_extension_ruleset" {
  project = var.project_id
  source {
    files {
      content = var.firestore_security_rules != "" ? var.firestore_security_rules : file("${path.module}/firestore-security-rules-minimal.rules")
      name    = "firestore.rules"
    }
  }

  depends_on = [google_firestore_database.agro_extension_db]
}

resource "google_firebaserules_release" "agro_extension_release" {
  name         = "cloud.firestore"
  project      = var.project_id
  ruleset_name = google_firebaserules_ruleset.agro_extension_ruleset.name

  depends_on = [google_firebaserules_ruleset.agro_extension_ruleset]
}

# Índices de Firestore para optimizar consultas

# Índice para business_profiles collection
resource "google_firestore_index" "business_profiles_company_name_index" {
  project    = var.project_id
  database   = google_firestore_database.agro_extension_db.name
  collection = "business_profiles"

  fields {
    field_path = "companyName"
    order      = "ASCENDING"
  }

  fields {
    field_path = "isActive"
    order      = "ASCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "business_profiles_certification_status_index" {
  project    = var.project_id
  database   = google_firestore_database.agro_extension_db.name
  collection = "business_profiles"

  fields {
    field_path = "certificationStatus"
    order      = "ASCENDING"
  }

  fields {
    field_path = "assignedAuditorId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "updatedAt"
    order      = "DESCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# Índices para registers collection
resource "google_firestore_index" "registers_business_profile_id_index" {
  project    = var.project_id
  database   = google_firestore_database.agro_extension_db.name
  collection = "registers"

  fields {
    field_path = "businessProfileId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "submissionDate"
    order      = "DESCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "registers_standard_id_index" {
  project    = var.project_id
  database   = google_firestore_database.agro_extension_db.name
  collection = "registers"

  fields {
    field_path = "standardId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "submissionDate"
    order      = "DESCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# Índices para auditors collection
resource "google_firestore_index" "auditors_active_index" {
  project    = var.project_id
  database   = google_firestore_database.agro_extension_db.name
  collection = "auditors"

  fields {
    field_path = "isActive"
    order      = "ASCENDING"
  }

  fields {
    field_path = "certificationLevel"
    order      = "ASCENDING"
  }

  fields {
    field_path = "currentAuditsCount"
    order      = "ASCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# Respaldo automático de la base de datos
# Gated by var.enable_daily_backup (dev sets it false to avoid backup costs).
resource "google_firestore_backup_schedule" "agro_extension_backup" {
  count     = var.enable_daily_backup ? 1 : 0
  project   = var.project_id
  database  = google_firestore_database.agro_extension_db.name
  retention = "${var.backup_retention_days * 24 * 3600}s" # Convert days to seconds

  daily_recurrence {}

  depends_on = [google_firestore_database.agro_extension_db]
}
