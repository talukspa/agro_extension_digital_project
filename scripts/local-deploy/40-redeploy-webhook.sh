#!/usr/bin/env bash
# Point the webhook Cloud Run service at a specific image tag.
#
#   ./scripts/local-deploy/40-redeploy-webhook.sh dev 1a2b3c4
#   ./scripts/local-deploy/40-redeploy-webhook.sh dev            # defaults to HEAD sha
#
# Needed because Cloud Run resolves :latest to a DIGEST at deploy time. Pushing
# a new :latest does not restart anything — the service keeps serving the digest
# it pinned. This forces a new revision on the tag you name.
#
# Deploy this only AFTER 30-agents.sh has seeded engine-{aa,pp}-resource-name.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
resolve_env "${1:-}"
TAG="${2:-$(git -C "$REPO_ROOT" rev-parse --short HEAD)}"
use_project
print_target
echo "  image tag      : ${TAG}"
echo

# Refuse to expose the webhook before the engine handles exist — this is the
# documented cutover failure mode (access latest → NOT_FOUND → 500 per message).
for s in engine-aa-resource-name engine-pp-resource-name; do
  gcloud secrets versions access latest --secret="$s" --project="$PROJECT_ID" >/dev/null 2>&1 \
    || die "${s} has no version. Run 30-agents.sh ${STACK} first, or the webhook 500s on every message."
done
c_grn "  ✅ engine-name secrets are seeded"

gcloud artifacts docker images describe "${WEBHOOK_IMAGE}:${TAG}" --project="$IMAGE_PROJECT" >/dev/null 2>&1 \
  || die "Image ${WEBHOOK_IMAGE}:${TAG} not found. Run 10-build-push.sh ${STACK} first."
c_grn "  ✅ image exists"

# Capture the currently-serving revision so a rollback is one command away.
prev="$(gcloud run services describe "$CLOUD_RUN_WEBHOOK" --region="$REGION" \
        --project="$PROJECT_ID" --format='value(status.traffic[0].revisionName)' 2>/dev/null || true)"
[[ -n "$prev" ]] && c_blu "  current revision: ${prev}"

echo
confirm_prd
gcloud run services update "$CLOUD_RUN_WEBHOOK" \
  --image="${WEBHOOK_IMAGE}:${TAG}" \
  --region="$REGION" \
  --project="$PROJECT_ID"

echo
c_grn "Deployed ${WEBHOOK_IMAGE}:${TAG} to ${CLOUD_RUN_WEBHOOK}."
if [[ -n "$prev" ]]; then
  echo
  c_ylw "Rollback (instant, no rebuild):"
  echo "  gcloud run services update-traffic ${CLOUD_RUN_WEBHOOK} \\"
  echo "    --to-revisions=${prev}=100 --region=${REGION} --project=${PROJECT_ID}"
fi
