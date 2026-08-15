# Local deploy kit

Runs the whole deploy from a workstation instead of the self-hosted GitHub
runner. Every script mirrors one workflow, with the workflow's implicit
assumptions made explicit.

| Script | Mirrors | Does |
|---|---|---|
| `00-preflight.sh <env>` | — | Read-only. Verifies tools, auth, ADC, arch, secrets. Changes nothing. |
| `05-create-app-secrets.sh <env>` | — | One-time. Creates `whatsapp-app-secret-{aa,pp}`. |
| `10-build-push.sh <env> [--latest]` | `build-and-push.yml` | Builds the `linux/amd64` webhook image, pushes to the NPE registry. |
| `20-infra.sh <env> plan\|apply` | `deploy.yaml` | `terragrunt run --all`. |
| `30-agents.sh <env>` | `deploy-agents.yml` | Deploys the two Agent Engines, seeds the engine-name secrets. |
| `40-redeploy-webhook.sh <env> [sha]` | — | Pins Cloud Run to an image tag; prints the rollback command. |

`<env>` is always the **stack** name — `dev` or `prd`.

## Order

```bash
./scripts/local-deploy/00-preflight.sh        dev   # fix everything it flags
./scripts/local-deploy/05-create-app-secrets.sh dev # once per project
./scripts/local-deploy/10-build-push.sh       dev
./scripts/local-deploy/20-infra.sh            dev plan    # READ THE PLAN
./scripts/local-deploy/20-infra.sh            dev apply
./scripts/local-deploy/30-agents.sh           dev   # MUST precede real traffic
./scripts/local-deploy/40-redeploy-webhook.sh dev
```

Steps 20 → 30 → 40 are order-critical. `20` creates
`engine-{aa,pp}-resource-name` as **empty** secrets; the webhook reads them on
every inbound message, so between `20` and `30` it returns 500 for everything.
Do not expose the endpoint until `30` reports both secrets seeded.

## Three names for one environment

The repo is inconsistent about this and it is the easiest way to deploy to the
wrong project. `lib.sh` resolves it centrally so no script takes a raw name:

| stack dir | `environment.name` | GCP project | `deploy.py --env` | Cloud Run service | image project |
|---|---|---|---|---|---|
| `dev` | `dev` | `agro-extension-digital-npe` | `npe` | `agent-webhook-dev` | npe |
| `prd` | `prd` | `agro-extension-digital-prd` | `prd` | `agent-webhook-prd` | **npe** |

Images live in **NPE for both environments** — prd Cloud Run pulls from the NPE
registry. Pushing to a prd registry produces an image nothing will ever pull.

## Gotchas these scripts already handle

- **`--platform linux/amd64`.** Cloud Run is amd64-only. A native build on Apple
  Silicon pushes fine and then fails to start with an exec-format error.
- **Terragrunt syntax drift.** `--terragrunt-non-interactive` was removed in
  0.78+; `run-all` is now the deprecated alias for `run --all`. The workflow's
  command line fails verbatim on a current install (locally: 0.99.4).
- **`run --all apply` is auto-approve by default.** `--no-auto-approve` is what
  restores the prompt. Running locally there is no GitHub Environment reviewer
  gate, so the plan review is the only gate.
- **ADC ≠ `gcloud auth login`.** `deploy.py` uses Application Default
  Credentials; without `gcloud auth application-default login` it dies with
  `DefaultCredentialsError` even though gcloud itself works.
- **`:latest` does not redeploy.** Cloud Run pins a digest at deploy time.
- **Plan-time secret reads.** The stacks call `run_cmd` on four secrets while
  *evaluating* config, so a missing one fails before any plan output, with an
  error that blames gcloud rather than the real cause.
- **No trailing newline in secrets.** `printf '%s'`, never `echo` — a trailing
  `\n` becomes part of the HMAC key and every signature check fails.

## Ambient state

Scripts set `CLOUDSDK_CORE_PROJECT` for their own shell rather than running
`gcloud config set project`, so your ambient gcloud config is never mutated.
They use your own credentials — no service-account key is needed or fetched.
