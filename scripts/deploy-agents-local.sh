#!/usr/bin/env bash
#
# deploy-agents-local.sh  (B5 — Agent Engine, SIN el runner self-hosted)
#
# El workflow deploy-agents.yml corre en un runner self-hosted. Si no está
# online, los runs quedan en cola para siempre. Este script hace EXACTAMENTE lo
# mismo desde tu máquina (owner con gcloud): carga las env vars requeridas desde
# Secret Manager y corre agents/deploy.py.
#
# USO:
#   gcloud auth login            # si no estás logueado
#   ./scripts/deploy-agents-local.sh            # default prd
#   ENVIRONMENT=npe ./scripts/deploy-agents-local.sh
#
# Requisitos: gcloud (con acceso de lectura a los secretos del proyecto) y uv.

set -euo pipefail

ENVIRONMENT="${ENVIRONMENT:-prd}"
PROJECT="agro-extension-digital-${ENVIRONMENT}"

blue() { printf '\033[34m%s\033[0m\n' "$*"; }
green(){ printf '\033[32m%s\033[0m\n' "$*"; }
red()  { printf '\033[31m%s\033[0m\n' "$*"; }

command -v gcloud >/dev/null 2>&1 || { red "Falta gcloud."; exit 1; }
command -v uv     >/dev/null 2>&1 || { red "Falta uv (astral)."; exit 1; }

cd "$(dirname "$0")/.."
export GOOGLE_CLOUD_PROJECT="$PROJECT"
gcloud config set project "$PROJECT" >/dev/null 2>&1

# Las 8 REQUERIDAS (RUNTIME_ENV_KEYS en agents/deploy.py). Mismo mapeo kebab-case
# que el workflow: FOO_BAR -> foo-bar.
REQUIRED=(DATASTORE_AA_ID DATASTORE_PP_ID DATASTORE_GUIDES_ID DATASTORE_FAQ_ID
          DATASTORE_CHILEPRUNES_CL_ID CIRUELA_API_BASE AGENT_SERVICE_TOKEN CATALOG_DSN)
# Opcionales: se cargan si el secreto existe; si no, se omiten.
OPTIONAL=(GEMINI_LOCATION CATALOG_MAX_ROWS TOOL_MAX_RETRIES AGENT_PLANNER AGENT_THINK_BUDGET)

blue "Cargando env vars desde Secret Manager ($PROJECT)..."
for k in "${REQUIRED[@]}"; do
  sid="$(echo "$k" | tr 'A-Z_' 'a-z-')"
  v="$(gcloud secrets versions access latest --secret="$sid" --project="$PROJECT" 2>/dev/null)" \
    || { red "  FALTA el secreto requerido: $sid"; exit 1; }
  export "$k=$v"
  blue "  ✓ $k"
done
for k in "${OPTIONAL[@]}"; do
  sid="$(echo "$k" | tr 'A-Z_' 'a-z-')"
  if v="$(gcloud secrets versions access latest --secret="$sid" --project="$PROJECT" 2>/dev/null)"; then
    export "$k=$v"; blue "  ✓ $k (opcional)"
  fi
done

blue "uv sync..."
( cd agents && uv sync )
green "Deploy del Agent Engine a $ENVIRONMENT..."
( cd agents && uv run python deploy.py --env "$ENVIRONMENT" )
green "✓ deploy.py terminó. Revisá arriba el resource name de cada engine."
