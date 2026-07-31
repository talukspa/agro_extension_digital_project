#!/usr/bin/env bash
# One-time (per environment): create the two Meta App Secrets the webhook uses
# to validate X-Hub-Signature-256 on inbound POSTs.
#
#   ./scripts/local-deploy/05-create-app-secrets.sh dev
#
# AA and PP are SEPARATE Meta apps with distinct App Secrets, so each webhook
# endpoint verifies against its own. Get each value from:
#   developers.facebook.com → the app → Settings → Basic → App Secret → Show
#     AA Meta App ID: 1328420471593056
#     PP Meta App ID: 1611224729556662
#
# These are the Meta *App* IDs — what you use to locate the App Secret in the
# console. They are NOT the numbers in cicd/stacks/*/env.yaml (those are
# WhatsApp phone-number IDs used to build the outbound graph.facebook.com URL).
#
# NOTE: this is the App Secret (HMAC key for inbound signature validation), NOT
# wsp-token (the Bearer access token used for outbound sends) and NOT
# webhook-verify-token (the string you invented for Meta's one-time GET
# subscription handshake). Three different values; they are not interchangeable.
#
# Values are read with `read -s` so they are never echoed and never land in
# shell history.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
resolve_env "${1:-}"
use_project
print_target
confirm_prd

put_secret() {
  local name="$1" label="$2" value

  read -r -s -p "  ${label} App Secret (input hidden, blank = skip): " value
  echo
  if [[ -z "$value" ]]; then c_ylw "  skipped ${name}"; return 0; fi

  # printf '%s' — NOT echo — so no trailing newline is stored. A trailing \n
  # becomes part of the HMAC key and every signature check would fail.
  if gcloud secrets describe "$name" --project="$PROJECT_ID" >/dev/null 2>&1; then
    printf '%s' "$value" | gcloud secrets versions add "$name" \
      --data-file=- --project="$PROJECT_ID" >/dev/null
    c_grn "  ✅ added new version to ${name}"
  else
    printf '%s' "$value" | gcloud secrets create "$name" \
      --data-file=- --replication-policy=automatic --project="$PROJECT_ID" >/dev/null
    c_grn "  ✅ created ${name}"
  fi
}

put_secret whatsapp-app-secret-aa "AA (Meta App 1328420471593056)"
put_secret whatsapp-app-secret-pp "PP (Meta App 1611224729556662)"

echo
c_blu "Verifying (length only — values are not printed):"
for s in whatsapp-app-secret-aa whatsapp-app-secret-pp; do
  if n=$(gcloud secrets versions access latest --secret="$s" --project="$PROJECT_ID" 2>/dev/null | wc -c | tr -d ' '); then
    c_grn "  ${s}: ${n} bytes"
  else
    c_red "  ${s}: unreadable"
  fi
done
