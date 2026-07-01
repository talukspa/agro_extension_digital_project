# Unit tests for the frontend module (Next.js on Cloud Run).
# Runs `command = plan` only, fully offline. Init with:
#   terraform init -backend=false
# then:
#   terraform test
#
# Invariants (from the review):
#   - The frontend SA must NOT hold project-wide roles/secretmanager.secretAccessor
#     (it reads no secrets; config arrives as plain env vars).
#   - No reference to the removed agent_aa_service_url / NEXT_PUBLIC_AGENT_AA_URL
#     (the AA agent is now a Vertex AI Agent Engine, not a Cloud Run URL).

variables {
  project_id                            = "test-project"
  environment                           = "prd"
  location                              = "us-central1"
  cloud_run_name_frontend               = "frontend-test"
  gar_image_location_frontend           = "us-docker.pkg.dev/test/repo/frontend:latest"
  service_account_id_frontend           = "frontend-sa"
  service_account_display_name_frontend = "Frontend SA"
  firebase_api_key                      = "dummy-api-key"
  firebase_auth_domain                  = "test-project.firebaseapp.com"
  firebase_storage_bucket               = "test-project.appspot.com"
  firebase_messaging_sender_id          = "1234567890"
  firebase_app_id                       = "1:1234567890:web:abc"
  webhook_service_url                   = "https://webhook-test.run.app"
}

run "frontend_iam_and_no_removed_agent_url" {
  command = plan

  # --- SA must NOT get project-wide secretmanager.secretAccessor ---
  assert {
    condition     = !contains(keys(google_project_iam_member.frontend_sa_roles), "roles/secretmanager.secretAccessor")
    error_message = "Frontend SA must not hold project-wide roles/secretmanager.secretAccessor."
  }

  # And it must not hold owner/editor either.
  assert {
    condition = alltrue([
      for r in keys(google_project_iam_member.frontend_sa_roles) :
      !contains(["roles/owner", "roles/editor"], r)
    ])
    error_message = "Frontend SA must never hold roles/owner or roles/editor."
  }

  # --- No reference to the removed AA agent Cloud Run URL ---
  assert {
    condition = !contains(
      [for e in google_cloud_run_v2_service.frontend_service.template[0].containers[0].env : e.name],
      "NEXT_PUBLIC_AGENT_AA_URL"
    )
    error_message = "Removed env var NEXT_PUBLIC_AGENT_AA_URL must not be present."
  }

  # None of the injected env var values should carry an agent_aa_service_url.
  assert {
    condition = alltrue([
      for e in google_cloud_run_v2_service.frontend_service.template[0].containers[0].env :
      !strcontains(lower(e.name), "agent_aa_service_url")
    ])
    error_message = "No reference to the removed agent_aa_service_url is allowed."
  }
}
