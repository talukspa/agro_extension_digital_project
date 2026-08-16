# Unit tests for the backend module (Agent Runtime + webhook).
# Runs `command = plan` only, fully offline. Init with:
#   terraform init -backend=false
# then:
#   terraform test
#
# Security-critical invariants asserted here (from the review):
#   - agent-engine staging bucket is hardened (UBLA, no force_destroy, lifecycle)
#   - both runtime service accounts exist
#   - NO IAM binding ever grants roles/owner or roles/editor
#   - deployer IAM bindings are INERT when deployer_sa_email = ""
#   - deployer IAM bindings are PRESENT when deployer_sa_email is set

# Minimal dummy values so `plan` succeeds offline (no real GCP calls at plan
# time: the module has no data sources).
# Mock the google provider so `terraform test` runs fully offline (no ADC /
# credentials needed). Assertions here check configured inputs, not
# provider-computed values, so mocked responses are sufficient.
mock_provider "google" {}

variables {
  project_id                               = "test-project"
  region                                   = "us-central1"
  cloud_run_name_webhook                   = "webhook-test"
  gar_image_location_webhook               = "us-docker.pkg.dev/test/repo/webhook:latest"
  estandar_aa_facebook_app                 = "aa-fb"
  estandar_pp_facebook_app                 = "pp-fb"
  verify_token                             = "dummy-verify-token"
  whatsapp_app_secret_aa                   = "dummy-app-secret-aa"
  whatsapp_app_secret_pp                   = "dummy-app-secret-pp"
  service_account_webhook_app              = "webhook-sa"
  service_account_display_name_webhook_app = "Webhook SA"
  estandar_aa_app_name                     = "aa-app"
  estandar_pp_app_name                     = "pp-app"
  wsp_token_aa                             = "dummy-wsp-token-aa"
  wsp_token_pp                             = "dummy-wsp-token-pp"
  bigquery_dataset                         = "agro_dataset"
  datastore_aa_id                          = "projects/test/locations/global/collections/default/dataStores/aa"
  datastore_pp_id                          = "projects/test/locations/global/collections/default/dataStores/pp"
  datastore_guides_id                      = "projects/test/locations/global/collections/default/dataStores/guides"
  datastore_faq_id                         = "projects/test/locations/global/collections/default/dataStores/faq"
  datastore_chileprunes_cl_id              = "projects/test/locations/global/collections/default/dataStores/cp"
}

# ------------------------------------------------------------------
# Default posture: deployer_sa_email left empty (inert deployer grants).
# ------------------------------------------------------------------
run "hardening_and_no_deployer_bindings" {
  command = plan

  # --- Agent-engine staging bucket hardening ---
  assert {
    condition     = google_storage_bucket.agent_engine_staging.uniform_bucket_level_access == true
    error_message = "Staging bucket must enforce uniform bucket-level access."
  }

  assert {
    condition     = google_storage_bucket.agent_engine_staging.force_destroy == false
    error_message = "Staging bucket must not allow force_destroy."
  }

  assert {
    condition     = google_storage_bucket.agent_engine_staging.public_access_prevention == "enforced"
    error_message = "Staging bucket must enforce public access prevention."
  }

  assert {
    condition     = length(google_storage_bucket.agent_engine_staging.lifecycle_rule) > 0
    error_message = "Staging bucket must define at least one lifecycle rule."
  }

  # --- Runtime service accounts exist ---
  assert {
    condition     = google_service_account.agent_aa_runtime.account_id == "agent-aa-runtime"
    error_message = "AA runtime service account must exist."
  }

  assert {
    condition     = google_service_account.agent_pp_runtime.account_id == "agent-pp-runtime"
    error_message = "PP runtime service account must exist."
  }

  # --- No runtime IAM binding grants owner/editor ---
  assert {
    condition = alltrue([
      for b in values(google_project_iam_member.runtime_bindings) :
      !contains(["roles/owner", "roles/editor"], b.role)
    ])
    error_message = "Runtime SA bindings must never grant roles/owner or roles/editor."
  }

  # --- The webhook's engine-invoke binding is scoped, not owner/editor ---
  assert {
    condition     = !contains(["roles/owner", "roles/editor"], google_project_iam_member.webhook_invokes_engines.role)
    error_message = "Webhook engine-invoke binding must not grant roles/owner or roles/editor."
  }

  # --- Deployer bindings are INERT when deployer_sa_email = "" ---
  assert {
    condition     = length(google_project_iam_member.deployer_aiplatform) == 0
    error_message = "Deployer aiplatform binding must be absent when deployer_sa_email is empty."
  }

  assert {
    condition     = length(google_storage_bucket_iam_member.deployer_staging) == 0
    error_message = "Deployer staging binding must be absent when deployer_sa_email is empty."
  }

  assert {
    condition     = length(google_service_account_iam_member.deployer_acts_as_runtime) == 0
    error_message = "Deployer actAs bindings must be absent when deployer_sa_email is empty."
  }

  assert {
    condition     = length(google_secret_manager_secret_iam_member.deployer_writes_engine_names) == 0
    error_message = "Deployer secret-version-adder bindings must be absent when deployer_sa_email is empty."
  }
}

# ------------------------------------------------------------------
# When deployer_sa_email is set, the deployer bindings materialize.
# ------------------------------------------------------------------
run "deployer_bindings_present_when_set" {
  command = plan

  variables {
    deployer_sa_email = "ci-deployer@test-project.iam.gserviceaccount.com"
  }

  assert {
    condition     = length(google_project_iam_member.deployer_aiplatform) == 1
    error_message = "Deployer aiplatform binding must be present when deployer_sa_email is set."
  }

  assert {
    condition     = google_project_iam_member.deployer_aiplatform[0].member == "serviceAccount:ci-deployer@test-project.iam.gserviceaccount.com"
    error_message = "Deployer aiplatform binding must target the configured deployer SA."
  }

  assert {
    condition     = length(google_storage_bucket_iam_member.deployer_staging) == 1
    error_message = "Deployer staging binding must be present when deployer_sa_email is set."
  }

  assert {
    condition     = length(google_service_account_iam_member.deployer_acts_as_runtime) == 2
    error_message = "Deployer must be able to actAs both runtime SAs when set."
  }

  # Deployer must never receive owner/editor even when enabled.
  assert {
    condition     = !contains(["roles/owner", "roles/editor"], google_project_iam_member.deployer_aiplatform[0].role)
    error_message = "Deployer aiplatform binding must not grant roles/owner or roles/editor."
  }
}
