resource "google_service_account" "webhook_app_sa" {
  account_id   = var.service_account_webhook_app
  display_name = var.service_account_display_name_webhook_app
  project      = var.project_id
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

      # Required by the Vertex AI Agent Runtime client in agent_client.py.
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
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

  ingress = "INGRESS_TRAFFIC_ALL"
}


resource "google_cloud_run_v2_service_iam_binding" "noauth_webhook" {
  name     = google_cloud_run_v2_service.cloud_run_name_webhook.name
  project  = var.project_id
  location = var.region
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}

# --------------------------------------------------------------------
# Agent Runtime (Vertex AI / Gemini Enterprise Agent Platform)
#
# These are the additive Agent Runtime resources. NOTE: the old Cloud Run agent
# service, its service account, and their IAM bindings have already been REMOVED
# from this Terraform config. They still exist live and in state, so the NEXT
# `terraform apply` on this backend stack DESTROYS them (a hard cutover) — it
# does NOT leave them "in place until post-soak". The runbook expects exactly 5
# destroys here (old agent service + SA + 2 role bindings + the
# webhook→agent Cloud Run invoker binding).
#
# OPERATOR DECISION before applying (do ONE of these — Terraform will not):
#   (A) Preserve for rollback: `terraform state rm` the old agent addresses
#       (e.g. the old google_cloud_run_v2_service / google_service_account /
#       google_*_iam_* for the agent) BEFORE apply, so they survive as
#       unmanaged resources you can fall back to during the soak window; OR
#   (B) Accept the hard cutover: apply as-is and rely on the runbook's
#       image/traffic rollback path if the new engines misbehave.
# Do NOT run `terraform state rm` from CI — it is a manual, deliberate step.
# --------------------------------------------------------------------

resource "google_storage_bucket" "agent_engine_staging" {
  name                        = "${var.project_id}-agent-engine-staging"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false
  # 30-day cleanup of the transient code archives deploy.py uploads. No prefix
  # filter: the Agent Engine SDK's staging object path is not a stable public
  # contract, so a guessed prefix could silently match nothing and disable the
  # rule. The bucket holds only transient staging artifacts today, so an
  # unfiltered age rule is safe.
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  # Guard the bucket itself against accidental `terraform destroy`.
  lifecycle {
    prevent_destroy = true
  }
}

resource "google_service_account" "agent_aa_runtime" {
  account_id   = "agent-aa-runtime"
  display_name = "Agent AA — Agent Runtime SA"
  project      = var.project_id
}

resource "google_service_account" "agent_pp_runtime" {
  account_id   = "agent-pp-runtime"
  display_name = "Agent PP — Agent Runtime SA"
  project      = var.project_id
}

locals {
  runtime_roles = [
    "roles/aiplatform.user",
    "roles/discoveryengine.viewer",
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser",
    "roles/bigquery.readSessionUser",
    "roles/cloudtrace.agent",
    "roles/logging.logWriter",
  ]
  runtime_sas = {
    aa = google_service_account.agent_aa_runtime.email
    pp = google_service_account.agent_pp_runtime.email
  }
  runtime_bindings = {
    for pair in setproduct(keys(local.runtime_sas), local.runtime_roles) :
    "${pair[0]}-${pair[1]}" => { sa = local.runtime_sas[pair[0]], role = pair[1] }
  }
}

resource "google_project_iam_member" "runtime_bindings" {
  for_each = local.runtime_bindings
  project  = var.project_id
  role     = each.value.role
  member   = "serviceAccount:${each.value.sa}"
}

# CUTOVER ORDERING (CRITICAL): these two secrets are created here as EMPTY
# containers — no secret version. Their versions (the reasoningEngine resource
# names) are seeded by `deploy.py`, run via `.github/workflows/deploy-agents.yml`.
# The public webhook resolves the engine handle with `access latest` on these
# secrets on every inbound message. Therefore deploy-agents.yml MUST run and
# succeed (Phase 2 of the runbook) BEFORE the webhook goes live / receives
# traffic — otherwise `access latest` returns NOT_FOUND and the public webhook
# 500s on every request. Sequence: (1) apply this backend stack, (2) run
# deploy-agents.yml to seed the engine-name secret versions, (3) deploy/redeploy
# the webhook image. See docs/superpowers/runbook-agent-runtime-deploy.md.
resource "google_secret_manager_secret" "engine_aa_name" {
  secret_id = "engine-aa-resource-name"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "engine_pp_name" {
  secret_id = "engine-pp-resource-name"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "webhook_reads_engine_aa" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.engine_aa_name.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.webhook_app_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "webhook_reads_engine_pp" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.engine_pp_name.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.webhook_app_sa.email}"
}

# TODO(iam-scope): project-level roles/aiplatform.user is broader than ideal —
# it grants the whole AI Platform surface, not just the two engines. Vertex AI
# Agent Engine has no resource-level IAM today, so this is currently
# unavoidable; scope down to the specific engines once Google ships
# engine-scoped bindings.
resource "google_project_iam_member" "webhook_invokes_engines" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.webhook_app_sa.email}"
}

# --------------------------------------------------------------------
# CI/CD deployer service-account bindings (deploy-agents.yml → GCP_SA_KEY).
# deploy.py performs ~5 privileged actions; codifying them here keeps a fresh
# env reproducible from Terraform instead of relying on manual one-off grants.
# Inert until var.deployer_sa_email is set (per-env, from env.yaml).
# --------------------------------------------------------------------
locals {
  deployer_enabled = var.deployer_sa_email != ""
  deployer_member  = "serviceAccount:${var.deployer_sa_email}"
}

# Create/update reasoning engines. NOTE: aiplatform.user covers create/update
# (the only operations deploy.py performs). If engine creation ever returns
# PERMISSION_DENIED, escalate just this binding to roles/aiplatform.admin.
resource "google_project_iam_member" "deployer_aiplatform" {
  count   = local.deployer_enabled ? 1 : 0
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = local.deployer_member
}

# Upload the staged code archive during agent_engines.create().
resource "google_storage_bucket_iam_member" "deployer_staging" {
  count  = local.deployer_enabled ? 1 : 0
  bucket = google_storage_bucket.agent_engine_staging.name
  role   = "roles/storage.objectAdmin"
  member = local.deployer_member
}

# actAs the runtime SAs (agent_engines.create(service_account=…) requires it).
resource "google_service_account_iam_member" "deployer_acts_as_runtime" {
  for_each = local.deployer_enabled ? {
    aa = google_service_account.agent_aa_runtime.name
    pp = google_service_account.agent_pp_runtime.name
  } : {}
  service_account_id = each.value
  role               = "roles/iam.serviceAccountUser"
  member             = local.deployer_member
}

# Write the resolved engine resource names back to Secret Manager
# (deploy.py:write_secret → add_secret_version).
resource "google_secret_manager_secret_iam_member" "deployer_writes_engine_names" {
  for_each = local.deployer_enabled ? {
    aa = google_secret_manager_secret.engine_aa_name.secret_id
    pp = google_secret_manager_secret.engine_pp_name.secret_id
  } : {}
  project   = var.project_id
  secret_id = each.value
  role      = "roles/secretmanager.secretVersionAdder"
  member    = local.deployer_member
}

# Read the runtime-config secrets in the "Load runtime env vars" workflow step.
resource "google_secret_manager_secret_iam_member" "deployer_reads_config" {
  for_each  = local.deployer_enabled ? local.runtime_config_secrets : {}
  project   = var.project_id
  secret_id = google_secret_manager_secret.runtime_config[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = local.deployer_member
}

# --------------------------------------------------------------------
# Runtime-config Secret Manager secrets read by deploy-agents.yml and
# by the engines at run time. Values come from per-env env.yaml.
#
# These hold non-confidential runtime config (datastore IDs, dataset name)
# that already lives in committed env.yaml — they are NOT secrets in the
# confidentiality sense. Secret Manager is used here only for a uniform,
# rotatable delivery channel into the engines, not to hide the values.
# --------------------------------------------------------------------
locals {
  runtime_config_secrets = {
    "datastore-aa-id"             = var.datastore_aa_id
    "datastore-pp-id"             = var.datastore_pp_id
    "datastore-guides-id"         = var.datastore_guides_id
    "datastore-faq-id"            = var.datastore_faq_id
    "datastore-chileprunes-cl-id" = var.datastore_chileprunes_cl_id
    "bigquery-dataset"            = var.bigquery_dataset
  }
}

resource "google_secret_manager_secret" "runtime_config" {
  for_each  = local.runtime_config_secrets
  project   = var.project_id
  secret_id = each.key
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "runtime_config" {
  for_each    = local.runtime_config_secrets
  secret      = google_secret_manager_secret.runtime_config[each.key].id
  secret_data = each.value
}

# Both runtime SAs need to read these secrets at engine startup.
resource "google_secret_manager_secret_iam_member" "runtime_reads_config" {
  for_each = {
    for pair in setproduct(keys(local.runtime_config_secrets), keys(local.runtime_sas)) :
    "${pair[0]}-${pair[1]}" => { secret_id = pair[0], sa = local.runtime_sas[pair[1]] }
  }
  project   = var.project_id
  secret_id = google_secret_manager_secret.runtime_config[each.value.secret_id].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${each.value.sa}"
}

terraform {
  backend "gcs" {}
}
