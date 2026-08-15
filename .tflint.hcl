# tflint configuration for the cicd/ Terraform.
#
# CI usage (from repo root):
#   tflint --init                       # download plugins (needs network)
#   tflint --chdir=cicd --recursive     # lint all modules/stacks under cicd/
#
# The google plugin adds GCP-specific rules (invalid machine types, deprecated
# arguments, etc.) on top of the terraform recommended ruleset.

config {
  # Lint child modules too.
  call_module_type = "all"
  force            = false
}

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "google" {
  enabled = true
  version = "0.31.0"
  source  = "github.com/terraform-linters/tflint-ruleset-google"
}

# Enforce a canonical module structure / naming hygiene.
rule "terraform_naming_convention" {
  enabled = true
}

rule "terraform_typed_variables" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}

# Deprecated interpolation syntax etc.
rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}
