# Unit tests for the database (Firestore) module.
# Runs `command = plan` only, fully offline. Init with:
#   terraform init -backend=false
# then:
#   terraform test
#
# AUTHZ-CRITICAL invariant (guards the prod-authz bug that was fixed):
#   When var.firestore_security_rules is set, the DEPLOYED ruleset content must
#   equal that variable — NOT the wide-open "any authenticated user" minimal
#   fallback. A regression here means prod runs effectively wide-open.
#
# Also asserts the daily backup schedule is gated by enable_daily_backup.

# Mock the google provider so `terraform test` runs fully offline (no ADC /
# credentials needed). Assertions here check configured inputs, not
# provider-computed values, so mocked responses are sufficient.
mock_provider "google" {}

variables {
  project_id  = "test-project"
  environment = "prd"
}

# ------------------------------------------------------------------
# When per-env rules are provided, they are exactly what gets deployed,
# and the wide-open fallback is NOT used. Backup disabled -> no schedule.
# ------------------------------------------------------------------
run "deploys_provided_rules_not_fallback" {
  command = plan

  variables {
    firestore_security_rules = <<-EOT
      rules_version = '2';
      service cloud.firestore {
        match /databases/{database}/documents {
          match /business_profiles/{doc} {
            allow read, write: if request.auth != null && request.auth.token.role == 'auditor';
          }
        }
      }
    EOT
    enable_daily_backup      = false
  }

  # Deployed ruleset content == the provided per-env rules (source of truth).
  assert {
    condition = (
      google_firebaserules_ruleset.agro_extension_ruleset.source[0].files[0].content
      == var.firestore_security_rules
    )
    error_message = "Deployed Firestore ruleset must equal the provided firestore_security_rules."
  }

  # ...and it must NOT be the wide-open minimal fallback.
  assert {
    condition = (
      google_firebaserules_ruleset.agro_extension_ruleset.source[0].files[0].content
      != file("${path.module}/firestore-security-rules-minimal.rules")
    )
    error_message = "Deployed Firestore ruleset must not be the wide-open minimal fallback in prd."
  }

  # Sanity: the provided rules are gated by an auditor role, not open to any
  # authenticated user.
  assert {
    condition     = strcontains(google_firebaserules_ruleset.agro_extension_ruleset.source[0].files[0].content, "auditor")
    error_message = "Provided ruleset should carry role-based (auditor) authorization."
  }

  # Backup schedule absent when disabled.
  assert {
    condition     = length(google_firestore_backup_schedule.agro_extension_backup) == 0
    error_message = "Backup schedule must be absent when enable_daily_backup = false."
  }
}

# ------------------------------------------------------------------
# When firestore_security_rules is left empty, the module falls back to the
# minimal ruleset (fallback path still works). Backup enabled -> schedule present.
# ------------------------------------------------------------------
run "fallback_used_only_when_rules_empty" {
  command = plan

  variables {
    firestore_security_rules = ""
    enable_daily_backup      = true
  }

  assert {
    condition = (
      google_firebaserules_ruleset.agro_extension_ruleset.source[0].files[0].content
      == file("${path.module}/firestore-security-rules-minimal.rules")
    )
    error_message = "Empty firestore_security_rules must fall back to the minimal ruleset file."
  }

  assert {
    condition     = length(google_firestore_backup_schedule.agro_extension_backup) == 1
    error_message = "Backup schedule must be present when enable_daily_backup = true."
  }
}
