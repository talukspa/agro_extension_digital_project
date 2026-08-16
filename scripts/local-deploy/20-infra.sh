#!/usr/bin/env bash
# Local equivalent of .github/workflows/deploy.yaml (terragrunt run-all).
#
#   ./scripts/local-deploy/20-infra.sh dev plan
#   ./scripts/local-deploy/20-infra.sh dev apply
#
# TWO DELIBERATE DIFFERENCES FROM THE WORKFLOW — do not "fix" them back:
#
# 1. Syntax. The workflow runs `terragrunt run-all <cmd> --terragrunt-non-interactive`.
#    That flag was REMOVED in Terragrunt 0.78+ (locally: 0.99.4 → "flag provided
#    but not defined"), and `run-all` is now the deprecated alias for `run --all`.
#    Copying the workflow line verbatim fails immediately on a current install.
#
# 2. Approval. `terragrunt run --all apply` appends `-auto-approve` to the
#    underlying terraform BY DEFAULT; `--no-auto-approve` is what restores the
#    per-unit prompt. So the "safe" reading of the workflow is backwards — it is
#    already unattended. The prd apply destroys the old Cloud Run agent service,
#    its SA and IAM bindings (the rollback target) and overwrites the live
#    Firestore ruleset. Run locally there is no GitHub Environment reviewer gate,
#    so the plan review IS the gate, and we force the prompt.

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
resolve_env "${1:-}"
action="${2:-plan}"
[[ "$action" == "plan" || "$action" == "apply" ]] || die "Second arg must be 'plan' or 'apply' (got '${action}')"

use_project
print_target

STACK_DIR="${REPO_ROOT}/cicd/stacks/${STACK}"
[[ -d "$STACK_DIR" ]] || die "No stack directory at ${STACK_DIR}"

# terragrunt reads these secrets with run_cmd while EVALUATING the config, so a
# missing one fails before any plan output appears — with an error that points
# at gcloud, not at the real cause. Check up front and say so plainly.
c_blu "Checking plan-time secret reads…"
missing=()
for s in "${PREEXISTING_SECRETS[@]}"; do
  gcloud secrets versions access latest --secret="$s" --project="$PROJECT_ID" >/dev/null 2>&1 \
    || missing+=("$s")
done
if (( ${#missing[@]} )); then
  c_red "Missing secrets in ${PROJECT_ID}: ${missing[*]}"
  die "terragrunt cannot evaluate the config. Run 05-create-app-secrets.sh ${STACK} first."
fi
c_grn "  ✅ all ${#PREEXISTING_SECRETS[@]} plan-time secrets readable"
echo

cd "$STACK_DIR"

c_blu "terragrunt run --all init…"
terragrunt run --all init --non-interactive

c_blu "terragrunt run --all plan…"
terragrunt run --all plan --non-interactive

if [[ "$action" == "plan" ]]; then
  echo
  c_grn "Plan complete. Read it, then re-run with 'apply'."
  echo
  c_ylw "Before applying, confirm in the plan above:"
  echo "  • Destroy count is exactly 5 on the first migration apply (old agent Cloud Run"
  echo "    service + its SA + 2 role bindings + webhook_invokes_agent_aa). Anything else → STOP."
  echo "  • The webhook Cloud Run service gains WHATSAPP_APP_SECRET_AA / _PP env entries."
  echo "  • cicd/modules/backend/main.tf documents a manual 'terraform state rm' of the"
  echo "    retired resources that must happen BEFORE this apply. Confirm it is done."
  exit 0
fi

echo
confirm_prd
c_ylw "Applying to ${PROJECT_ID}. --no-auto-approve keeps the per-unit prompt."
# NOTE: --non-interactive is deliberately absent here. It means "assume yes to
# all prompts", which would defeat --no-auto-approve.
terragrunt run --all apply --no-auto-approve

echo
c_grn "Infra applied."
echo
c_ylw "ORDERING (critical): engine-{aa,pp}-resource-name now exist but are EMPTY."
echo "The webhook resolves the engine handle from them on every inbound message,"
echo "so it 500s until they are seeded. Run this next, before any real traffic:"
echo "  ./scripts/local-deploy/30-agents.sh ${STACK}"
