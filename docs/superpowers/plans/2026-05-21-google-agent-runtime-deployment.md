# Google Agent Runtime Deployment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the two Google ADK agents (`agent_aa_app`, `agent_pp_app`) off Cloud Run onto Vertex AI Agent Runtime with managed Sessions and Memory Bank; rewrite the webhook's agent client to use the Vertex AI SDK; provision supporting infrastructure via Terragrunt; roll out dev → prd with a fall-back lane until soak passes.

**Architecture:** One `reasoningEngines/{id}` per ADK agent (two engines: AA and PP). Each engine wraps `vertexai.agent_engines.AdkApp(root_agent=…)`. Webhook reads each engine's stable resource name from Secret Manager and calls `async_stream_query`. Sessions are deterministic per `wa_id` (matches existing convention). Infra (SAs, IAM, GCS staging bucket, Secret Manager containers) is Terragrunt-managed; engine resources are managed by an idempotent `agents/deploy.py` invoked from a new GitHub Actions workflow.

**Tech Stack:** Python 3.12, `google-adk` ≥ 1.0, `google-cloud-aiplatform[adk,agent_engines]` ≥ 1.135, `google-cloud-secret-manager`, FastAPI (webhook), Terraform + Terragrunt + hashicorp/google provider, GitHub Actions on a self-hosted runner, `uv` for Python dependency management.

**Reference spec:** `docs/superpowers/specs/2026-05-21-google-agent-runtime-deployment-design.md` (read first if any task is ambiguous).

---

## File Map

**Created (this plan):**
- `agents/agent_aa_app/agent_engine_app.py` — AdkApp shim wrapping `root_agent` for AA.
- `agents/agent_pp_app/agent_engine_app.py` — AdkApp shim wrapping `root_agent` for PP.
- `agents/deploy.py` — idempotent create-or-update for both reasoning engines; writes resource names to Secret Manager.
- `agents/tests/__init__.py`
- `agents/tests/test_deploy.py` — unit tests for the deploy script's pure helpers.
- `webhook-application/tests/external_services/__init__.py`
- `webhook-application/tests/external_services/test_agent_client.py` — unit tests for the rewritten webhook agent client.
- `.github/workflows/deploy-agents.yml` — manual + on-push workflow that runs `agents/deploy.py` per env.

**Modified (this plan):**
- `agents/pyproject.toml` — add Vertex AI Agent Engine + Secret Manager + Discovery Engine deps.
- `webhook-application/pyproject.toml` — add `google-cloud-aiplatform[agent_engines]` and `google-cloud-secret-manager`; drop `httpx` if no other callers (TBD via grep — see Task 7 step 2).
- `webhook-application/whatsapp_webhook/external_services/agent_client.py` — full rewrite, preserving the public signatures `send_to_agent(...)` and `create_agent_session(...)`.
- `webhook-application/whatsapp_webhook/utils/app_config.py` — remove `agent_url` and `agent_http_timeout` fields.
- `cicd/modules/backend/main.tf` — add GCS staging bucket, two runtime SAs, IAM bindings, Secret Manager containers, webhook → `roles/aiplatform.user` binding. (Old Cloud Run agent resources are NOT removed here — removed in the cleanup phase.)
- `cicd/modules/backend/variables.tf` — no new variables needed in the pre-flight phase (all new resources derive from `project_id` / `region`); cleanup phase will retire `cloud_run_name_agent_aa`, `service_account_id_agent_aa`, etc.
- `.github/workflows/build-and-push.yml` — (in the cleanup phase) remove the agents image build/push step.

**Deleted (cleanup phase only, after prd has soaked 7 days):**
- `agents/main.py`
- `agents/Dockerfile`
- `agents/deploy-agent.sh`
- `cicd/modules/backend/main.tf` — the `google_cloud_run_v2_service.cloud_run_name_agent_aa`, `google_service_account.agent_aa_app`, related role bindings, and `webhook_invokes_agent_aa`.

---

## Phase 0 — Branch + worktree setup

### Task 0: Create a feature branch

**Files:** none (git only).

- [ ] **Step 1: Verify clean working tree on `main`**

Run: `git status -sb && git log -1 --oneline`
Expected: branch shows `## main`, no staged/unstaged changes other than untracked files unrelated to this plan, last commit is the spec-alignment commit.

- [ ] **Step 2: Create the feature branch**

Run: `git checkout -b feature/agent-runtime-migration-phase1`

Expected: switched to a new branch.

---

## Phase 1 — Pre-flight infrastructure (additive only)

### Task 1: Add Terraform resources for the new infra (still additive)

**Files:**
- Modify: `cicd/modules/backend/main.tf` — append the new block at the end of the file (before the `terraform { backend "gcs" {} }` block which must remain last).

- [ ] **Step 1: Open `cicd/modules/backend/main.tf` and locate the line `terraform {`**

Run: `grep -n 'terraform {' cicd/modules/backend/main.tf`
Expected: a single match around the bottom of the file.

- [ ] **Step 2: Insert the new resources directly above that line**

Use Edit. Insert this block immediately before the `terraform { backend "gcs" {} }` block:

```hcl
# --------------------------------------------------------------------
# Agent Runtime (Vertex AI / Gemini Enterprise Agent Platform) — Phase 1
# Additive resources. The old Cloud Run agent service and SA stay in
# place until the cleanup phase (post-soak).
# --------------------------------------------------------------------

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

- [ ] **Step 3: Verify `terraform fmt` clean**

Run: `cd cicd/modules/backend && terraform fmt -check -recursive`
Expected: no output (file is already formatted). If output appears, run `terraform fmt -recursive` and re-verify.

- [ ] **Step 4: `terraform init` + `terraform validate` (local syntax check)**

Run: `cd cicd/modules/backend && terraform init -backend=false && terraform validate`
Expected: `Success! The configuration is valid.`

- [ ] **Step 5: Commit**

```bash
git add cicd/modules/backend/main.tf
git commit -m "infra(agent-runtime): add SAs, bucket, secrets, IAM (additive, pre-flight)"
```

### Task 2: Terragrunt plan against npe (dev)

**Files:** none (read-only validation).

- [ ] **Step 1: Authenticate with the dev SA**

Run (the user must execute this; you cannot do it yourself if credentials aren't preloaded — ask them to run `! gcloud auth login` first):
```
gcloud config set project agro-extension-digital-npe
gcloud auth application-default login
```

- [ ] **Step 2: `terragrunt plan` in the dev stack**

Run: `cd cicd/stacks/dev && terragrunt plan -no-color | tee /tmp/agent-runtime-dev-plan.txt`

Expected: plan shows ONLY additions:
- 1 × `google_storage_bucket.agent_engine_staging`
- 2 × `google_service_account` (agent_aa_runtime, agent_pp_runtime)
- 14 × `google_project_iam_member.runtime_bindings` (2 SAs × 7 roles)
- 2 × `google_secret_manager_secret` (engine_aa_name, engine_pp_name)
- 2 × `google_secret_manager_secret_iam_member` (webhook reads)
- 1 × `google_project_iam_member.webhook_invokes_engines`
- Zero changes or destroys to existing resources

If the plan shows any change/destroy on existing resources, **stop and investigate** before proceeding.

- [ ] **Step 3: Confirm with the user before applying**

State: "Plan is additive only — 22 resources to add, 0 to change, 0 to destroy. Proceed with apply to dev?" Wait for confirmation.

### Task 3: Terragrunt apply against npe (dev)

**Files:** none.

- [ ] **Step 1: Apply**

Run: `cd cicd/stacks/dev && terragrunt apply -auto-approve`

Expected: 22 resources created, no errors.

- [ ] **Step 2: Verify the staging bucket exists**

Run: `gcloud storage buckets list --filter='name:agro-extension-digital-npe-agent-engine-staging' --format='value(name)'`

Expected: one line: `agro-extension-digital-npe-agent-engine-staging`.

- [ ] **Step 3: Verify the two runtime SAs exist**

Run: `gcloud iam service-accounts list --project=agro-extension-digital-npe --filter='email:agent-aa-runtime@* OR email:agent-pp-runtime@*' --format='value(email)'`

Expected: two lines: `agent-aa-runtime@agro-extension-digital-npe.iam.gserviceaccount.com`, `agent-pp-runtime@agro-extension-digital-npe.iam.gserviceaccount.com`.

- [ ] **Step 4: Verify the two empty secrets exist**

Run: `gcloud secrets list --project=agro-extension-digital-npe --filter='name:engine-aa-resource-name OR name:engine-pp-resource-name' --format='value(name)'`

Expected: two lines (the secret containers; they have no versions yet — that's expected).

### Task 4: Terragrunt plan + apply against prd

**Files:** none.

- [ ] **Step 1: Switch to prd project**

Run: `gcloud config set project agro-extension-digital-prd`

- [ ] **Step 2: `terragrunt plan` in the prd stack**

Run: `cd cicd/stacks/prd && terragrunt plan -no-color | tee /tmp/agent-runtime-prd-plan.txt`

Expected: identical shape to dev — 22 additions, 0 changes, 0 destroys.

- [ ] **Step 3: Confirm with the user before applying to prd**

State: "PRD plan matches dev shape exactly. Apply to production?" Wait for confirmation.

- [ ] **Step 4: Apply**

Run: `cd cicd/stacks/prd && terragrunt apply -auto-approve`

Expected: 22 resources created, no errors.

- [ ] **Step 5: Verify prd resources analogously to Task 3 Steps 2–4 (substitute project id)**

### Task 5: Open the pre-flight PR

**Files:** none (git only).

- [ ] **Step 1: Push the branch**

Run: `git push -u origin feature/agent-runtime-migration-phase1`

- [ ] **Step 2: Open a PR**

Run:
```bash
gh pr create --title "infra(agent-runtime): pre-flight SAs/bucket/secrets/IAM (additive)" --body "$(cat <<'EOF'
## Summary
- Adds two runtime SAs (agent_aa_runtime, agent_pp_runtime) with the role set documented in the spec
- Adds a regional GCS staging bucket per env with a 30-day lifecycle rule
- Adds two empty Secret Manager containers (engine-aa-resource-name, engine-pp-resource-name)
- Grants webhook_app_sa roles/aiplatform.user and secretAccessor on the new secrets

All changes are additive — no existing resource is altered or removed. Old Cloud Run agent resources remain in place; this PR just lays the rails.

Applied to npe and prd; verified the new SAs, bucket, and secret containers exist in both projects.

## Test plan
- [ ] terraform validate clean
- [ ] terragrunt plan dev: 22 additions / 0 changes / 0 destroys
- [ ] terragrunt apply dev succeeded
- [ ] terragrunt plan prd: 22 additions / 0 changes / 0 destroys
- [ ] terragrunt apply prd succeeded
- [ ] Verified SAs, bucket, and secrets in both projects via gcloud

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: PR URL printed. Wait for review + merge before proceeding to Phase 2.

---

## Phase 2 — Repo code changes (no deploy yet)

### Task 6: Create a new feature branch for the code phase

**Files:** none.

- [ ] **Step 1: After Phase 1 PR merges, sync main and branch**

```bash
git checkout main
git pull
git checkout -b feature/agent-runtime-migration-phase2
```

### Task 7: Inventory remaining `httpx`/`APP_URL` callers in the webhook

**Files:** none — read-only.

- [ ] **Step 1: Grep for `httpx` usage in the webhook**

Run: `grep -rln 'httpx\|APP_URL\|AGENT_HTTP_TIMEOUT\|agent_url\|agent_http_timeout' webhook-application/whatsapp_webhook 2>/dev/null`

Expected (typical): only `external_services/agent_client.py` and `external_services/whatsapp_client.py` use `httpx`, and `utils/app_config.py` defines the two env-var fields. Anything else surfaces here so we don't miss callers.

- [ ] **Step 2: Note whether `httpx` has callers other than `agent_client.py`**

If `external_services/whatsapp_client.py` (or any other file) uses `httpx`, **keep `httpx` in `pyproject.toml`** (do NOT remove it in Task 12). Document this decision in the commit message for Task 12.

### Task 8: Add the AA AdkApp shim (TDD)

**Files:**
- Create: `agents/agent_aa_app/agent_engine_app.py`
- Test: `agents/tests/__init__.py`, `agents/tests/test_agent_engine_app.py`

- [ ] **Step 1: Create an empty `agents/tests/__init__.py`**

Use Write with content `""`.

- [ ] **Step 2: Write the failing import-and-shape test for AA**

Create `agents/tests/test_agent_engine_app.py`:
```python
"""Smoke tests for the AdkApp shims that ship to Agent Runtime."""
import importlib

import pytest


def test_aa_shim_exposes_app_attribute():
    """The deploy script imports `app` from the shim — guard against drift."""
    mod = importlib.import_module("agent_aa_app.agent_engine_app")
    assert hasattr(mod, "app"), "agent_aa_app.agent_engine_app must export `app`"


def test_aa_shim_app_wraps_root_agent():
    """app.agent must be the package's root_agent (one engine, one root agent)."""
    mod = importlib.import_module("agent_aa_app.agent_engine_app")
    from agent_aa_app.agent import root_agent
    assert mod.app.agent is root_agent
```

- [ ] **Step 3: Run the failing test**

Run: `cd agents && uv run --extra dev pytest tests/test_agent_engine_app.py::test_aa_shim_exposes_app_attribute -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'agent_aa_app.agent_engine_app'`.

- [ ] **Step 4: Implement `agents/agent_aa_app/agent_engine_app.py`**

Use Write:
```python
"""AdkApp shim wrapping agent_aa_app's root_agent for Agent Runtime deploy.

When deployed via vertexai.agent_engines.create(), the AdkApp template
auto-wires the default session_service (Agent Runtime managed Sessions)
and memory_service (Memory Bank on this engine's resource id), so no
builders are passed here. Tracing is enabled via env vars at deploy time
(see agents/deploy.py); `enable_tracing=True` remains as soft-deprecated
back-compat for older ADK versions.
"""
from vertexai.agent_engines import AdkApp

from agent_aa_app.agent import root_agent

app = AdkApp(agent=root_agent, enable_tracing=True)
```

- [ ] **Step 5: Run both tests**

Run: `cd agents && uv run --extra dev pytest tests/test_agent_engine_app.py -v -k "aa_shim"`
Expected: both `test_aa_shim_*` tests PASS. (If `vertexai.agent_engines` import fails, that means deps aren't installed yet — that's the next task; for now Step 5 may need to wait until after Task 10.)

If Step 5 cannot pass yet (because `vertexai.agent_engines` is missing from `pyproject.toml`), skip running the test now and rerun it after Task 10. Document this in Task 10 step 5.

- [ ] **Step 6: Commit**

```bash
git add agents/tests/__init__.py agents/tests/test_agent_engine_app.py agents/agent_aa_app/agent_engine_app.py
git commit -m "feat(agents): add AA AdkApp shim for Agent Runtime deploy"
```

### Task 9: Add the PP AdkApp shim (TDD)

**Files:**
- Create: `agents/agent_pp_app/agent_engine_app.py`
- Modify: `agents/tests/test_agent_engine_app.py` — append PP tests.

- [ ] **Step 1: Append the failing PP tests**

Edit `agents/tests/test_agent_engine_app.py`, appending:
```python
def test_pp_shim_exposes_app_attribute():
    mod = importlib.import_module("agent_pp_app.agent_engine_app")
    assert hasattr(mod, "app"), "agent_pp_app.agent_engine_app must export `app`"


def test_pp_shim_app_wraps_root_agent():
    mod = importlib.import_module("agent_pp_app.agent_engine_app")
    from agent_pp_app.agent import root_agent
    assert mod.app.agent is root_agent
```

- [ ] **Step 2: Run — should fail with `ModuleNotFoundError`**

Run: `cd agents && uv run --extra dev pytest tests/test_agent_engine_app.py::test_pp_shim_exposes_app_attribute -v` (after deps are installed in Task 10)
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `agents/agent_pp_app/agent_engine_app.py`**

Use Write:
```python
"""AdkApp shim wrapping agent_pp_app's root_agent for Agent Runtime deploy.

Mirror of agent_aa_app/agent_engine_app.py — see that file for the why.
"""
from vertexai.agent_engines import AdkApp

from agent_pp_app.agent import root_agent

app = AdkApp(agent=root_agent, enable_tracing=True)
```

- [ ] **Step 4: Run — should pass**

Run: `cd agents && uv run --extra dev pytest tests/test_agent_engine_app.py -v` (after Task 10 deps land)
Expected: 4 tests passing.

- [ ] **Step 5: Commit**

```bash
git add agents/tests/test_agent_engine_app.py agents/agent_pp_app/agent_engine_app.py
git commit -m "feat(agents): add PP AdkApp shim for Agent Runtime deploy"
```

### Task 10: Update `agents/pyproject.toml`

**Files:**
- Modify: `agents/pyproject.toml`.

- [ ] **Step 1: Add deps**

Edit `agents/pyproject.toml` — extend `dependencies` to:
```toml
dependencies = [
    "google-adk==1.0.0",
    "google-cloud-aiplatform[adk,agent_engines]>=1.135.0",
    "google-cloud-secret-manager>=2.20.0",
    "google-cloud-discoveryengine>=0.13.0",
    "langchain_community",
    "langchain_google_vertexai",
    "langgraph",
    "sqlalchemy-bigquery",
    "google-cloud-bigquery-storage",
    "ipykernel",
]
```

Also add a `[dependency-groups]` table at the bottom (uv convention; if the project already uses optional-dependencies, mirror the existing style):
```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

- [ ] **Step 2: Run `uv lock`**

Run: `cd agents && uv lock`
Expected: `uv.lock` is updated; no errors.

- [ ] **Step 3: Run `uv sync --group dev`**

Run: `cd agents && uv sync --group dev`
Expected: installs the new deps + dev group.

- [ ] **Step 4: Run the shim tests from Tasks 8–9**

Run: `cd agents && uv run pytest tests/test_agent_engine_app.py -v`
Expected: 4 tests passing.

- [ ] **Step 5: Commit**

```bash
git add agents/pyproject.toml agents/uv.lock
git commit -m "chore(agents): add Vertex AI Agent Engine, Secret Manager, Discovery Engine deps"
```

### Task 11: Add `agents/deploy.py` (TDD on the pure helpers)

**Files:**
- Create: `agents/deploy.py`
- Test: `agents/tests/test_deploy.py`

- [ ] **Step 1: Write the failing tests for the pure helpers**

Create `agents/tests/test_deploy.py`:
```python
"""Unit tests for agents/deploy.py pure helpers.

Network-touching paths (vertexai.init, agent_engines.create/list, Secret
Manager) are NOT tested here — they are covered by Phase 3's live smoke
test against the dev project.
"""
from unittest.mock import MagicMock, patch

import pytest


def test_env_vars_for_collects_required_runtime_keys(monkeypatch):
    """env_vars_for must read exactly the runtime + telemetry env keys."""
    from agents import deploy
    for k, v in {
        "DATASTORE_AA_ID": "ds-aa",
        "DATASTORE_PP_ID": "ds-pp",
        "DATASTORE_GUIDES_ID": "ds-g",
        "DATASTORE_FAQ_ID": "ds-faq",
        "DATASTORE_CHILEPRUNES_CL_ID": "ds-cl",
        "BIGQUERY_DATASET": "ds-bq",
    }.items():
        monkeypatch.setenv(k, v)
    env = deploy.env_vars_for("agent_aa")
    assert env["DATASTORE_AA_ID"] == "ds-aa"
    assert env["BIGQUERY_DATASET"] == "ds-bq"
    # Telemetry env must be injected automatically.
    assert env["GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"] == "true"
    assert env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == "true"


def test_env_vars_for_raises_when_required_key_missing(monkeypatch):
    monkeypatch.delenv("DATASTORE_AA_ID", raising=False)
    from agents import deploy
    with pytest.raises(KeyError):
        deploy.env_vars_for("agent_aa")


def test_find_existing_returns_resource_name_on_match(monkeypatch):
    from agents import deploy
    fake = MagicMock(display_name="Adecuación Agroindustrial",
                     resource_name="projects/p/locations/us-central1/reasoningEngines/123")
    monkeypatch.setattr(deploy.agent_engines, "list", lambda: [fake])
    assert deploy.find_existing("Adecuación Agroindustrial") == fake.resource_name


def test_find_existing_returns_none_on_no_match(monkeypatch):
    from agents import deploy
    monkeypatch.setattr(deploy.agent_engines, "list", lambda: [])
    assert deploy.find_existing("nope") is None
```

- [ ] **Step 2: Run — should fail with `ModuleNotFoundError: No module named 'agents.deploy'`**

Run: `cd agents && uv run pytest tests/test_deploy.py -v`
Expected: all 4 tests FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `agents/deploy.py`**

Use Write — full file from spec Appendix A, reproduced here verbatim so the engineer doesn't have to cross-reference:

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

# Telemetry env vars required post-ADK 1.18 to actually export traces.
# See https://github.com/google/adk-python/issues/3498.
TELEMETRY_ENV = {
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
}


def env_vars_for(agent_key: str) -> dict[str, str]:
    base = {k: os.environ[k] for k in RUNTIME_ENV_KEYS}
    return base | TELEMETRY_ENV


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
                "secret": {"replication": {"automatic": {}}},
            }
        )
    client.add_secret_version(
        request={"parent": name, "payload": {"data": value.encode()}}
    )


def deploy_one(key: str, cfg: dict, project: str, sa: str) -> None:
    mod = import_module(cfg["app_module"])
    existing = find_existing(cfg["display_name"])
    kwargs = dict(
        agent_engine=mod.app,
        requirements=REQUIREMENTS,
        extra_packages=[cfg["module_path"]],
        display_name=cfg["display_name"],
        env_vars=env_vars_for(key),
        service_account=sa,
        min_instances=0,
        max_instances=3,
    )
    if existing:
        # update() is an instance method on AgentEngine, not a module-level
        # function — fetch the engine first, then call .update(**kwargs).
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

- [ ] **Step 4: Run the tests**

Run: `cd agents && uv run pytest tests/test_deploy.py -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/deploy.py agents/tests/test_deploy.py
git commit -m "feat(agents): add deploy.py — idempotent create-or-update for both engines"
```

### Task 12: Rewrite the webhook agent client (TDD)

**Files:**
- Modify: `webhook-application/whatsapp_webhook/external_services/agent_client.py` (full rewrite, preserving public signatures).
- Create: `webhook-application/tests/external_services/__init__.py`, `webhook-application/tests/external_services/test_agent_client.py`

- [ ] **Step 1: Create the test directory + __init__.py**

Use Write to create `webhook-application/tests/external_services/__init__.py` with content `""`.

- [ ] **Step 2: Write the failing tests**

Create `webhook-application/tests/external_services/test_agent_client.py`:
```python
"""Unit tests for the rewritten Vertex AI Agent Runtime client.

Tests are async (pytest-asyncio is already configured in pyproject.toml).
All network calls are stubbed via mocks — no GCP creds required.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.api_core import exceptions as gax


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    # Reset the lru_caches so each test gets a fresh engine.
    from whatsapp_webhook.external_services import agent_client
    agent_client._init.cache_clear()
    agent_client.get_engine.cache_clear()


@pytest.mark.asyncio
async def test_create_agent_session_returns_existing_on_already_exists():
    """get_or_create semantics: AlreadyExists -> async_get_session is called."""
    from whatsapp_webhook.external_services import agent_client

    engine = MagicMock()
    engine.async_create_session = AsyncMock(side_effect=gax.AlreadyExists("dup"))
    engine.async_get_session = AsyncMock(return_value={"id": "+56999", "events": []})
    with patch.object(agent_client, "get_engine", return_value=engine):
        out = await agent_client.create_agent_session(
            user_id="+56999", app_name="agent_aa", session_id="+56999",
        )
    assert out["id"] == "+56999"
    engine.async_get_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_agent_session_returns_new_when_absent():
    from whatsapp_webhook.external_services import agent_client

    engine = MagicMock()
    engine.async_create_session = AsyncMock(return_value={"id": "+56999"})
    with patch.object(agent_client, "get_engine", return_value=engine):
        out = await agent_client.create_agent_session(
            user_id="+56999", app_name="agent_aa", session_id="+56999",
        )
    assert out["id"] == "+56999"
    engine.async_create_session.assert_awaited_once_with(
        user_id="+56999", session_id="+56999",
    )


@pytest.mark.asyncio
async def test_send_to_agent_concatenates_assistant_text():
    """Multiple events with text parts -> concatenated response string."""
    from whatsapp_webhook.external_services import agent_client

    async def fake_stream(*, user_id, session_id, message):
        yield {"content": {"parts": [{"text": "Hola "}]}}
        yield {"content": {"parts": [{"function_call": {"name": "search"}}]}}
        yield {"content": {"parts": [{"text": "mundo."}]}}

    engine = MagicMock()
    engine.async_stream_query = lambda **kw: fake_stream(**kw)
    with patch.object(agent_client, "get_engine", return_value=engine):
        result = await agent_client.send_to_agent(
            app_name="agent_aa", user_id="+56999", session_id="+56999",
            message="hola",
        )
    assert result["response"] == "Hola mundo."
    assert len(result["raw_response"]) == 3


@pytest.mark.asyncio
async def test_send_to_agent_returns_error_payload_when_no_text():
    """Tool-call-only stream -> empty string -> error payload."""
    from whatsapp_webhook.external_services import agent_client

    async def fake_stream(*, user_id, session_id, message):
        yield {"content": {"parts": [{"function_call": {"name": "search"}}]}}

    engine = MagicMock()
    engine.async_stream_query = lambda **kw: fake_stream(**kw)
    with patch.object(agent_client, "get_engine", return_value=engine):
        result = await agent_client.send_to_agent(
            app_name="agent_aa", user_id="+56999", session_id="+56999",
            message="hola",
        )
    assert "Error" in result["response"]
```

- [ ] **Step 3: Run — should fail**

Run: `cd webhook-application && uv run --extra test pytest tests/external_services/test_agent_client.py -v`
Expected: tests fail because the rewritten functions don't exist yet (or because the existing httpx-based versions don't accept these mocks).

- [ ] **Step 4: Rewrite `external_services/agent_client.py`**

Use Write (full replacement) with the content from spec Appendix B:

```python
"""Vertex AI Agent Runtime client used by the WhatsApp webhook.

Replaces the previous httpx-based client that POSTed to {APP_URL}/run and
{APP_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}. Public
signatures are preserved so callers in messages.py don't need to change.
"""
import logging
import os
from functools import lru_cache
from typing import Any

import vertexai
from google.api_core import exceptions as gax
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
    """Resolve the reasoningEngine resource name from Secret Manager and cache the client.

    `app_name` is the existing aa/pp key from app_config (e.g. config.aa_app_name).
    """
    _init()
    short = "aa" if "aa" in app_name.lower() else "pp"
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    secret_id = f"engine-{short}-resource-name"
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    sm = secretmanager.SecretManagerServiceClient()
    resource_name = sm.access_secret_version(request={"name": name}).payload.data.decode()
    return agent_engines.get(resource_name)


async def create_agent_session(
    user_id: str, app_name: str, session_id: str
) -> dict[str, Any]:
    """Get-or-create a session with a deterministic id (session_id == wa_id)."""
    engine = get_engine(app_name)
    try:
        return await engine.async_create_session(
            user_id=user_id, session_id=session_id
        )
    except gax.AlreadyExists:
        logging.info(
            "Session %s already exists for user %s on %s",
            session_id, user_id, app_name,
        )
        return await engine.async_get_session(
            user_id=user_id, session_id=session_id
        )


async def send_to_agent(
    app_name: str, user_id: str, session_id: str, message: str
) -> dict[str, Any]:
    """Stream a query to Agent Runtime, returning the concatenated assistant text."""
    engine = get_engine(app_name)
    logging.info(f"Sending message to agent {app_name} for user {user_id}")
    out: list[str] = []
    raw_events: list[dict] = []
    async for event in engine.async_stream_query(
        user_id=user_id, session_id=session_id, message=message
    ):
        raw_events.append(event)
        # event["content"]["parts"][i] is either {"text": ...} (assistant token)
        # or {"function_call": ...} / {"function_response": ...} (tool events).
        # The `if text:` guard naturally skips tool-call parts.
        content = event.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if text:
                out.append(text)
    response_text = "".join(out).strip()
    if not response_text:
        logging.warning(
            f"Empty response from agent {app_name}: {len(raw_events)} events"
        )
        return {
            "response": "Error: Could not extract text from agent response.",
            "raw_response": raw_events,
        }
    return {"response": response_text, "raw_response": raw_events}
```

- [ ] **Step 5: Run the tests — should pass**

Run: `cd webhook-application && uv run --extra test pytest tests/external_services/test_agent_client.py -v`
Expected: 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add webhook-application/whatsapp_webhook/external_services/agent_client.py \
        webhook-application/tests/external_services/__init__.py \
        webhook-application/tests/external_services/test_agent_client.py
git commit -m "feat(webhook): rewrite agent_client to use Vertex AI Agent Runtime SDK"
```

### Task 13: Drop `agent_url` / `agent_http_timeout` from `app_config.py`

**Files:**
- Modify: `webhook-application/whatsapp_webhook/utils/app_config.py`

- [ ] **Step 1: Read the file to locate the fields**

Run: `grep -n 'agent_url\|agent_http_timeout\|APP_URL\|AGENT_HTTP_TIMEOUT' webhook-application/whatsapp_webhook/utils/app_config.py`

- [ ] **Step 2: Remove both fields and their env-var lookups**

Edit `webhook-application/whatsapp_webhook/utils/app_config.py`. Remove:
- the `agent_url: str` and `agent_http_timeout: ...` fields from the config dataclass/model
- the `os.getenv("APP_URL")` and `os.getenv("AGENT_HTTP_TIMEOUT")` lines

Leave every other field untouched.

- [ ] **Step 3: Grep for residual references**

Run: `grep -rn 'config\.agent_url\|config\.agent_http_timeout' webhook-application/whatsapp_webhook 2>/dev/null`
Expected: zero results (after Task 12 the only callers were inside `agent_client.py`, which we rewrote).

- [ ] **Step 4: Run the full webhook test suite to confirm no regressions**

Run: `cd webhook-application && uv run --extra test pytest tests/ -v`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add webhook-application/whatsapp_webhook/utils/app_config.py
git commit -m "refactor(webhook): drop agent_url and agent_http_timeout from app_config"
```

### Task 14: Update `webhook-application/pyproject.toml`

**Files:**
- Modify: `webhook-application/pyproject.toml`

- [ ] **Step 1: Add deps**

Edit `webhook-application/pyproject.toml` — extend the `dependencies` list:
```toml
    "google-cloud-aiplatform[agent_engines]>=1.135.0",
    "google-cloud-secret-manager>=2.20.0",
```

If Task 7 step 2 showed that `httpx` is still used by `whatsapp_client.py`, leave `httpx` in the list. Otherwise, remove `"httpx>=0.25.0,<0.30.0",` from `dependencies` (it stays in the `test` extra for HTTP client testing).

- [ ] **Step 2: Lock + sync**

Run:
```bash
cd webhook-application
uv lock
uv sync --extra test
```

- [ ] **Step 3: Run the webhook test suite end-to-end**

Run: `cd webhook-application && uv run --extra test pytest tests/ -v`
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add webhook-application/pyproject.toml webhook-application/uv.lock
git commit -m "chore(webhook): add Vertex AI Agent Engine + Secret Manager deps"
```

### Task 15: Add the `deploy-agents.yml` workflow

**Files:**
- Create: `.github/workflows/deploy-agents.yml`

- [ ] **Step 1: Write the workflow file**

Use Write — content from spec section 6.1:

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
            secret_id="$(echo $k | tr A-Z_ a-z- )"
            v=$(gcloud secrets versions access latest --secret="$secret_id")
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

- [ ] **Step 2: Run actionlint (if installed) or `yamllint`**

Run: `which actionlint && actionlint .github/workflows/deploy-agents.yml || yamllint .github/workflows/deploy-agents.yml`
Expected: no errors. If neither linter is installed, skip — CI will validate on push.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/deploy-agents.yml
git commit -m "ci: add deploy-agents workflow for Agent Runtime"
```

### Task 16: Open the Phase 2 PR (but do NOT merge yet — Phase 3 deploys from this branch)

**Files:** none.

- [ ] **Step 1: Push the branch**

Run: `git push -u origin feature/agent-runtime-migration-phase2`

- [ ] **Step 2: Open a DRAFT PR**

Run:
```bash
gh pr create --draft --title "feat(agent-runtime): code changes for dev cutover" --body "$(cat <<'EOF'
## Summary
- Adds per-agent AdkApp shims (agent_engine_app.py) wrapping each root_agent
- Adds agents/deploy.py — idempotent create-or-update for both reasoningEngines, writes resource names to Secret Manager
- Rewrites webhook external_services/agent_client.py to use the Vertex AI SDK while preserving the public function signatures
- Drops agent_url / agent_http_timeout from webhook app_config
- Adds .github/workflows/deploy-agents.yml — manual + on-push deployment
- Adds unit tests for the new pure helpers and the rewritten async client

The old Cloud Run agent service remains in place; the webhook will keep working against it until Task 19 redeploys the webhook image.

## Test plan
- [x] agents/tests/test_agent_engine_app.py — 4 PASS
- [x] agents/tests/test_deploy.py — 4 PASS
- [x] webhook-application/tests/external_services/test_agent_client.py — 4 PASS
- [x] webhook-application full suite — green
- [ ] Phase 3 — run deploy-agents workflow against npe, smoke-test, redeploy webhook
- [ ] Phase 4 — same against prd

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Keep the PR as a draft until Phase 3 smoke tests pass.

---

## Phase 3 — Dev cutover

### Task 17: Trigger the deploy-agents workflow against npe

**Files:** none (CI run).

- [ ] **Step 1: Run the workflow via gh CLI**

Run: `gh workflow run deploy-agents.yml --ref feature/agent-runtime-migration-phase2 -f environment=npe`
Expected: a new workflow run is queued. The self-hosted runner picks it up.

- [ ] **Step 2: Watch the run**

Run: `gh run watch $(gh run list --workflow=deploy-agents.yml --limit=1 --json databaseId -q '.[0].databaseId')`
Expected: workflow completes successfully. The final step prints two lines like:
```
agent_aa: projects/.../locations/us-central1/reasoningEngines/<AA_ID>
agent_pp: projects/.../locations/us-central1/reasoningEngines/<PP_ID>
```

- [ ] **Step 3: Verify Secret Manager versions were written**

Run:
```bash
gcloud secrets versions access latest --project=agro-extension-digital-npe --secret=engine-aa-resource-name
gcloud secrets versions access latest --project=agro-extension-digital-npe --secret=engine-pp-resource-name
```
Expected: each prints a `projects/.../reasoningEngines/<id>` resource name.

### Task 18: Smoke-test each engine directly

**Files:** none.

- [ ] **Step 1: Set ADC to the dev project**

Run: `gcloud config set project agro-extension-digital-npe`

- [ ] **Step 2: Smoke-test AA**

Run:
```bash
RN=$(gcloud secrets versions access latest --secret=engine-aa-resource-name)
python - <<PY
import os
import vertexai
from vertexai import agent_engines
vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe"),
              location="us-central1")
eng = agent_engines.get("$RN")
s = eng.create_session(user_id="smoke-test-aa")
got_text = False
for ev in eng.stream_query(user_id="smoke-test-aa", session_id=s["id"],
                            message="Hola, ¿qué cultivos manejas?"):
    for part in (ev.get("content") or {}).get("parts") or []:
        if "text" in part and part["text"].strip():
            got_text = True
print("OK" if got_text else "EMPTY")
PY
```
Expected: `OK`. If `EMPTY`, run `gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"' --limit=50` and inspect.

- [ ] **Step 3: Smoke-test PP analogously**

Repeat Step 2 with `engine-pp-resource-name`, `user_id="smoke-test-pp"`, message="Ayúdame con la planificación de producción de ciruelas.".

### Task 19: Redeploy the webhook to dev with the new SDK client

**Files:** none (CI).

- [ ] **Step 1: Push a commit (if needed) to trigger the webhook image build**

If `webhook-application/**` is unchanged on this branch and the `build-and-push.yml` workflow only triggers on changes there, push an empty commit:
```bash
git commit --allow-empty -m "ci: trigger webhook image rebuild for Agent Runtime cutover"
git push
```

- [ ] **Step 2: Watch the build-and-push run**

Run: `gh run watch $(gh run list --workflow=build-and-push.yml --limit=1 --json databaseId -q '.[0].databaseId')`
Expected: webhook image built and pushed to GAR with the new commit SHA tag.

- [ ] **Step 3: Update the Cloud Run webhook image to the new tag (dev)**

Run:
```bash
NEW_SHA=$(git rev-parse --short HEAD)
gcloud run deploy webhook-app \
  --project=agro-extension-digital-npe \
  --region=us-central1 \
  --image=us-central1-docker.pkg.dev/agro-extension-digital-npe/agents/agent-webhook-app:${NEW_SHA}
```
Expected: revision deployed; service URL unchanged.

- [ ] **Step 4: Verify the webhook can call Agent Runtime**

Run (from your machine or the runner):
```bash
WEBHOOK_URL=$(gcloud run services describe webhook-app --project=agro-extension-digital-npe --region=us-central1 --format='value(status.url)')
curl -s -o /dev/null -w "%{http_code}\n" "$WEBHOOK_URL/healthz" || curl -s -o /dev/null -w "%{http_code}\n" "$WEBHOOK_URL/"
```
Expected: a 2xx from the webhook (it's still running; just confirming it boots with the new image).

### Task 20: End-to-end WhatsApp test (dev)

**Files:** none.

- [ ] **Step 1: Send a test WhatsApp message via the dev test number**

The user must do this manually from a real WhatsApp client. The test number's configuration is in Meta's developer console (out of band).

- [ ] **Step 2: Watch the webhook logs**

Run: `gcloud logging tail 'resource.type="cloud_run_revision" AND resource.labels.service_name="webhook-app"' --project=agro-extension-digital-npe`
Expected: log lines showing the incoming message, the call to `send_to_agent`, and the response back to WhatsApp. No `httpx.HTTPError`. No `ValueError: Agent URL is not configured`.

- [ ] **Step 3: Watch the engine logs**

Run: `gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"' --project=agro-extension-digital-npe --limit=50 --format='value(timestamp,severity,textPayload)'`
Expected: trace entries for the message turn. If empty, double-check the telemetry env vars on the engine (see spec section 7.1).

- [ ] **Step 4: Confirm the WhatsApp client received an intelligible reply**

The user must confirm the reply on their WhatsApp client.

### Task 21: Soak in dev (24–48h)

**Files:** none.

- [ ] **Step 1: Set a calendar reminder / wait**

Wait 24–48 hours. The webhook should be calling Agent Runtime continuously; the old Cloud Run agent service is idle but still deployed (fall-back lane).

- [ ] **Step 2: After soak, check error rate**

Run: `gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND severity>=ERROR' --project=agro-extension-digital-npe --limit=100`
Expected: zero or near-zero errors. If there's a pattern, fix before promoting to prd.

- [ ] **Step 3: Mark the Phase 2 PR ready for review**

Run: `gh pr ready` (in the same branch). Get review and merge into `main`.

---

## Phase 4 — Prod cutover

### Task 22: Trigger the deploy-agents workflow against prd

**Files:** none.

- [ ] **Step 1: Run the workflow**

Run: `gh workflow run deploy-agents.yml --ref main -f environment=prd`

- [ ] **Step 2: Watch + verify Secret Manager versions in prd**

Same as Task 17 step 2–3, against `agro-extension-digital-prd`.

### Task 23: Smoke-test prd engines

**Files:** none.

- [ ] **Step 1: Run the smoke test from Task 18 against prd**

Substitute `agro-extension-digital-prd`. Expected: `OK` for both AA and PP.

### Task 24: Redeploy the webhook to prd

**Files:** none.

- [ ] **Step 1: Promote the same image SHA used in dev**

Run:
```bash
SHA=$(gcloud run services describe webhook-app --project=agro-extension-digital-npe --region=us-central1 --format='value(spec.template.spec.containers[0].image)' | awk -F: '{print $NF}')
gcloud run deploy webhook-app \
  --project=agro-extension-digital-prd \
  --region=us-central1 \
  --image=us-central1-docker.pkg.dev/agro-extension-digital-prd/agents/agent-webhook-app:${SHA}
```
Expected: prd webhook now runs the SDK-based client. (If your build pipeline pushes to a separate prd GAR repo, adjust the image path.)

- [ ] **Step 2: Watch for 2 hours**

Run: `gcloud logging tail 'resource.type="cloud_run_revision" AND resource.labels.service_name="webhook-app" AND severity>=WARNING' --project=agro-extension-digital-prd`
Expected: no spike in warnings/errors. Use Cloud Monitoring's existing Cloud Run latency / error-rate dashboards if available.

---

## Phase 5 — Cleanup (only after prd is green for 7 days)

### Task 25: Create the cleanup branch

**Files:** none.

- [ ] **Step 1: Branch from main**

```bash
git checkout main
git pull
git checkout -b feature/agent-runtime-migration-cleanup
```

### Task 26: Remove old `agents/main.py`, `Dockerfile`, `deploy-agent.sh`

**Files:**
- Delete: `agents/main.py`, `agents/Dockerfile`, `agents/deploy-agent.sh`.

- [ ] **Step 1: Delete the three files**

Run:
```bash
git rm agents/main.py agents/Dockerfile agents/deploy-agent.sh
```

- [ ] **Step 2: Grep for any stale references**

Run: `grep -rln 'agents/main.py\|agents/Dockerfile\|deploy-agent.sh' . 2>/dev/null`
Expected: zero results (the workflow we edit in Task 27 may match — that's the next step).

- [ ] **Step 3: Commit**

```bash
git commit -m "chore(agents): remove Cloud Run host (main.py, Dockerfile, deploy-agent.sh)"
```

### Task 27: Remove the agents image build step from `build-and-push.yml`

**Files:**
- Modify: `.github/workflows/build-and-push.yml`

- [ ] **Step 1: Read the workflow and identify the agents build step**

Run: `grep -n 'agents\|GAR_REPO\b' .github/workflows/build-and-push.yml`

- [ ] **Step 2: Remove the "Build agents Docker image" + "Push agents Docker images" steps and the `GAR_REPO` env var**

Edit `.github/workflows/build-and-push.yml`:
- Delete the two steps named "Build agents Docker image" and "Push agents Docker images".
- Delete the `GAR_REPO: us-central1-docker.pkg.dev/...` line from the `env:` block (leave `GAR_REPO_WEBHOOK` and `GAR_REPO_FRONTEND`).

- [ ] **Step 3: Lint**

Run: `which actionlint && actionlint .github/workflows/build-and-push.yml || true`
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/build-and-push.yml
git commit -m "ci: remove agents image build/push from build-and-push (agents now deploy via deploy-agents.yml)"
```

### Task 28: Remove old Cloud Run + SA from Terraform

**Files:**
- Modify: `cicd/modules/backend/main.tf`
- Modify: `cicd/modules/backend/variables.tf`

- [ ] **Step 1: Delete the obsolete resources from `cicd/modules/backend/main.tf`**

Delete these resource blocks (verify each block's exact location by line number first):
- `google_service_account.agent_aa_app`
- `google_project_iam_member.agent_aa_sa_role`
- `google_project_iam_member.agent_aa_sa_role_discovery`
- `google_cloud_run_v2_service.cloud_run_name_agent_aa`
- `google_cloud_run_v2_service_iam_member.webhook_invokes_agent_aa`
- The `APP_URL` and `AGENT_HTTP_TIMEOUT` env entries on `google_cloud_run_v2_service.cloud_run_name_webhook`

Leave the `noauth_webhook` IAM binding, the webhook Cloud Run service, and everything we added in Phase 1.

- [ ] **Step 2: Remove now-unused variables from `variables.tf`**

If any of these variables are unused after Step 1, remove them:
- `cloud_run_name_agent_aa`
- `gar_image_location_agent_aa`
- `service_account_id_agent_aa`
- `service_account_display_name_agent_aa`
- `service_name` (only if not consumed elsewhere — grep first)
- `agent_http_timeout` (if defined)

Run: `grep -rn 'var\.cloud_run_name_agent_aa\|var\.gar_image_location_agent_aa\|var\.service_account_id_agent_aa\|var\.agent_http_timeout' cicd/`

For each variable that has NO matches, remove its declaration from `variables.tf` and its assignment in `cicd/stacks/dev/` and `cicd/stacks/prd/` `terragrunt.hcl` / `common.yaml`.

- [ ] **Step 3: `terraform fmt -recursive` + `terraform validate`**

Run: `cd cicd/modules/backend && terraform init -backend=false && terraform fmt -check -recursive && terraform validate`
Expected: clean.

- [ ] **Step 4: `terragrunt plan` against npe**

Run: `cd cicd/stacks/dev && terragrunt plan -no-color | tee /tmp/cleanup-dev-plan.txt`
Expected: plan shows ONLY destroys (and possibly an env update on the webhook service to drop `APP_URL`):
- destroy `google_cloud_run_v2_service.cloud_run_name_agent_aa`
- destroy `google_service_account.agent_aa_app`
- destroy 2 × `google_project_iam_member.agent_aa_sa_role*`
- destroy `google_cloud_run_v2_service_iam_member.webhook_invokes_agent_aa`
- update on `cloud_run_name_webhook` to remove the two env entries
- ZERO destroys of anything from Phase 1 (the new runtime SAs/bucket/secrets must remain).

If anything from Phase 1 appears in the destroy list, **STOP** — that's a bug.

- [ ] **Step 5: Apply to dev**

Run: `cd cicd/stacks/dev && terragrunt apply -auto-approve`

- [ ] **Step 6: Verify the old agent service is gone**

Run: `gcloud run services list --project=agro-extension-digital-npe --filter='metadata.name:agent-aa' --format='value(metadata.name)'`
Expected: empty.

- [ ] **Step 7: Repeat plan + apply for prd, with confirmation**

```bash
gcloud config set project agro-extension-digital-prd
cd cicd/stacks/prd && terragrunt plan
# Confirm with user, then:
cd cicd/stacks/prd && terragrunt apply -auto-approve
```

- [ ] **Step 8: Commit and push**

```bash
git add cicd/modules/backend/main.tf cicd/modules/backend/variables.tf cicd/stacks/
git commit -m "infra(agent-runtime): remove old Cloud Run agent service and its variables"
git push -u origin feature/agent-runtime-migration-cleanup
```

### Task 29: Open the cleanup PR

**Files:** none.

- [ ] **Step 1: Open the PR**

Run:
```bash
gh pr create --title "chore(agent-runtime): cleanup — remove old Cloud Run agent" --body "$(cat <<'EOF'
## Summary
- Deletes agents/main.py, agents/Dockerfile, agents/deploy-agent.sh (Cloud Run host retired)
- Removes the agents image build/push step from build-and-push.yml
- Removes google_cloud_run_v2_service.cloud_run_name_agent_aa, the old runtime SA, and the webhook → run.invoker binding
- Removes APP_URL and AGENT_HTTP_TIMEOUT env entries on the webhook Cloud Run service
- Retires now-unused Terraform variables (cloud_run_name_agent_aa, gar_image_location_agent_aa, service_account_id_agent_aa, etc.)

Applied to npe and prd; verified the old agent-aa Cloud Run service no longer exists. The new Agent Runtime resources from Phase 1 are unaffected.

## Test plan
- [x] terraform validate clean
- [x] terragrunt plan dev: only destroys + the webhook env update; no new additions; no destroys of Phase 1 resources
- [x] terragrunt apply dev succeeded
- [x] terragrunt plan prd: same shape as dev
- [x] terragrunt apply prd succeeded
- [x] Webhook on prd still serving traffic (calls Agent Runtime; no calls to the deleted Cloud Run service)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Rollback playbook

**Until the cleanup PR (Task 29) merges:** the old Cloud Run agent service is still running. Rollback in any env = redeploy the **previous** webhook revision (which still uses the httpx-based client and hits `APP_URL`).

```bash
# List recent webhook revisions
gcloud run revisions list --project=<env-project> --service=webhook-app --region=us-central1 --limit=10
# Roll back traffic to the previous revision
gcloud run services update-traffic webhook-app --project=<env-project> --region=us-central1 --to-revisions=<previous-revision>=100
```

The Agent Runtime engines stay deployed but receive no traffic; cost is near-zero at `min_instances=0`.

**After the cleanup PR merges:** rollback requires reverting the cleanup PR and re-applying Terragrunt. Inside one normal release cycle.

---

## Self-Review

**1. Spec coverage check:**

| Spec section | Implementing tasks |
|---|---|
| §2 Target architecture | Task 8, 9, 11, 12 (code shape) + Task 1 (infra) |
| §3 IAM | Task 1 |
| §4.1 Per-agent shims | Tasks 8, 9 |
| §4.1 `agents/deploy.py` | Task 11 |
| §4.2 Modified files (`pyproject.toml`, `agent_client.py`, `app_config.py`) | Tasks 10, 12, 13, 14 |
| §4.3 Deleted at cutover | Tasks 26, 27 |
| §5 IaC delta — additions | Task 1 |
| §5 IaC delta — removals | Task 28 |
| §6 CI/CD — `deploy-agents.yml` | Task 15 |
| §6 CI/CD — `build-and-push.yml` edits | Task 27 |
| §7 Observability | Telemetry env vars wired in Task 11 (`TELEMETRY_ENV`) |
| §7.2 Smoke tests | Tasks 18, 20, 23 |
| §8.1 Rollout sequence | Phases 1 → 5 |
| §8.2 Rollback | Rollback playbook above |

All spec sections have implementing tasks. ✓

**2. Placeholder scan:** searched for "TBD", "TODO", "implement later", "fill in details", "appropriate", "similar to". One legitimate "TBD" remains in the File Map referring to Task 7's runtime check on `httpx` callers — kept because it's a real branch (resolved in-task) not an unfilled stub. No other placeholders.

**3. Type consistency:** `send_to_agent` / `create_agent_session` keep their existing public signatures (`app_name, user_id, session_id, message`) across spec, plan, tests, and implementation. `deploy.py` exposes `env_vars_for(key)` / `find_existing(display_name)` / `write_secret(project, secret_id, value)` / `deploy_one(key, cfg, project, sa)` consistently. `AGENTS` dict keys (`"agent_aa"`, `"agent_pp"`) and Secret Manager `secret_id`s (`engine-aa-resource-name`, `engine-pp-resource-name`) match between `deploy.py`, the workflow, the rewritten webhook client, and the Terraform definitions.
