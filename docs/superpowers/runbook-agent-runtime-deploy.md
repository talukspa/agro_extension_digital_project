# Agent Runtime Deploy Runbook

What to do per env to deploy or redeploy the Vertex AI Agent Runtime engines and the rewritten webhook.

> **Deploys now run locally, not on the runner.** The self-hosted runner is not
> picking up jobs, so every workflow below (`deploy.yaml`, `deploy-agents.yml`,
> `build-and-push.yml`) queues indefinitely. Use `scripts/local-deploy/`, which
> mirrors each workflow and encodes the ordering and naming rules this document
> describes prose-only. See `scripts/local-deploy/README.md`.
>
> The GitHub-dispatch instructions below are kept for when the runner returns.

## Naming (three names for one environment)

Getting this wrong deploys to the wrong project. `scripts/local-deploy/lib.sh`
resolves it centrally; anything run by hand must apply it manually.

| stack dir | `environment.name` | GCP project | `deploy.py --env` | Cloud Run service | image project |
|---|---|---|---|---|---|
| `dev` | `dev` | `agro-extension-digital-npe` | `npe` | `agent-webhook-dev` | npe |
| `prd` | `prd` | `agro-extension-digital-prd` | `prd` | `agent-webhook-prd` | **npe** |

Container images live in the **NPE** project for *both* environments
(`cicd/stacks/common.yaml` → `containers.project`) — that is the path the backend
Terraform points Cloud Run at in prd too.

## Prerequisites (once per environment)

- `gcloud` authenticated with an account that has Owner or equivalent IAM in the target project — plus `gcloud auth application-default login`, which is separate and is what `deploy.py` actually uses.
- `terraform` 1.5+ (that is all `required_version` asks for; 1.6+ only matters for `terraform test`, which is CI-only), `terragrunt` 0.78+, `uv` 0.9+, `docker` with `linux/amd64` buildx support.
- **Five secrets must already exist in the project before the first `terragrunt plan`**, because the stack reads them with `run_cmd` while *evaluating* config: `webhook-verify-token`, `whatsapp-app-secret-aa`, `whatsapp-app-secret-pp`, `wsp-token-aa`, `wsp-token-pp`. Create the four per-app ones with `scripts/local-deploy/05-create-app-secrets.sh <env>`. AA and PP are separate Meta apps / WABAs, each with its own App Secret (inbound signature) **and** its own access token (outbound sends) — a token for one app returns 401 against the other's number.
- Run `scripts/local-deploy/00-preflight.sh <env>` — it checks all of the above and changes nothing.

For GitHub-dispatched runs (when the runner is back), the repo secret `GCP_SA_KEY` must additionally hold a service-account key with `roles/aiplatform.admin`, `roles/secretmanager.secretAccessor` on the six runtime-config secrets, `roles/storage.admin` on the staging bucket, and `roles/iam.serviceAccountUser` on `agent-aa-runtime@…` / `agent-pp-runtime@…`. Note `cicd.deployer_sa_email` is commented out in both `env.yaml` files, so Terraform currently grants that SA nothing — the bindings are inert and the IAM must be granted out-of-band.

## Phase 1 — Infra

Local: `scripts/local-deploy/20-infra.sh <env> plan`, then `… apply`. By hand:

```bash
cd cicd/stacks/<env>/backend     # <env> = dev or prd (stack dir, not project)
terragrunt plan -out=phase1.tfplan
# Review the plan. Expected for a fresh prd: ~25 adds (runtime SAs, GCS staging
# bucket, 6 runtime-config secrets + versions, engine resource-name secret
# containers, IAM bindings), update on the webhook Cloud Run service to gain
# the GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION env entries, and the Phase 5
# destroys (5 resources: old Cloud Run agent service + SA + IAM bindings).
# If the destroy count is anything other than 5, STOP and investigate.
terragrunt apply phase1.tfplan
```

What just got created in the target project:

- `gs://<project>-agent-engine-staging` bucket
- `agent-aa-runtime@<project>.iam.gserviceaccount.com`
- `agent-pp-runtime@<project>.iam.gserviceaccount.com`
- Project IAM bindings for 7 roles × 2 SAs
- 8 Secret Manager secrets:
  - `engine-aa-resource-name`, `engine-pp-resource-name` — empty containers, written by deploy.py
  - `datastore-{aa,pp,guides,faq,chileprunes-cl}-id`, `bigquery-dataset` — populated from `env.yaml`

What got destroyed: the old Cloud Run agent service, its SA, two role bindings, and the `webhook_invokes_agent_aa` Cloud Run IAM member. The webhook's `APP_URL` and `AGENT_HTTP_TIMEOUT` env vars are also gone.

The webhook Cloud Run service has a fresh revision serving the old image with the new env shape (no `APP_URL`, plus `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`). The old image still reads `APP_URL` via `os.getenv` and will throw `ValueError("Agent URL is not configured.")` on every request. **Continue to Phase 2 immediately — there is no agent-side answer until then.**

## Phase 2 — Deploy engines

**Ordering (critical):** `engine-aa-resource-name` / `engine-pp-resource-name` are
created by Phase 1 as empty secret containers with **no version**. The webhook
resolves the engine handle via `gcloud secrets versions access latest` on these
secrets on every inbound WhatsApp message. If the webhook goes live before this
phase seeds those versions, `access latest` returns `NOT_FOUND` and the public
webhook **500s on every request**. So this phase (deploy.py writing the engine
resource names back to the secrets) MUST complete successfully **before** the
webhook is exposed to traffic (Phase 3 redeploy). Never point production WhatsApp
at the webhook until Phase 2 is green.

```bash
gh workflow run deploy-agents.yml -f environment=<env>
# Watch progress
gh run watch
```

Locally (the current default): `scripts/local-deploy/30-agents.sh <env>`. By hand — note `<agent-env>` is `npe` or `prd`, **not** the `dev`/`prd` stack name, and there is no `agro-extension-digital-dev` project:

```bash
cd agents
export GOOGLE_CLOUD_PROJECT=agro-extension-digital-<agent-env>   # npe | prd
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
# Pull runtime config from the secrets we just created:
for k in DATASTORE_AA_ID DATASTORE_PP_ID DATASTORE_GUIDES_ID \
         DATASTORE_FAQ_ID DATASTORE_CHILEPRUNES_CL_ID BIGQUERY_DATASET; do
  secret_id="$(echo $k | tr A-Z_ a-z- )"
  export $k="$(gcloud secrets versions access latest --secret=$secret_id)"
done
uv run python deploy.py --env <agent-env>          # npe | prd
```

`deploy.py` refuses to run if `GOOGLE_CLOUD_PROJECT` disagrees with `--env`, so a stale exported project cannot point one environment's datastore/RAG paths at another environment's engine.

Expected output: `agent_aa: projects/.../reasoningEngines/<id>` and `agent_pp: projects/.../reasoningEngines/<id>`. Both resource names are written back to `engine-{aa,pp}-resource-name` secrets.

## Phase 3 — Webhook image + redeploy

If the runner is online:

```bash
# Push a tag (or merge to main) → build-and-push.yml builds + pushes
# us-central1-docker.pkg.dev/<project>/agro-extension-digital/webhook:<sha>
git push origin feature/agent-runtime-migration
gh run watch
```

Locally (the current default):

```bash
./scripts/local-deploy/10-build-push.sh       <env> --latest
./scripts/local-deploy/40-redeploy-webhook.sh <env>
```

By hand — the image project is **always npe**, for prd too. Pushing to a prd registry produces an image nothing pulls:

```bash
cd webhook-application
SHA=$(git rev-parse --short HEAD)
IMG=us-central1-docker.pkg.dev/agro-extension-digital-npe/agro-extension-digital/webhook
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
# --platform linux/amd64 is mandatory: Cloud Run is amd64-only, and a native
# build on Apple Silicon pushes fine then fails to start with exec-format error.
docker buildx build --platform linux/amd64 --push -t $IMG:$SHA -t $IMG:latest .
```

Then redeploy the Cloud Run service — pushing `:latest` alone does nothing, because Cloud Run pinned a digest at deploy time:

```bash
# service name uses the STACK name (dev|prd); project uses npe|prd
gcloud run services update agent-webhook-<env> \
  --image=$IMG:$SHA \
  --region=us-central1 \
  --project=agro-extension-digital-<agent-env>
```

The env vars are already correct (Phase 1 added `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION`).

## Phase 4 — Smoke

```bash
# Direct engine smoke
gcloud config set project agro-extension-digital-<env>
cd agents
uv run python <<'PY'
import asyncio, vertexai
from google.cloud import secretmanager
from vertexai import agent_engines

vertexai.init(project='agro-extension-digital-<env>', location='us-central1')
sm = secretmanager.SecretManagerServiceClient()

async def smoke(short):
    name = sm.access_secret_version(request={
        'name': f'projects/agro-extension-digital-<env>/secrets/engine-{short}-resource-name/versions/latest'
    }).payload.data.decode()
    eng = agent_engines.get(name)
    await eng.async_create_session(user_id='smoke', session_id='smoke')
    chunks = []
    async for ev in eng.async_stream_query(user_id='smoke', session_id='smoke',
                                           message="Hola, di solo: ok"):
        for p in (ev.get('content') or {}).get('parts') or []:
            if p.get('text'): chunks.append(p['text'])
    print(short, '->', ''.join(chunks)[:80])

asyncio.run(smoke('aa'))
asyncio.run(smoke('pp'))
PY
```

Real WhatsApp end-to-end test from a real phone number — send a question to the dev / prd WhatsApp number. The webhook logs should show `agent_query.start` → `agent_query.complete` events with non-zero `events_received`.

## Phase 5 — Soak

dev: 24-48h. prd: 7 days. Watch Cloud Logging for `agent_query.timeout`, `agent_query.empty_response`, and any `severity>=ERROR`. Threshold (pre-cutover SLO): error rate < 0.5% over a 1h window.

## Rollback

The PR's Phase 5 cleanup destroys the old Cloud Run agent service, so a rollback to "previous behavior" requires reverting the Terraform delete and re-applying. Faster rollback inside a window:

- **Webhook image rollback only** (recovers from a bad new image; keeps engines): `gcloud run services update-traffic agent-webhook-<env> --to-revisions=<previous-revision>=100 --region=us-central1`
- **Engine handle reset** (recovers from a poisoned Secret Manager value): disable the bad version on `engine-{aa,pp}-resource-name`, re-run `deploy.py` to write a fresh version

If the engine itself is failing, `deploy.py` does idempotent update — fix the agent code, push, re-run.

## Per-environment overrides

| Env var | Default | Override when… |
|---|---|---|
| `AGENT_SESSION_TIMEOUT` | 15s | session create is hitting timeouts in soak |
| `AGENT_QUERY_TIMEOUT` | 90s | long-running queries are timing out legitimately |
| `GEMINI_LOCATION` | global | Vertex AI promotes 3.x to regional GA |
| `OTEL_CAPTURE_MESSAGE_CONTENT` | false | debug-only deploy needs verbatim message text in traces (NEVER in prd) |
