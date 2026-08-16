#!/usr/bin/env bash
# Shared environment resolution for the local deploy scripts.
#
# WHY THIS FILE EXISTS: this repo uses three different names for the same
# environment, and mixing them up is the easiest way to deploy prod code to the
# wrong project (or push a prd image into a registry nothing pulls from):
#
#   stack dir │ environment.name │ GCP project                  │ deploy.py --env
#   ──────────┼──────────────────┼──────────────────────────────┼────────────────
#   dev       │ dev              │ agro-extension-digital-npe   │ npe
#   prd       │ prd              │ agro-extension-digital-prd   │ prd
#
# Container images live in the NPE project for BOTH environments
# (cicd/stacks/common.yaml → containers.project), because that is the path the
# backend Terraform points Cloud Run at in dev *and* prd. Never push to the prd
# registry — nothing pulls from there.
#
# Source this, don't run it:  source "$(dirname "$0")/lib.sh"; resolve_env "$1"

set -euo pipefail

REGION="us-central1"
IMAGE_PROJECT="agro-extension-digital-npe"
WEBHOOK_IMAGE="${REGION}-docker.pkg.dev/${IMAGE_PROJECT}/agro-extension-digital/webhook"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Secrets that must ALREADY exist before `terragrunt plan` runs. The stack reads
# them with run_cmd at plan time, so a missing one is a hard plan failure, not a
# runtime problem. Terraform creates the other secrets (datastore-*, engine-*).
PREEXISTING_SECRETS=(
  webhook-verify-token
  whatsapp-app-secret
  wsp-token-aa
  wsp-token-pp
)

c_red()  { printf '\033[0;31m%s\033[0m\n' "$*"; }
c_grn()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
c_ylw()  { printf '\033[1;33m%s\033[0m\n' "$*"; }
c_blu()  { printf '\033[0;34m%s\033[0m\n' "$*"; }
die()    { c_red "❌ $*"; exit 1; }

# resolve_env <dev|prd> — exports STACK, ENV_NAME, PROJECT_ID, AGENT_ENV,
# CLOUD_RUN_WEBHOOK.
resolve_env() {
  local stack="${1:-}"
  case "$stack" in
    dev)
      STACK="dev"; ENV_NAME="dev"
      PROJECT_ID="agro-extension-digital-npe"
      AGENT_ENV="npe"
      ;;
    prd)
      STACK="prd"; ENV_NAME="prd"
      PROJECT_ID="agro-extension-digital-prd"
      AGENT_ENV="prd"
      ;;
    *)
      die "Usage: $(basename "${0}") <dev|prd>   (got: '${stack}')"
      ;;
  esac
  CLOUD_RUN_WEBHOOK="agent-webhook-${ENV_NAME}"
  export STACK ENV_NAME PROJECT_ID AGENT_ENV CLOUD_RUN_WEBHOOK
}

# Print the resolved target so every script states plainly what it will touch.
print_target() {
  c_blu "──────────────────────────────────────────────"
  echo  "  stack dir      : cicd/stacks/${STACK}"
  echo  "  GCP project    : ${PROJECT_ID}"
  echo  "  deploy.py --env: ${AGENT_ENV}"
  echo  "  Cloud Run      : ${CLOUD_RUN_WEBHOOK} (${REGION})"
  echo  "  image registry : ${IMAGE_PROJECT}"
  c_blu "──────────────────────────────────────────────"
}

# Refuse to touch prd without an explicit typed confirmation.
confirm_prd() {
  [[ "$STACK" == "prd" ]] || return 0
  c_ylw "⚠️  TARGET IS PRODUCTION (${PROJECT_ID})."
  read -r -p "Type 'deploy prd' to continue: " reply
  [[ "$reply" == "deploy prd" ]] || die "Aborted."
}

# Make sure gcloud is pointed at the project we think it is, for this shell only.
# Uses CLOUDSDK_CORE_PROJECT rather than `gcloud config set project` so we never
# mutate the user's ambient gcloud state.
#
# USER_PROJECT_OVERRIDE + GOOGLE_BILLING_PROJECT: the CI workflows authenticate
# with a service-account key, whose credential carries its own project. Locally
# we use USER Application Default Credentials, and some APIs the stack touches —
# firebaserules.googleapis.com in the database unit above all — reject a user
# credential that carries no quota/billing project, attributing the call to
# Google's shared default project (32555940559) where the API is disabled:
#   Error 403 ... requires a quota project, which is not set by default
# The hashicorp/google provider only sends the X-Goog-User-Project header (which
# carries the billing project) when user_project_override is true. The provider
# blocks here don't set it, but the provider also reads these two env vars, so
# we set them centrally rather than editing every module. Harmless with SA creds.
use_project() {
  export CLOUDSDK_CORE_PROJECT="$PROJECT_ID"
  export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
  export USER_PROJECT_OVERRIDE="true"
  export GOOGLE_BILLING_PROJECT="$PROJECT_ID"
}
