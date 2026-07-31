#!/usr/bin/env bash
# Verifies this machine can run a local deploy against <dev|prd>, WITHOUT
# changing anything. Run this first; fix everything it flags before proceeding.
#
#   ./scripts/local-deploy/00-preflight.sh dev

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
resolve_env "${1:-}"
use_project
print_target

fail=0
note() { c_grn "  ✅ $*"; }
warn() { c_ylw "  ⚠️  $*"; }
bad()  { c_red "  ❌ $*"; fail=1; }

# ── 1. Tooling ────────────────────────────────────────────────────────────────
c_blu "1. Tooling"
for t in gcloud terragrunt terraform uv docker; do
  command -v "$t" >/dev/null 2>&1 || { bad "$t not installed"; continue; }
  note "$t $("$t" --version 2>&1 | head -1)"
done

# The frontend module needs >= 1.5; nothing here needs more. (`terraform test`
# needs 1.6+, but that only runs in CI — it is not part of a deploy.)
if command -v terraform >/dev/null 2>&1; then
  tf_ver="$(terraform version -json 2>/dev/null | sed -n 's/.*"terraform_version": *"\([^"]*\)".*/\1/p')"
  tf_major="${tf_ver%%.*}"; tf_minor="$(echo "$tf_ver" | cut -d. -f2)"
  if (( tf_major > 1 )) || (( tf_major == 1 && tf_minor >= 5 )); then
    note "terraform ${tf_ver} satisfies required_version >= 1.5"
  else
    bad "terraform ${tf_ver} is below the modules' required_version >= 1.5"
  fi
fi

# ── 2. Docker can produce linux/amd64 ────────────────────────────────────────
c_blu "2. Docker / image architecture"
host_arch="$(uname -m)"
if ! docker info >/dev/null 2>&1; then
  bad "Docker daemon is not running (start Docker Desktop)"
elif [[ "$host_arch" == "arm64" || "$host_arch" == "aarch64" ]]; then
  # Cloud Run only runs linux/amd64. A plain `docker build` on Apple Silicon
  # produces an arm64 image that pushes fine and then fails to start with an
  # exec-format error — the single worst local-deploy trap. 10-build-push.sh
  # always passes --platform linux/amd64; this just confirms it can.
  if docker buildx inspect --bootstrap >/dev/null 2>&1; then
    note "host is ${host_arch}; buildx available for --platform linux/amd64"
  else
    bad "host is ${host_arch} but docker buildx is unavailable — images would be arm64 and Cloud Run would not start them"
  fi
else
  note "host is ${host_arch}"
fi

# ── 3. gcloud identity + project access ──────────────────────────────────────
c_blu "3. Authentication"
active="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null || true)"
[[ -n "$active" ]] && note "active account: ${active}" || bad "no active gcloud account (run: gcloud auth login)"

if gcloud projects describe "$PROJECT_ID" >/dev/null 2>&1; then
  note "can read project ${PROJECT_ID}"
else
  bad "cannot access project ${PROJECT_ID} as ${active}"
fi

# deploy.py (Vertex AI SDK) authenticates via Application Default Credentials,
# which are SEPARATE from `gcloud auth login`. Missing ADC is a common surprise:
# gcloud works, then deploy.py dies with DefaultCredentialsError.
adc="${HOME}/.config/gcloud/application_default_credentials.json"
if [[ -f "$adc" ]]; then
  note "ADC present (needed by agents/deploy.py)"
  # The database unit's firebaserules calls fail under user ADC unless a quota
  # project is set (20-infra.sh also forces it via GOOGLE_BILLING_PROJECT, but a
  # set quota project is the durable fix and avoids a confusing first run).
  qp="$(python3 -c "import json,sys;print(json.load(open('$adc')).get('quota_project_id',''))" 2>/dev/null || true)"
  if [[ "$qp" == "$PROJECT_ID" ]]; then
    note "ADC quota project = ${qp}"
  elif [[ -n "$qp" ]]; then
    warn "ADC quota project is ${qp}, not ${PROJECT_ID} — run: gcloud auth application-default set-quota-project ${PROJECT_ID}"
  else
    warn "ADC has no quota project — run: gcloud auth application-default set-quota-project ${PROJECT_ID}"
  fi
else
  bad "no ADC — run: gcloud auth application-default login"
fi

# ── 4. Secrets that must pre-exist ───────────────────────────────────────────
c_blu "4. Pre-existing secrets (read by terragrunt run_cmd at PLAN time)"
for s in "${PREEXISTING_SECRETS[@]}"; do
  if gcloud secrets versions access latest --secret="$s" --project="$PROJECT_ID" >/dev/null 2>&1; then
    note "${s}"
  else
    bad "${s} missing or unreadable — terragrunt plan will fail before it starts"
  fi
done

# ── 5. Terraform-managed secrets (informational) ─────────────────────────────
c_blu "5. Terraform-managed secrets (created by 20-infra.sh, not by you)"
for s in datastore-aa-id datastore-pp-id datastore-guides-id datastore-faq-id \
         datastore-chileprunes-cl-id bigquery-dataset; do
  if gcloud secrets describe "$s" --project="$PROJECT_ID" >/dev/null 2>&1; then
    note "${s} exists"
  else
    warn "${s} absent — expected before the first infra apply"
  fi
done
for s in engine-aa-resource-name engine-pp-resource-name; do
  if gcloud secrets versions access latest --secret="$s" --project="$PROJECT_ID" >/dev/null 2>&1; then
    note "${s} has a version (engines already deployed)"
  elif gcloud secrets describe "$s" --project="$PROJECT_ID" >/dev/null 2>&1; then
    warn "${s} exists but is EMPTY — the webhook 500s until 30-agents.sh seeds it"
  else
    warn "${s} absent — created by the infra apply"
  fi
done

echo
if (( fail )); then
  c_red "PREFLIGHT FAILED — fix the ❌ items above before deploying."
  exit 1
fi
c_grn "PREFLIGHT PASSED for ${STACK} (${PROJECT_ID})."
