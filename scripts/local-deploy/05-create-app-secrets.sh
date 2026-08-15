#!/usr/bin/env bash
# One-time (per environment): create the FOUR per-app WhatsApp secrets the
# webhook needs. AA and PP are SEPARATE Meta apps (separate WABAs), so each
# value is per-app.
#
#   ./scripts/local-deploy/05-create-app-secrets.sh dev
#
#   whatsapp-app-secret-aa / -pp : Meta App Secret. HMAC key that validates the
#     X-Hub-Signature-256 header on INBOUND POSTs (fail-closed). From:
#       developers.facebook.com → the app → Settings → Basic → App Secret → Show
#         AA Meta App ID: 1328420471593056
#         PP Meta App ID: 1611224729556662
#
#   wsp-token-aa / -pp : WhatsApp Cloud API access token. Bearer token for
#     OUTBOUND sends. The token of one app returns 401 against the other app's
#     number, so it is per-app. Use a permanent System User token (Meta Business
#     Suite → System users → generate token, scope whatsapp_business_messaging);
#     plain user tokens expire.
#
# Three different kinds of value — App Secret (inbound HMAC) ≠ access token
# (outbound Bearer) ≠ webhook-verify-token (the GET handshake string). Not
# interchangeable. The Meta App ID above is NOT the phone-number ID in env.yaml.
#
# Values are read with `read -s` so they are never echoed and never land in
# shell history.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
resolve_env "${1:-}"
use_project
print_target
confirm_prd

# put_secret <secret-name> <prompt-label>
put_secret() {
  local name="$1" label="$2" value

  read -r -s -p "  ${label} (input hidden, blank = skip): " value
  echo
  if [[ -z "$value" ]]; then c_ylw "  skipped ${name}"; return 0; fi

  # printf '%s' — NOT echo — so no trailing newline is stored. A trailing \n
  # becomes part of the HMAC key / Bearer token and every check would fail.
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

c_blu "Meta App Secrets (inbound signature validation):"
put_secret whatsapp-app-secret-aa "AA App Secret (Meta App 1328420471593056)"
put_secret whatsapp-app-secret-pp "PP App Secret (Meta App 1611224729556662)"

echo
c_blu "Access tokens (outbound sends — use permanent System User tokens):"
put_secret wsp-token-aa "AA access token"
put_secret wsp-token-pp "PP access token"

echo
c_blu "Verifying (length only — values are not printed):"
for s in whatsapp-app-secret-aa whatsapp-app-secret-pp wsp-token-aa wsp-token-pp; do
  if n=$(gcloud secrets versions access latest --secret="$s" --project="$PROJECT_ID" 2>/dev/null | wc -c | tr -d ' '); then
    c_grn "  ${s}: ${n} bytes"
  else
    c_red "  ${s}: unreadable"
  fi
done
