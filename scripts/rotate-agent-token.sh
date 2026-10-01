#!/usr/bin/env bash
#
# rotate-agent-token.sh
#
# Crea UNA versión nueva del AGENT_SERVICE_TOKEN y la deja en los dos lados:
#   1. App Ciruela  -> Vercel Production, env var AGENT_SERVICE_TOKEN
#   2. Agente (GCP) -> Secret Manager, secret `agent-service-token`
#                      (crea el secret si no existe; si existe, agrega versión nueva)
#      + lo lee el Agent Engine (deploy-agents.yml) y el webhook (Cloud Run) en el deploy.
#
# El token es un string aleatorio: lo mismo en los dos lados. No se guarda en
# disco; se imprime UNA vez al final para tu gestor de contraseñas.
#
# Uso:
#   ./scripts/rotate-agent-token.sh                 # proyecto prd (default)
#   GCP_PROJECTS="agro-extension-digital-npe agro-extension-digital-prd" ./scripts/rotate-agent-token.sh
#   VERCEL_VAR=AGENT_SERVICE_TOKEN_NEXT ./scripts/rotate-agent-token.sh   # rotación sin caída
#
# Requisitos: openssl, vercel (logueado), gcloud (logueado, con permiso sobre el/los proyecto/s).
#
# Rotación sin caída (recomendado si el agente ya está en prod):
#   1) correr con VERCEL_VAR=AGENT_SERVICE_TOKEN_NEXT  -> deja el token nuevo como SECUNDARIO en Vercel
#      y como versión :latest del secret en GCP.
#   2) redeployar el Agent Engine + webhook (toman el nuevo secret).
#   3) correr normal (VERCEL_VAR=AGENT_SERVICE_TOKEN) para promover el nuevo a primario en Vercel.
#   Mientras tanto Vercel acepta AMBOS tokens, así que no hay ventana de 401.

set -euo pipefail

# --- Config -----------------------------------------------------------------
VERCEL_SCOPE="${VERCEL_SCOPE:-taluk-spa}"
VERCEL_ENV="${VERCEL_ENV:-production}"
VERCEL_VAR="${VERCEL_VAR:-AGENT_SERVICE_TOKEN}"        # o AGENT_SERVICE_TOKEN_NEXT para rotar
GCP_SECRET="${GCP_SECRET:-agent-service-token}"
GCP_PROJECTS="${GCP_PROJECTS:-agro-extension-digital-prd}"   # espacio-separado para varios
# ---------------------------------------------------------------------------

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
blue()  { printf '\033[34m%s\033[0m\n' "$*"; }

command -v openssl >/dev/null 2>&1 || { red "Falta openssl."; exit 1; }
command -v vercel  >/dev/null 2>&1 || { red "Falta la CLI de vercel (vercel login)."; exit 1; }
command -v gcloud  >/dev/null 2>&1 || { red "Falta gcloud (gcloud auth login)."; exit 1; }

blue "Voy a:"
blue "  - Vercel ${VERCEL_ENV} (scope ${VERCEL_SCOPE}): setear ${VERCEL_VAR}"
blue "  - GCP Secret Manager: nueva versión de '${GCP_SECRET}' en: ${GCP_PROJECTS}"
printf 'Continuar? [y/N] '
read -r ans
[ "${ans}" = "y" ] || [ "${ans}" = "Y" ] || { echo "Cancelado."; exit 0; }

# 1. Generar el token (256 bits)
TOKEN="$(openssl rand -hex 32)"

# 2. Vercel — idempotente (borra el existente si lo hay, luego agrega)
if vercel env ls --scope "${VERCEL_SCOPE}" 2>/dev/null \
     | grep -qE "^[[:space:]]*${VERCEL_VAR}[[:space:]].*${VERCEL_ENV}"; then
  blue "Vercel: ${VERCEL_VAR} ya existe en ${VERCEL_ENV}; lo reemplazo."
  vercel env rm "${VERCEL_VAR}" "${VERCEL_ENV}" --yes --scope "${VERCEL_SCOPE}" >/dev/null
fi
printf '%s' "${TOKEN}" | vercel env add "${VERCEL_VAR}" "${VERCEL_ENV}" --scope "${VERCEL_SCOPE}" >/dev/null
green "✓ Vercel ${VERCEL_ENV}: ${VERCEL_VAR} seteado."

# 3. GCP Secret Manager — por cada proyecto: crear el secret si falta, luego agregar versión
for proj in ${GCP_PROJECTS}; do
  if gcloud secrets describe "${GCP_SECRET}" --project="${proj}" >/dev/null 2>&1; then
    blue "GCP[${proj}]: '${GCP_SECRET}' existe; agrego versión nueva."
  else
    blue "GCP[${proj}]: '${GCP_SECRET}' no existe; lo creo."
    gcloud secrets create "${GCP_SECRET}" --project="${proj}" --replication-policy=automatic >/dev/null
  fi
  printf '%s' "${TOKEN}" | gcloud secrets versions add "${GCP_SECRET}" --project="${proj}" --data-file=- >/dev/null
  green "✓ GCP[${proj}]: '${GCP_SECRET}' -> versión :latest actualizada."
done

# 4. Mostrar el valor UNA vez
echo
green "TOKEN GENERADO (guardalo en tu gestor; no queda en disco):"
echo "    ${TOKEN}"
echo
blue "Pendiente para que surta efecto:"
blue "  - App Ciruela: redeploy de prod  ->  (repo app, desde raíz)  vercel --prod --yes"
blue "  - Agente/webhook: redeploy en GCP (Agent Engine via deploy-agents.yml + Cloud Run webhook)"
blue "    toman el secret '${GCP_SECRET}:latest' en el próximo apply/deploy."
