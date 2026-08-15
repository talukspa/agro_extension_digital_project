#!/usr/bin/env bash
# Local equivalent of .github/workflows/build-and-push.yml.
#
#   ./scripts/local-deploy/10-build-push.sh dev [--latest]
#
# Builds and pushes the webhook image tagged with the current short SHA. Pass
# --latest to ALSO move the :latest tag, which is what Cloud Run pulls — mirrors
# the workflow's PUSH_LATEST gate, which only fires on main and version tags.
# Omit it when you just want an immutable :<sha> to test.
#
# Images always go to the NPE registry for BOTH environments — see lib.sh.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
resolve_env "${1:-}"; shift || true

push_latest=0
for arg in "$@"; do
  case "$arg" in
    --latest)   push_latest=1 ;;
    *) die "Unknown flag: $arg" ;;
  esac
done

use_project
print_target

GIT_SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
if [[ -n "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)" ]]; then
  c_ylw "⚠️  Working tree has uncommitted tracked changes; :${GIT_SHA} will NOT match this build."
fi
echo "  building from ${GIT_SHA} on $(git -C "$REPO_ROOT" branch --show-current)"
(( push_latest )) && c_ylw "  --latest: this WILL move the tag Cloud Run pulls."
echo

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

build_push() {
  local ctx="$1" image="$2" name="$3"
  c_blu "Building ${name}…"
  local tags=(-t "${image}:${GIT_SHA}")
  (( push_latest )) && tags+=(-t "${image}:latest")

  # --platform linux/amd64 is MANDATORY. Cloud Run runs amd64 only; a native
  # build on Apple Silicon yields an arm64 image that pushes successfully and
  # then fails at startup with an exec-format error.
  docker buildx build --platform linux/amd64 --push "${tags[@]}" "$ctx"

  c_grn "  ✅ pushed ${image}:${GIT_SHA}"
  (( push_latest )) && c_grn "  ✅ pushed ${image}:latest"
}

build_push "${REPO_ROOT}/webhook-application" "$WEBHOOK_IMAGE" "whatsapp webhook"

echo
c_grn "Done. Image digest actually served:"
docker buildx imagetools inspect "${WEBHOOK_IMAGE}:${GIT_SHA}" --format '{{.Manifest.Digest}}' 2>/dev/null || true
echo
echo "Next: ./scripts/local-deploy/20-infra.sh ${STACK} plan"
echo "Or redeploy just the webhook: ./scripts/local-deploy/40-redeploy-webhook.sh ${STACK} ${GIT_SHA}"
