#!/usr/bin/env bash
# Local equivalent of .github/workflows/deploy-agents.yml.
#
#   ./scripts/local-deploy/30-agents.sh dev
#
# Creates or updates the two Vertex AI Agent Engines and writes their resource
# names back into engine-{aa,pp}-resource-name. deploy.py is idempotent: it
# resolves an existing engine from the secret and updates in place, so re-running
# is safe.
#
# Run this AFTER 20-infra.sh (which creates the runtime-config secrets this
# reads) and BEFORE pointing any real WhatsApp traffic at the webhook (which
# 500s while the engine-name secrets are empty).

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
resolve_env "${1:-}"
use_project
print_target
confirm_prd

# deploy.py refuses to run when GOOGLE_CLOUD_PROJECT disagrees with --env, so
# that a stale exported project can't send one env's datastore/RAG paths at
# another env's engine. use_project already set it to match; this is the value
# that guard will check.
export GOOGLE_CLOUD_LOCATION="$REGION"
export GOOGLE_GENAI_USE_VERTEXAI=TRUE

c_blu "Loading runtime config from Secret Manager (${PROJECT_ID})…"
for k in DATASTORE_AA_ID DATASTORE_PP_ID DATASTORE_GUIDES_ID \
         DATASTORE_FAQ_ID DATASTORE_CHILEPRUNES_CL_ID BIGQUERY_DATASET; do
  secret_id="$(echo "$k" | tr 'A-Z_' 'a-z-')"
  if ! v="$(gcloud secrets versions access latest --secret="$secret_id" --project="$PROJECT_ID" 2>/dev/null)"; then
    die "Secret '${secret_id}' not found in ${PROJECT_ID}. Run 20-infra.sh ${STACK} apply first — Terraform creates these."
  fi
  export "$k=$v"
  c_grn "  ✅ ${k}"
done
echo

cd "${REPO_ROOT}/agents"
c_blu "uv sync…"
uv sync --quiet

c_blu "Deploying engines (this takes several minutes per engine)…"
uv run python deploy.py --env "$AGENT_ENV"

echo
c_blu "Verifying the engine-name secrets were seeded:"
for s in engine-aa-resource-name engine-pp-resource-name; do
  if v="$(gcloud secrets versions access latest --secret="$s" --project="$PROJECT_ID" 2>/dev/null)"; then
    c_grn "  ✅ ${s} → ${v}"
  else
    c_red "  ❌ ${s} still EMPTY — the webhook will 500 on every message."
    exit 1
  fi
done

echo
c_grn "Engines deployed."
echo "Next: ./scripts/local-deploy/40-redeploy-webhook.sh ${STACK} <sha>"
