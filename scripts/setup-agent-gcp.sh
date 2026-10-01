#!/usr/bin/env bash
#
# setup-agent-gcp.sh  (Fase B del plan: B2 secretos + B3 IAM + B4 test de DSN)
#
# Deja listos en GCP los 3 secretos que consume el agente, con IAM, y VERIFICA
# el CATALOG_DSN antes de guardarlo (probando el user simple y el user con .ref
# que suele exigir el pooler de Supavisor). NO hace el deploy (B5): eso es
# terragrunt apply + deploy-agents.yml, al final se imprime cómo.
#
# El script NO ejecuta nada destructivo en prod salvo crear/versionar secretos y
# bindings de IAM (lo que pediste). No corre deploys.
#
# USO (en tu entorno con gcloud logueado y psql instalado):
#   export CATALOG_DSN='postgresql://agent_catalog_reader:<PW>@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require'
#   export AGENT_SERVICE_TOKEN='<el token que está en Vercel>'   # o usá ROTATE=1 (ver abajo)
#   ./scripts/setup-agent-gcp.sh
#
# Variables opcionales:
#   GCP_PROJECT   (default agro-extension-digital-prd)
#   REF           (default svznwftzdbfnxtjwgtfo)  -> para el fallback user.ref
#   DEPLOYER_SA   service account del deploy de agentes (la de secrets.GCP_SA_KEY);
#                 si la pasás, también recibe secretAccessor.
#   CIRUELA_API_BASE (default https://agro-extension-digital-app.vercel.app)
#   ROTATE=1      en vez de usar AGENT_SERVICE_TOKEN, corre rotate-agent-token.sh
#                 (genera uno nuevo en Vercel+GCP). OJO: si rotás, hay que
#                 re-deployar Vercel prod para que el build corriendo tome el
#                 token nuevo, o el agente da 401 por mismatch.

set -euo pipefail

GCP_PROJECT="${GCP_PROJECT:-agro-extension-digital-prd}"
REF="${REF:-svznwftzdbfnxtjwgtfo}"
CIRUELA_API_BASE="${CIRUELA_API_BASE:-https://agro-extension-digital-app.vercel.app}"
DEPLOYER_SA="${DEPLOYER_SA:-}"
REGION="${REGION:-us-central1}"

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
blue()  { printf '\033[34m%s\033[0m\n' "$*"; }

command -v gcloud >/dev/null 2>&1 || { red "Falta gcloud."; exit 1; }
command -v psql   >/dev/null 2>&1 || { red "Falta psql (para verificar el DSN)."; exit 1; }

# -------- token: usar el provisto, o rotar --------
if [ "${ROTATE:-0}" = "1" ]; then
  blue "ROTATE=1 -> corriendo rotate-agent-token.sh (genera token nuevo en Vercel+GCP)."
  GCP_PROJECTS="$GCP_PROJECT" "$(dirname "$0")/rotate-agent-token.sh"
  red "RECORDÁ: re-deployar Vercel prod para que tome el token nuevo (si no, 401)."
  TOKEN_DONE=1
else
  : "${AGENT_SERVICE_TOKEN:?Exportá AGENT_SERVICE_TOKEN (el valor que está en Vercel) o usá ROTATE=1}"
  TOKEN_DONE=0
fi

: "${CATALOG_DSN:?Exportá CATALOG_DSN (el de Task A3)}"

# -------- B4: verificar el DSN, con fallback a user.ref --------
test_dsn() { psql "$1" -tAc "SELECT count(*) FROM questions WHERE is_active;" 2>/dev/null; }

blue "B4: probando CATALOG_DSN tal cual..."
if n=$(test_dsn "$CATALOG_DSN"); then
  green "  conecta y lee ($n preguntas activas). DSN OK."
  FINAL_DSN="$CATALOG_DSN"
else
  blue "  falló. Probando con usuario .${REF} (formato pooler Supavisor)..."
  DSN_REF="${CATALOG_DSN/agent_catalog_reader:/agent_catalog_reader.${REF}:}"
  if [ "$DSN_REF" = "$CATALOG_DSN" ]; then
    red "  no pude derivar la variante .ref automáticamente. Revisá el DSN a mano."; exit 1
  fi
  if n=$(test_dsn "$DSN_REF"); then
    green "  conecta con .${REF} ($n preguntas). Uso esa variante como DSN final."
    FINAL_DSN="$DSN_REF"
  else
    red "  ninguna variante conecta. Revisá password/host/egress antes de seguir."; exit 1
  fi
fi

# -------- B2: crear/versionar los 3 secretos --------
put_secret() {
  local name="$1" val="$2"
  if gcloud secrets describe "$name" --project="$GCP_PROJECT" >/dev/null 2>&1; then
    printf '%s' "$val" | gcloud secrets versions add "$name" --project="$GCP_PROJECT" --data-file=- >/dev/null
    blue "  $name: versión nueva."
  else
    printf '%s' "$val" | gcloud secrets create "$name" --project="$GCP_PROJECT" --replication-policy=automatic --data-file=- >/dev/null
    blue "  $name: creado."
  fi
}
blue "B2: secretos en $GCP_PROJECT..."
put_secret ciruela-api-base "$CIRUELA_API_BASE"
put_secret catalog-dsn      "$FINAL_DSN"
if [ "$TOKEN_DONE" = "0" ]; then
  put_secret agent-service-token "$AGENT_SERVICE_TOKEN"
else
  blue "  agent-service-token: ya lo seteó rotate-agent-token.sh."
fi
green "✓ B2 ok."

# -------- B3: IAM secretAccessor --------
# El deploy-agents.yml lee los secretos como las SAs runtime (agent-aa-runtime /
# agent-pp-runtime): es a ellas a quien está concedido datastore-aa-id, así que
# espejamos ese patrón. Más la SA del webhook (identity.py). No hay un deployer SA
# aparte en el IAM de prd (verificado).
blue "B3: IAM secretAccessor..."
WEBHOOK_SA=$(gcloud run services describe "agent-webhook-${GCP_PROJECT##*-}" --project="$GCP_PROJECT" --region="$REGION" \
  --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null || true)
GRANTEES=(
  "agent-aa-runtime@${GCP_PROJECT}.iam.gserviceaccount.com"
  "agent-pp-runtime@${GCP_PROJECT}.iam.gserviceaccount.com"
)
[ -n "$WEBHOOK_SA" ] && GRANTEES+=("$WEBHOOK_SA") || red "  no pude leer la webhook SA (ajustá a mano)."
# Si tu deploy usa una SA distinta a las runtime, pasala en DEPLOYER_SA.
[ -n "$DEPLOYER_SA" ] && GRANTEES+=("$DEPLOYER_SA")
printf '  grantees: %s\n' "${GRANTEES[@]}"
for s in agent-service-token ciruela-api-base catalog-dsn; do
  for sa in "${GRANTEES[@]}"; do
    gcloud secrets add-iam-policy-binding "$s" --project="$GCP_PROJECT" \
      --member="serviceAccount:$sa" --role=roles/secretmanager.secretAccessor >/dev/null
  done
done
green "✓ B3 ok (agent-aa-runtime, agent-pp-runtime${WEBHOOK_SA:+, webhook}${DEPLOYER_SA:+, +DEPLOYER_SA})."

# -------- B5: next steps (no se ejecutan acá) --------
echo
green "Listo B2+B3+B4. Falta el deploy (B5), que NO corro acá:"
blue "  1) Webhook:      cd cicd/stacks/${GCP_PROJECT##*-}/backend && terragrunt apply"
blue "  2) Agent Engine: disparar .github/workflows/deploy-agents.yml para ${GCP_PROJECT##*-}"
blue "  3) e2e (C1):     mensaje real de WhatsApp -> ver logs sin 401/500 contra /api/agent/*"
