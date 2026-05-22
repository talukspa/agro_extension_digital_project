# Deploying the AgroExtensión ADK agents to Google Agent Runtime — Design

| | |
|---|---|
| **Status** | Draft v2 — validated against current Google docs 2026-05-21; pending user review |
| **Date** | 2026-05-21 |
| **Author** | Brainstormed with Claude (Opus 4.7) |
| **Scope** | Full migration of `agents/agent_aa_app` and `agents/agent_pp_app` off Cloud Run onto Vertex AI Agent Runtime, with managed Sessions + Memory Bank. Webhook stays on Cloud Run; rollout is dev (npe) → prd. |
| **Out of scope** | WhatsApp webhook re-platforming, Memory Bank retention/redaction policy, monitoring/alerting policy, BigQuery checkpointer for the LangGraph sub-agent. |

---

## 1. Context

### Today's state

- Two Google ADK agents (`google-adk==1.0.0`) live under `agents/`:
  - `agent_aa_app/agent.py` — root `LlmAgent` for "Adecuación Agroindustrial", composing a Vertex AI Search RAG sub-agent (5 datastores) and a LangGraph text-to-SQL sub-agent over BigQuery.
  - `agent_pp_app/agent.py` — symmetric root agent for "Planificación de Producción".
- Both agents are hosted by one FastAPI app via `google.adk.cli.fast_api.get_fast_api_app(agent_dir=AGENT_DIR)` in `agents/main.py`, packaged in a single Docker image, deployed to Cloud Run (`google_cloud_run_v2_service.cloud_run_name_agent_aa`).
- A separate webhook Cloud Run service (`webhook-application/`) receives WhatsApp messages from Meta, picks the target agent (`ESTANDAR_AA_*` vs `ESTANDAR_PP_*` env vars), and calls the agent service over HTTP with `roles/run.invoker`.
- Infrastructure is Terraform + Terragrunt under `cicd/`, with two GCP projects: `agro-extension-digital-npe` (dev) and `agro-extension-digital-prd`. Region: `us-central1`.
- Conversation state is currently transient: the inner LangGraph BigQuery sub-agent uses `langgraph.checkpoint.memory.InMemorySaver`; there is no durable session store at the FastAPI layer.

### What "Agent Runtime" is, as of May 2026

- **Agent Runtime** is the May 2026 name for **Vertex AI Agent Engine**, rebranded at Google Cloud Next 2026 (April 22–24, 2026) under the umbrella **Gemini Enterprise Agent Platform**. The underlying REST resource is still `aiplatform.googleapis.com/.../reasoningEngines/{id}`, kept for backwards compatibility.
- It's a managed runtime for one agent per resource: one `AdkApp` (one ADK `root_agent`), one staging bundle, one set of env vars, one runtime service account. Google handles containerization, autoscaling, IAM-secured HTTPS endpoints (`:query` and `:streamQuery`), Cloud Trace + Cloud Logging integration, and built-in **Sessions** (short-term, per `user_id` + `session_id`) and **Memory Bank** (long-term per-user facts).
- Pricing (as of May 2026): $0.0864 per vCPU-hour + $0.0090 per GiB-hour on active runtime, billed per second; idle scaled-to-zero engines are not billed. Free tier: 50 vCPU-hours + 100 GiB-hours/month. **Sessions & Memory Bank storage**: $0.25 per 1,000 events/memories. **Memory Bank retrieval**: $0.50 per 1,000 memories returned (first 1,000/month free). Paid GA: 2026-01-28. Vertex AI Search, BigQuery, and model tokens are billed separately under their own rates.
- Supported Python runtimes on Agent Runtime as of May 2026: **3.10, 3.11, 3.12, 3.13, 3.14**. There is no fixed default — the SDK pins the build image to whatever Python version the local interpreter reports at `create()` time.
- ADK packaging path: wrap `root_agent` in `vertexai.agent_engines.AdkApp` (the canonical non-preview path; `vertexai.preview.reasoning_engines.AdkApp` still resolves but is a legacy alias) and deploy via `vertexai.agent_engines.create(...)` (Python SDK) or `adk deploy agent_engine` (CLI). Local code travels via `extra_packages=[...]`; pip deps via `requirements=[...]`; runtime env vars via `env_vars={...}`.

### Decisions locked in during brainstorming

| Decision | Choice |
|---|---|
| End state | Full migration off Cloud Run for the agents (webhook stays on Cloud Run). |
| Rollout | Dev (`npe`) first, then prd after validation. |
| Sessions / Memory | Adopt managed Sessions **and** Memory Bank. |
| IaC posture | Hybrid: Terragrunt for supporting infra (SAs, IAM, GCS, Secret Manager); Python deploy script (`agents/deploy.py`) in CI for the engines themselves. |
| Repo shape | Approach A — minimal lift-and-shift. Keep `agents/` monorepo; add per-agent shims and `deploy.py`. |

---

## 2. Target architecture

```
┌────────────────────────┐
│ WhatsApp Cloud API     │
└──────────┬─────────────┘
           │ HTTPS (verify + messages)
           ▼
┌────────────────────────┐        Secret Manager
│ webhook  (Cloud Run)   │ ───►   engine-aa-resource-name
│   FastAPI + Pydantic   │        engine-pp-resource-name
│   webhook_app_sa       │
└──────────┬─────────────┘
           │ google-cloud-aiplatform SDK
           │ aiplatform.reasoningEngines.streamQuery
           │ (ADC = webhook_app_sa)
           ▼
┌────────────────────────────────────────────────────────────┐
│ Agent Runtime (Vertex AI / Gemini Enterprise Agent Platform)│
│                                                            │
│  reasoningEngines/AA_ID    reasoningEngines/PP_ID          │
│  AdkApp(root_agent=aa)     AdkApp(root_agent=pp)           │
│  runs as agent_aa_runtime  runs as agent_pp_runtime        │
│                                                            │
│  ▸ Managed Sessions (user_id = wa_id, session_id = …)      │
│  ▸ Memory Bank attached per engine                         │
│  ▸ Cloud Trace + Cloud Logging auto-wired                  │
└────────┬──────────────────────────┬────────────────────────┘
         │                          │
         │ Vertex AI Search          │ BigQuery (text-to-SQL)
         ▼                          ▼
    5 datastores                 BIGQUERY_DATASET
    (AA, PP, GUIDES,
     FAQ, CHILEPRUNES_CL)
```

### Per-message data flow

1. Meta posts to the webhook Cloud Run service (URL unchanged).
2. Webhook resolves the target agent (`agent_aa` or `agent_pp`) from existing `ESTANDAR_*_APP_NAME` logic.
3. Webhook reads the corresponding engine resource name from Secret Manager (`engine-aa-resource-name` / `engine-pp-resource-name`), cached per process with `@lru_cache`.
4. Webhook resolves the `session_id` for this `wa_id` by calling `engine.async_list_sessions(user_id=wa_id)` and picking the most recent active session; if none exists (or the latest is older than `SESSION_IDLE_RESET_SECONDS`), calls `engine.async_create_session(user_id=wa_id)`. Agent Runtime is the source of truth for sessions — no extra store needed in the webhook.
5. Webhook calls `engine.async_stream_query(user_id=wa_id, session_id=session_id, message=text)`, concatenates `content.parts[*].text` from streamed events, posts the reply back to WhatsApp.
6. Agent Runtime executes the ADK graph (RAG sub-agent + LangGraph BigQuery sub-agent). Session events persist automatically. Memory Bank extracts long-term facts asynchronously.

### Why two engines, not one

`AdkApp` wraps exactly one `root_agent`. The current single-Cloud-Run-container-hosting-both-agents pattern does not exist on Agent Runtime; each agent gets its own `reasoningEngines/{id}` with its own runtime service account, env vars, scaling knobs, and Memory Bank. The webhook is the join point — it already knows which agent to call per message.

---

## 3. IAM

| Principal | Role(s) | Why |
|---|---|---|
| `webhook_app_sa` (existing) | `roles/aiplatform.user` (project-level), `roles/secretmanager.secretAccessor` on the two engine-name secrets | Call `streamQuery`; read engine resource names at boot |
| `agent_aa_runtime` (new) | `roles/aiplatform.user`, `roles/discoveryengine.viewer`, `roles/bigquery.dataViewer`, `roles/bigquery.jobUser`, `roles/bigquery.readSessionUser`, `roles/cloudtrace.agent`, `roles/logging.logWriter` | Gemini, Vertex AI Search, BigQuery text-to-SQL, telemetry |
| `agent_pp_runtime` (new) | Same as AA | Symmetric |
| GitHub Actions deploy SA (existing) | `roles/aiplatform.admin`, `roles/storage.admin` on the staging bucket | Create/update reasoning engines, upload staging bundle |

Removed at cutover: `google_service_account.agent_aa_app` (today's Cloud Run runtime SA), its `agent_aa_sa_role*` bindings, and `webhook_invokes_agent_aa` (`roles/run.invoker` on the old Cloud Run service).

**Why `roles/aiplatform.user` and not a tighter role:** there is no predefined role named `roles/aiplatform.reasoningEngineUser` or `…reasoningEngineAdmin` in Google's IAM catalog as of May 2026 — `aiplatform.user` is the documented role for callers of `reasoningEngines.query` / `streamQuery`. If we later need to tighten, a custom role containing exactly `aiplatform.reasoningEngines.query` and `aiplatform.reasoningEngines.streamQuery` is the right tool.

---

## 4. Repo changes (Approach A)

### 4.1 New files

**`agents/agent_aa_app/agent_engine_app.py`** (and symmetric `agent_pp_app/agent_engine_app.py`):
```python
from vertexai.agent_engines import AdkApp
from agent_aa_app.agent import root_agent

# When deployed to Agent Runtime, the AdkApp template auto-wires:
#   - session_service → managed Sessions on this engine
#   - memory_service  → Memory Bank on this engine (same reasoningEngines/{id})
# No builders need to be passed unless we want a custom service.
# Tracing is enabled via env vars at deploy time (see deploy.py); enable_tracing
# remains as a soft-deprecated back-compat hint for older ADK versions.
app = AdkApp(agent=root_agent, enable_tracing=True)
```

**`agents/deploy.py`** — idempotent create-or-update for both engines, invoked from CI. See section 8 (Appendix A) for the full file.

### 4.2 Modified files

- `agents/pyproject.toml` — add `google-cloud-aiplatform[adk,agent_engines]>=1.135.0`, `google-cloud-secret-manager`, `google-cloud-discoveryengine`.
- `webhook-application/whatsapp_webhook/utils/agent_client.py` — new module wrapping `vertexai.agent_engines.get(name).async_stream_query(...)` and the session-resolution helper (list-or-create against Agent Runtime). Replaces the previous HTTP client targeting `APP_URL`. See section 8 (Appendix B).
- `webhook-application/whatsapp_webhook/api/*.py` — call the new `agent_client.query_agent(...)` instead of the previous HTTP client. Drop `AGENT_HTTP_TIMEOUT` handling.

### 4.3 Deleted at cutover

- `agents/main.py` — Cloud Run FastAPI host.
- `agents/Dockerfile`.
- `agents/deploy-agent.sh`.
- The agents image build job in `.github/workflows/build-and-push.yml` (the webhook + frontend jobs remain).

---

## 5. IaC delta (`cicd/modules/backend/`)

### 5.1 Removed

- `google_cloud_run_v2_service.cloud_run_name_agent_aa`
- `google_cloud_run_v2_service_iam_member.webhook_invokes_agent_aa`
- `google_service_account.agent_aa_app`
- `google_project_iam_member.agent_aa_sa_role`, `..._discovery`
- `APP_URL` and `AGENT_HTTP_TIMEOUT` env entries on the webhook service

### 5.2 Added

```hcl
resource "google_storage_bucket" "agent_engine_staging" {
  name                        = "${var.project_id}-agent-engine-staging"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false
  lifecycle_rule {
    condition { age = 30 }
    action    { type = "Delete" }
  }
}

resource "google_service_account" "agent_aa_runtime" {
  account_id   = "agent-aa-runtime"
  display_name = "Agent AA — Agent Runtime SA"
  project      = var.project_id
}
resource "google_service_account" "agent_pp_runtime" {
  account_id   = "agent-pp-runtime"
  display_name = "Agent PP — Agent Runtime SA"
  project      = var.project_id
}

locals {
  runtime_roles = [
    "roles/aiplatform.user",
    "roles/discoveryengine.viewer",
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser",
    "roles/bigquery.readSessionUser",
    "roles/cloudtrace.agent",
    "roles/logging.logWriter",
  ]
  runtime_sas = {
    aa = google_service_account.agent_aa_runtime.email
    pp = google_service_account.agent_pp_runtime.email
  }
  runtime_bindings = {
    for pair in setproduct(keys(local.runtime_sas), local.runtime_roles) :
    "${pair[0]}-${pair[1]}" => { sa = local.runtime_sas[pair[0]], role = pair[1] }
  }
}

resource "google_project_iam_member" "runtime_bindings" {
  for_each = local.runtime_bindings
  project  = var.project_id
  role     = each.value.role
  member   = "serviceAccount:${each.value.sa}"
}

resource "google_secret_manager_secret" "engine_aa_name" {
  secret_id = "engine-aa-resource-name"
  project   = var.project_id
  replication { auto {} }
}
resource "google_secret_manager_secret" "engine_pp_name" {
  secret_id = "engine-pp-resource-name"
  project   = var.project_id
  replication { auto {} }
}

resource "google_secret_manager_secret_iam_member" "webhook_reads_engine_aa" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.engine_aa_name.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.webhook_app_sa.email}"
}
resource "google_secret_manager_secret_iam_member" "webhook_reads_engine_pp" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.engine_pp_name.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.webhook_app_sa.email}"
}

resource "google_project_iam_member" "webhook_invokes_engines" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.webhook_app_sa.email}"
}
```

The secret values (engine resource names) are written by `deploy.py` after the first engine create; Terraform manages only the *secret* containers, not their versions.

**TF migration caveat:** the `replication { auto {} }` syntax is current. *Migrating* an existing secret from the older `automatic = true` to `auto {}` triggers a destructive replacement in the hashicorp/google provider ([issues #15885](https://github.com/hashicorp/terraform-provider-google/issues/15885), [#15926](https://github.com/hashicorp/terraform-provider-google/issues/15926)). The two engine-name secrets are net-new here, so this is informational only — but the same caveat applies if we later refactor pre-existing secrets in this module.

---

## 6. CI/CD

### 6.1 New workflow: `.github/workflows/deploy-agents.yml`

```yaml
name: Deploy ADK agents to Agent Runtime

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [npe, prd]
        required: true
        default: npe
  push:
    branches: [main]
    paths:
      - 'agents/**'
      - '.github/workflows/deploy-agents.yml'

concurrency:
  group: deploy-agents-${{ github.event.inputs.environment || 'npe' }}
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: self-hosted
    env:
      ENVIRONMENT: ${{ github.event.inputs.environment || 'npe' }}
      GOOGLE_CLOUD_LOCATION: us-central1
    steps:
      - uses: actions/checkout@v4

      - name: Auth + project
        env:
          GCP_SA_KEY: ${{ secrets.GCP_SA_KEY }}
        run: |
          echo "GOOGLE_CLOUD_PROJECT=agro-extension-digital-${ENVIRONMENT}" >> $GITHUB_ENV
          echo "$GCP_SA_KEY" > /tmp/account.json
          gcloud auth activate-service-account --key-file=/tmp/account.json
          gcloud config set project agro-extension-digital-${ENVIRONMENT}

      - name: Load runtime env vars from Secret Manager
        run: |
          for k in DATASTORE_AA_ID DATASTORE_PP_ID DATASTORE_GUIDES_ID \
                   DATASTORE_FAQ_ID DATASTORE_CHILEPRUNES_CL_ID BIGQUERY_DATASET; do
            v=$(gcloud secrets versions access latest --secret="$(echo $k | tr A-Z_ a-z- )")
            echo "$k=$v" >> $GITHUB_ENV
          done

      - uses: astral-sh/setup-uv@v3

      - name: Install deploy deps
        working-directory: agents
        run: uv sync

      - name: Deploy engines (create or update)
        working-directory: agents
        run: uv run python deploy.py --env "${ENVIRONMENT}"
```

### 6.2 Edit: `.github/workflows/build-and-push.yml`

Remove the *agents* image build/push job. Webhook + frontend jobs unchanged.

### 6.3 Ordering (one-time per env)

1. `deploy.yaml` (Terragrunt) — provisions SAs, IAM, staging bucket, empty Secret Manager containers.
2. `deploy-agents.yml` — builds both engines server-side from the staged bundle, writes resource names to the Secret Manager secrets.
3. Webhook redeploy via the existing webhook build pipeline picks up the new SDK-based client code.

---

## 7. Observability & verification

### 7.1 Observability

- Cloud Trace export from Agent Runtime is driven by env vars (post-ADK 1.18 the `AdkApp(enable_tracing=True)` flag alone is no longer sufficient — see [adk-python#3498](https://github.com/google/adk-python/issues/3498)). `deploy.py` sets the following on both engines:
  - `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true` — emits `gen_ai.*` OpenTelemetry spans without prompt content.
  - `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` — also captures inputs/outputs (toggle off in prd if PII is a concern).
- Agent stdout/stderr land in **Cloud Logging** under `aiplatform.googleapis.com/reasoning_engine`, filterable by `resource.labels.reasoning_engine_id`. A saved log view per env makes triage one click.
- The **Agent Engine console UI** (Vertex AI → Agent Builder → Agent Runtime → engine id) exposes traces, token/latency/error dashboards, and a playground for ad-hoc queries.
- Webhook structured logs gain a `reasoning_engine_id` field on every line for join with Agent Runtime traces.

### 7.2 Smoke tests

After each `deploy.py` run, for each agent:

```bash
RESOURCE_NAME=$(gcloud secrets versions access latest --secret=engine-aa-resource-name)
python -c "
from vertexai import agent_engines
import vertexai, os
vertexai.init(project=os.environ['GOOGLE_CLOUD_PROJECT'], location='us-central1')
eng = agent_engines.get('$RESOURCE_NAME')
s = eng.create_session(user_id='smoke-test')
for ev in eng.stream_query(user_id='smoke-test', session_id=s['id'],
                            message='Hola, ¿qué cultivos manejas?'):
    print(ev)
"
```

Expected: streamed events ending in `content.parts[0].text`. Empty output → check Cloud Logging for the engine.

End-to-end (dev): send a WhatsApp test message; confirm reply text matches what the smoke test produced. The webhook log line for that message should contain the new `reasoning_engine_id`.

---

## 8. Rollout & rollback

### 8.1 Sequence

**Pre-flight PR (infra-only, both envs)** — adds new SAs, staging bucket, secrets, project IAM binding for webhook → `roles/aiplatform.user`. Apply to npe, then prd. No behavior change.

**Dev cutover PR** — lands repo code changes (shims, `deploy.py`, pyproject deps, webhook SDK client). Keeps `agents/main.py`, `Dockerfile`, and the old Cloud Run resource as a fall-back lane.
1. Run `deploy-agents.yml` against npe → engines created, secrets populated.
2. Smoke-test each engine.
3. Redeploy webhook to npe → reads engine names from Secret Manager.
4. End-to-end test via WhatsApp test number.
5. Soak 24–48h with both lanes co-existing (webhook on SDK; Cloud Run agent idle).

**Prod cutover PR**
6. Run `deploy-agents.yml` against prd.
7. Smoke-test prod engines.
8. Redeploy webhook to prd.
9. Watch error rate + latency in Cloud Monitoring for 2 hours.

**Cleanup PR** — only after prd is green for 7 days.
10. Remove `agents/main.py`, `Dockerfile`, `deploy-agent.sh`, the *agents* image build job.
11. Remove `google_cloud_run_v2_service.cloud_run_name_agent_aa`, `google_service_account.agent_aa_app`, `agent_aa_sa_role*` bindings, `webhook_invokes_agent_aa`. Apply Terragrunt to npe, then prd.

### 8.2 Rollback

Until the cleanup PR ships: redeploy the previous webhook image (still has HTTP + ID-token logic against `APP_URL`). Single Cloud Run revision rollback per env. Engines stay deployed but receive no traffic; cost is near-zero at `min_instances=0`.

After cleanup: rollback requires reverting the cleanup PR and re-applying Terragrunt. Still inside one normal release cycle.

---

## 9. Risks & known follow-ups

| Risk / item | Severity | Note |
|---|---|---|
| `LangGraphAgent` uses `InMemorySaver` for the inner BigQuery ReAct loop | Low | Scoped to a single top-level request; Agent Runtime worker recycling can't lose user-visible state because the outer Session holds the transcript. Revisit only if mid-execution durable state becomes a requirement. |
| `extra_packages` directory packaging vs CLI gap ([adk-python#2506](https://github.com/google/adk-python/issues/2506), closed 2025-10-28) | Medium | The original report was a `cwd` path-resolution mistake, not a packaging bug; issue is closed. We use the Python SDK path with explicit `extra_packages=["./agents/agent_aa_app"]`, which sidesteps the CLI's missing `--extra_packages` flag. Inside agent code, always resolve subdir paths via `os.path.dirname(__file__)`. **Robust alternative**: build a wheel (`uv build --wheel agents/agent_aa_app -o dist/`) and pass `extra_packages=["./dist/agent_aa_app-*.whl"]`. The wheel route is Google's documented fix for `src/` layouts and projects with sub-packages ([adk-python#2947](https://github.com/google/adk-python/discussions/2947)); revisit if directory packaging fails. |
| Session resolution is non-idiomatic | Medium | Google's documented pattern is to store `session_id` client-side keyed by `user_id`. We instead call `engine.async_list_sessions(user_id=wa_id)` per inbound message and sort by `last_update_time` descending (the SDK does **not** guarantee return order — explicit sort is required). Cost: $0.25 per 1,000 list events on top of the per-event session billing. **Future enhancement**: add a Firestore (or Cloud Run instance-local cache) `wa_id → (session_id, last_seen)` lookup table to skip the per-message `list_sessions` call. |
| Memory Bank is per-engine, not per-user-across-engines | Medium | `reasoningEngines/AA_ID` and `reasoningEngines/PP_ID` each own an isolated Memory Bank. A user who interacts with AA today and PP tomorrow has **no shared long-term memory** by default. To share, instantiate `VertexAiMemoryBankService(agent_engine_id=SHARED_ID)` inside the other agent's code and point at a single "memory" engine — out of scope for this migration. |
| Pickling / version skew at deploy time | Medium | Pin `langchain*`, `pydantic`, `google-cloud-aiplatform`, `google-adk` versions in `requirements` to match the local interpreter used by CI. CI must run Python 3.10–3.14 — the SDK pins the build image to whatever the local interpreter reports at `create()` time. |
| Memory Bank governance | Out of scope | Retention, redaction, and per-user deletion are a separate compliance design. |
| Monitoring / alerts | Out of scope | A Cloud Monitoring alert on `aiplatform.googleapis.com/reasoning_engine/request/error_count` > 0 for 5 min, per env, is a follow-up spec. |
| Engines aren't managed by Terraform | Accepted | `deploy.py` is idempotent and writes resource names to Terraform-managed secrets, which is the boundary. Re-evaluate if Google ships a clean `google_vertex_ai_reasoning_engine` resource later. |

---

## 10. Appendices

### Appendix A — `agents/deploy.py` (reference)

```python
"""Deploy or update agent_aa and agent_pp on Vertex AI Agent Runtime.

Usage:
    uv run python agents/deploy.py --env npe        # or prd
"""
import argparse
import os
from importlib import import_module
from typing import Optional

import vertexai
from google.cloud import secretmanager
from vertexai import agent_engines

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]>=1.135.0",
    "google-adk>=1.0.0",
    "langchain-community",
    "langchain-google-vertexai",
    "langgraph",
    "sqlalchemy-bigquery",
    "google-cloud-bigquery-storage",
    "google-cloud-discoveryengine",
]

AGENTS = {
    "agent_aa": {
        "module_path": "agents/agent_aa_app",
        "app_module": "agent_aa_app.agent_engine_app",
        "display_name": "Adecuación Agroindustrial",
        "secret_id": "engine-aa-resource-name",
    },
    "agent_pp": {
        "module_path": "agents/agent_pp_app",
        "app_module": "agent_pp_app.agent_engine_app",
        "display_name": "Planificación de Producción",
        "secret_id": "engine-pp-resource-name",
    },
}

RUNTIME_ENV_KEYS = [
    "DATASTORE_AA_ID", "DATASTORE_PP_ID", "DATASTORE_GUIDES_ID",
    "DATASTORE_FAQ_ID", "DATASTORE_CHILEPRUNES_CL_ID", "BIGQUERY_DATASET",
]

# Telemetry env vars are required to export traces post-ADK 1.18 (the
# AdkApp(enable_tracing=True) flag alone no longer suffices; see
# https://github.com/google/adk-python/issues/3498).
TELEMETRY_ENV = {
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
}

def find_existing(display_name: str) -> Optional[str]:
    for eng in agent_engines.list():
        if eng.display_name == display_name:
            return eng.resource_name
    return None

def write_secret(project: str, secret_id: str, value: str) -> None:
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project}"
    name = f"{parent}/secrets/{secret_id}"
    try:
        client.get_secret(request={"name": name})
    except Exception:
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},  # API still uses 'automatic'; TF provider uses 'auto'
            }
        )
    client.add_secret_version(
        request={"parent": name, "payload": {"data": value.encode()}}
    )

def deploy_one(key: str, cfg: dict, project: str, sa: str) -> None:
    mod = import_module(cfg["app_module"])
    existing = find_existing(cfg["display_name"])
    env_vars = {k: os.environ[k] for k in RUNTIME_ENV_KEYS} | TELEMETRY_ENV
    kwargs = dict(
        agent_engine=mod.app,
        requirements=REQUIREMENTS,
        extra_packages=[cfg["module_path"]],
        display_name=cfg["display_name"],
        env_vars=env_vars,
        service_account=sa,
        min_instances=0,
        max_instances=3,
    )
    if existing:
        # update() is an instance method on AgentEngine, not a module-level
        # function — must fetch the engine first, then call .update(**kwargs).
        engine = agent_engines.get(existing)
        engine = engine.update(**kwargs)
    else:
        engine = agent_engines.create(**kwargs)
    write_secret(project, cfg["secret_id"], engine.resource_name)
    print(f"{key}: {engine.resource_name}")

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["npe", "prd"], required=True)
    args = p.parse_args()
    project = f"agro-extension-digital-{args.env}"
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = f"gs://{project}-agent-engine-staging"
    vertexai.init(project=project, location=location, staging_bucket=bucket)
    sa_for = {
        "agent_aa": f"agent-aa-runtime@{project}.iam.gserviceaccount.com",
        "agent_pp": f"agent-pp-runtime@{project}.iam.gserviceaccount.com",
    }
    for key, cfg in AGENTS.items():
        deploy_one(key, cfg, project, sa_for[key])

if __name__ == "__main__":
    main()
```

### Appendix B — `webhook-application/whatsapp_webhook/utils/agent_client.py` (reference)

```python
"""Vertex AI Agent Runtime client used by the WhatsApp webhook."""
import os
from functools import lru_cache

import vertexai
from google.cloud import secretmanager
from vertexai import agent_engines


@lru_cache(maxsize=1)
def _init() -> None:
    vertexai.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
    )


@lru_cache(maxsize=2)
def get_engine(app_name: str):
    _init()
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    secret_id = f"engine-{app_name}-resource-name"
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    sm = secretmanager.SecretManagerServiceClient()
    resource_name = sm.access_secret_version(request={"name": name}).payload.data.decode()
    return agent_engines.get(resource_name)


SESSION_IDLE_RESET_SECONDS = int(os.environ.get("SESSION_IDLE_RESET_SECONDS", "21600"))  # 6h


def _seconds_since_epoch(now_epoch: float) -> float:
    """Sessions expose last_update_time as a float (seconds-since-epoch, UTC)."""
    import time
    return time.time() - float(now_epoch)


async def resolve_session(engine, user_id: str) -> str:
    """Return the freshest active session id for user_id, creating one if needed.

    The AdkApp SDK does NOT guarantee ordering on async_list_sessions, and it
    returns a ListSessionsResponse object (not a bare list) — must read
    `.sessions` and sort client-side by last_update_time descending.
    """
    response = await engine.async_list_sessions(user_id=user_id)
    sessions = sorted(
        getattr(response, "sessions", None) or [],
        key=lambda s: s.get("last_update_time", 0.0),
        reverse=True,
    )
    if sessions:
        freshest = sessions[0]
        last = freshest.get("last_update_time")
        if last is not None and _seconds_since_epoch(last) < SESSION_IDLE_RESET_SECONDS:
            return freshest["id"]
    new_session = await engine.async_create_session(user_id=user_id)
    return new_session["id"]


async def query_agent(app_name: str, user_id: str, message: str) -> str:
    engine = get_engine(app_name)
    session_id = await resolve_session(engine, user_id)
    out: list[str] = []
    async for event in engine.async_stream_query(
        user_id=user_id, session_id=session_id, message=message
    ):
        # event["content"]["parts"][i] is either {"text": ...} (assistant token)
        # or {"function_call": ...} / {"function_response": ...} (tool events).
        # The `if text:` guard naturally skips tool-call parts.
        content = event.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if text:
                out.append(text)
    return "".join(out)
```

### Appendix C — Authoritative sources (as of 2026-05-21)

- [Agent Runtime overview (Gemini Enterprise Agent Platform)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime)
- [Vertex AI Agent Engine overview](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Deploy an agent (Agent Engine docs)](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)
- [`vertexai.agent_engines.AdkApp` Python reference](https://docs.cloud.google.com/python/docs/reference/vertexai/latest/vertexai.agent_engines.AdkApp)
- [ReasoningEngines REST resource](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/projects.locations.reasoningEngines)
- [streamQuery method](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/projects.locations.reasoningEngines/streamQuery)
- [Agent observability / Cloud Trace + Logging](https://docs.cloud.google.com/stackdriver/docs/observability/agent-observability)
- [Managing access for deployed agents (IAM)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/manage-agent-access)
- [Memory Bank overview](https://docs.cloud.google.com/agent-builder/agent-engine/memory-bank/overview)
- [Quotas](https://docs.cloud.google.com/agent-builder/quotas)
- [Pricing — Gemini Enterprise Agent Platform](https://cloud.google.com/vertex-ai/pricing)
- [ADK deploy guide — Agent Runtime](https://adk.dev/deploy/agent-runtime/)
- [adk-samples deploy.py examples](https://github.com/google/adk-samples)
- [Cloud Next 2026 — Gemini Enterprise Agent Platform announcement](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform)
- [Cloud Next 2026 — more ways to build and scale AI agents](https://cloud.google.com/blog/products/ai-machine-learning/more-ways-to-build-and-scale-ai-agents-with-vertex-ai-agent-builder)
- [Vertex AI predefined IAM roles](https://docs.cloud.google.com/iam/docs/roles-permissions/aiplatform)
- [Agent observability — ADK + Cloud Trace env vars](https://docs.cloud.google.com/stackdriver/docs/instrumentation/ai-agent-adk)
- [Manage sessions with ADK (reasoningEngines.sessions API)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/sessions/manage-sessions-adk)
- [Memory Bank ADK quickstart](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/quickstart-adk)
- Source: [`vertexai/agent_engines/_agent_engines.py`](https://github.com/googleapis/python-aiplatform/blob/main/vertexai/agent_engines/_agent_engines.py) and [`templates/adk.py`](https://github.com/googleapis/python-aiplatform/blob/main/vertexai/agent_engines/templates/adk.py)
- Closed issue: [adk-python#2506 — extra_packages subdirectory packaging (closed 2025-10-28)](https://github.com/google/adk-python/issues/2506)
- Related discussion: [adk-python#2947 — wheel-based packaging for sub-packages](https://github.com/google/adk-python/discussions/2947)
- Related issue: [adk-python#3498 — `enable_tracing=True` no longer self-sufficient post-1.18](https://github.com/google/adk-python/issues/3498)
- Provider issue: [hashicorp/terraform-provider-google#15885 — Secret Manager replication block migration](https://github.com/hashicorp/terraform-provider-google/issues/15885)
