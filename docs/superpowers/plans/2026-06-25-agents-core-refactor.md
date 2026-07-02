# Agents `core/` Refactor + WhatsApp Sanitizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collapse the duplicated `agent_aa_app` / `agent_pp_app` code into one shared `core/` package, replace the LangGraph BigQuery sub-agent with four native ADK function tools, and move WhatsApp formatting out of the prompts into a deterministic post-processing sanitizer in the webhook — all on **ADK 1.35** (no version bump).

**Architecture:** A new `agents/core/` package holds the shared model wrapper, the four BigQuery tools, the prompt composition, and a single `build_app(name, display_name, main_datastore_env)` factory that returns an `AdkApp`. The two per-agent packages shrink to a one-line shim that calls `build_app`. The BigQuery sub-agent becomes an ordinary `LlmAgent` with four function tools (`list_tables`, `get_schema`, `check_query`, `run_query`), deleting the vendored `LangGraphAgent`, the `asyncio.Lock`, the lazy graph factory, and the `SQLDatabaseToolkit` wiring. The webhook's `send_to_agent` gains a pure-regex `_normalize_whatsapp_markdown` step so the model no longer has to enforce formatting.

**Tech Stack:** Python 3.12, `google-adk>=1.35.0,<2.0.0` (unchanged), `google-cloud-bigquery`, `vertexai.agent_engines`, FastAPI (webhook), `uv`, `pytest` + `pytest-asyncio`.

**Reference:** GitHub Discussion #44 (the proposal) and RodrigoVasquez's review of it. This plan is **PR-A** of the split Rodrigo recommended.

---

## Sequencing context (read first)

This is the **first of three follow-up PRs**, all sequenced *after* PR #43 (the Agent Runtime migration) has merged and soaked in prd for 7 days:

```
PR #43 (migration)        → npe → 24–48h dev soak → prd → 7d prd soak → MERGE
                                                                          │
                                                                          ▼
PR-A  THIS PLAN: core/ refactor + sanitizer (ADK 1.35)  → npe 24h → prd → MERGE
                                                                          │
                                                                          ▼
PR-B  ADK 2.x bump ONLY                                 → npe 48h → prd → MERGE
                                                                          │
                                                                          ▼
PR-C  planner + RAG quality (eval harness first/parallel)
```

**Do not start this plan until PR #43 is merged to `main`.** This branch is cut from `main`, not stacked on `feature/agent-runtime-migration`. Stacking would invalidate the migration soak (Rodrigo R1).

### Deviations from Discussion #44 (deliberate, Rodrigo-aligned)

| #44 proposed | This plan does | Why |
|---|---|---|
| Rename packages to `adecuacion_agroindustrial` / `produccion_primaria` | **Keep `agent_aa_app` / `agent_pp_app` dir names** | Smaller blast radius: `deploy.py` keys, secret IDs (`engine-aa-…`), runtime SA emails, and the webhook router stay untouched; keeps the `engine-{aa,pp}-resource-name` secret-keyed idempotency (#43) stable. Rename can be a trivial later PR. |
| BQ tools raise, then harden in a later commit | **Tools return `{ok, error, …}` from the start** | DRY — no reason to build raising tools then rewrite them in the same PR. |
| `BQ_MAX_BYTES` default 100 MB | **Default 1 GB** (`BQ_MAX_BYTES`, per-engine env override) | Rodrigo Q4: 100 MB is a foot-gun for legitimate analytic queries; keep it as a safety net, not a target. |
| Drop WhatsApp formatting from prompts entirely | **Keep one belt-and-suspenders plain-text line in the shared prompt** AND a deterministic sanitizer | Rodrigo V5: sanitizer can't cover every Markdown construct; a one-line prompt hint is cheap insurance. |
| Planner, RAG citations, Memory Bank curation | **Out of scope — deferred to PR-C** | Rodrigo R3: keep merge boundaries bisectable. |
| ADK 2.x bump | **Out of scope — deferred to PR-B** | Rodrigo R2/R3. |

### Migration hazard this plan must handle (neither thread flagged it)

`deploy.py:find_existing()` matches an existing engine by `display_name`. This plan corrects PP's display name from `"Planificación de Producción"` to `"Producción Primaria"` (matches `cicd/stacks/dev/env.yaml:38` → `produccion-primaria`). Consequence: the first PR-A deploy will **not** match the existing PP engine and will **create a new PP engine** (new resource name → `write_secret` rewrites `engine-pp-resource-name` → the webhook's `get_engine` follows the new resource name on its next call). This is a clean cutover, but it leaves the **old PP engine orphaned**. Task 14 deletes it after soak. AA's display name is unchanged, so AA updates in place. This behavior is documented in Task 11 and gated in Task 13.

### Update (2026-07-01) — validated by the #43 live `npe` deploy

Since this plan was written, **#43 replaced `find_existing()`**: `deploy.py` now keys idempotency off the **stored engine resource name** (the `engine-{aa,pp}-resource-name` Secret Manager value), not `display_name`. A full deploy + direct-query test in `npe` confirmed the real behavior and surfaced three fixes PR-A must carry forward (each is landed in #43; do not regress them):

- **The PP rename no longer orphans an engine.** With resource-name keying, changing `display_name` reads the stored resource name, `agent_engines.get()`s it, and calls `.update(display_name=…)` → the PP engine renames **in place** (verified live: the redeploy updated PP's display name with no new engine created). **The `find_existing`/`display_name` hazard above is superseded** — Task 14's orphan cleanup now only applies to engines left over from *before* #43, and Task 13's gating for a "new PP engine" is no longer triggered by the rename alone.
- **`deploy.py` must treat a DISABLED engine-name secret version as "no engine".** `access_secret_version` raises `FailedPrecondition` (not `NotFound`) when the latest version is disabled/destroyed — a documented rollback step. `read_secret`/`write_secret` must catch **both**, or the deploy crashes mid-run. (Fixed in #43; PR-A's `deploy.py` edits — Task 6 — must preserve it.)
- **Never put `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` in the engine `env_vars`.** Agent Engine reserves those names and rejects `create()` with `"Environment variable name '…' is reserved"`. The runtime injects them; the code reads them via `os.environ`. (Fixed in #43 by dropping them from `env_vars_for`; PR-A must not reintroduce.)
- **`core/agent.py:build_app` must pass the FULL datastore resource name to `VertexAiSearchTool`**, not the bare id — `projects/{project}/locations/global/collections/default_collection/dataStores/{id}`. The bare id makes every RAG query fail server-side with `"Invalid Vertex AI datastore resource name"` (root-caused via Cloud Logging in the #43 live test; all five dev datastores are in the `global` location). **This is the highest-risk carry-forward** because PR-A rewrites the search-tool construction (Task 4) — build the full path there, with a unit test asserting the format.

---

## File Map

**Created:**
- `agents/core/__init__.py` — empty package marker.
- `agents/core/llm_global.py` — single `GlobalGemini` + `GEMINI_LOCATION` (was duplicated ×2).
- `agents/core/bq_tools.py` — four native ADK function tools over BigQuery.
- `agents/core/prompts.py` — plain-Python prompt composition helpers.
- `agents/core/prompts/shared/whatsapp_plain.md` — one-line plain-text hint (belt-and-suspenders).
- `agents/core/prompts/shared/bq_workflow.md` — the four-tool workflow guidance, shared.
- `agents/core/prompts/agent_aa/root.md`, `rag.md`, `rag_description.md`, `bq.md`, `bq_description.md` — relocated AA prompts (root.md with the verbose Markdown block removed).
- `agents/core/prompts/agent_pp/root.md`, `rag.md`, `rag_description.md`, `bq.md`, `bq_description.md` — relocated PP prompts.
- `agents/core/agent.py` — `build_app(name, display_name, main_datastore_env) -> AdkApp`.
- `agents/tests/test_bq_tools.py`, `agents/tests/test_core_agent.py`.
- `webhook-application/whatsapp_webhook/external_services/whatsapp_format.py` — the sanitizer.
- `webhook-application/tests/external_services/test_whatsapp_format.py`.

**Modified:**
- `agents/agent_aa_app/agent_engine_app.py` — becomes a 3-line shim calling `build_app`.
- `agents/agent_pp_app/agent_engine_app.py` — same.
- `agents/deploy.py` — `REQUIREMENTS` (drop LangChain/LangGraph, add `google-cloud-bigquery`); `extra_packages` add `"core"`; PP `display_name` → `"Producción Primaria"`.
- `agents/pyproject.toml` — drop `langchain_community`, `langchain_google_vertexai`, `langgraph`, `sqlalchemy-bigquery`; add `google-cloud-bigquery>=3.25.0`.
- `agents/tests/conftest.py` — drop the `SQLDatabase.from_uri` stub.
- `agents/tests/test_agent_engine_app.py` — update assertions for the new shim shape.
- `webhook-application/whatsapp_webhook/external_services/agent_client.py` — call the sanitizer on `response_text` before returning.

**Deleted:**
- `agents/agent_aa_app/agent.py`, `agents/agent_pp_app/agent.py`
- `agents/agent_aa_app/tools.py`, `agents/agent_pp_app/tools.py`
- `agents/agent_aa_app/llm_global.py`, `agents/agent_pp_app/llm_global.py`
- `agents/agent_aa_app/prompts.py`, `agents/agent_pp_app/prompts.py`
- `agents/agent_aa_app/prompts/` (tree), `agents/agent_pp_app/prompts/` (tree)
- `agents/agent_aa_app/utils/langgraph_agent.py`, `agents/agent_pp_app/utils/langgraph_agent.py`
- `agents/utils/langgraph_agent.py` (top-level orphan)

---

## Phase 0 — Branch

### Task 0: Cut the PR-A branch from up-to-date `main`

**Files:** none (git only).

- [ ] **Step 1: Confirm PR #43 is merged and `main` is current**

Run: `git checkout main && git pull && git log -1 --oneline`
Expected: the tip includes the PR #43 merge. If PR #43 is not merged yet, **stop** — this plan cannot start.

- [ ] **Step 2: Create the branch**

Run: `git checkout -b feature/agents-core-refactor`
Expected: switched to a new branch.

---

## Phase 1 — Build the `core/` package

### Task 1: Create the `core/` skeleton and move `GlobalGemini`

**Files:**
- Create: `agents/core/__init__.py`, `agents/core/llm_global.py`

- [ ] **Step 1: Create the package marker**

Use Write to create `agents/core/__init__.py` with content `""`.

- [ ] **Step 2: Create `agents/core/llm_global.py`**

Use Write (this is the AA copy verbatim — it is the canonical one; the PP copy was a comment-only stub):
```python
"""Gemini variant that routes model calls to location="global".

Gemini 3.x preview models (gemini-3.5-flash, gemini-3.1-flash-lite, ...) are
served only from the Vertex AI `global` location as of 2026-06. The Agent
Runtime engine itself must stay regional (Agent Engine resources are not
available in `global`), but the LLM client inside the engine can target
`global` for model calls. BigQuery + Vertex AI Search clients keep using
the engine's regional location.

This follows ADK's documented override pattern (see google.adk.models.Gemini
docstring).
"""
import os

from google import genai
from google.adk.models import Gemini

GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")


class GlobalGemini(Gemini):
    @property
    def api_client(self) -> genai.Client:
        # NOTE: plain @property (not @cached_property): the AdkApp gets
        # deepcopy'd at engine-create time, and a cached genai.Client holds
        # a module reference that fails to pickle. ADK's own Gemini caches
        # the client; we trade a per-call client init for picklability.
        return genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=GEMINI_LOCATION,
        )
```

> **Do NOT delete `llm_global.py` in any later PR on the assumption that a `Gemini.location` field replaces it.** It exists for two reasons: global-location routing AND picklability of `api_client`. A `location` field would not fix the deepcopy/pickle issue (Rodrigo V2).

- [ ] **Step 3: Commit**

```bash
git add agents/core/__init__.py agents/core/llm_global.py
git commit -m "refactor(agents): add core/ package with shared GlobalGemini"
```

### Task 2: Implement `core/bq_tools.py` — four native BigQuery tools (TDD)

**Files:**
- Create: `agents/core/bq_tools.py`, `agents/tests/test_bq_tools.py`

The four tools replace the entire LangGraph/LangChain SQL stack. Each returns a dict with `ok: bool` and never raises into the model. `list_tables`/`get_schema` are `@cache`d (process-lifetime; redeploy is the flush). `check_query` is a free BigQuery dry-run. `run_query` refuses non-`SELECT`, refuses scans over `BQ_MAX_BYTES` (default 1 GB), and truncates to `max_rows`.

- [ ] **Step 1: Write the failing tests**

Use Write to create `agents/tests/test_bq_tools.py`:
```python
"""Unit tests for core.bq_tools. The BigQuery client is mocked — no GCP creds."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _clear_caches():
    from core import bq_tools
    bq_tools.list_tables.cache_clear()
    bq_tools.get_schema.cache_clear()
    yield


def _fake_client():
    """A MagicMock standing in for bigquery.Client."""
    return MagicMock()


def test_list_tables_returns_table_ids():
    from core import bq_tools
    client = _fake_client()
    t1, t2 = MagicMock(), MagicMock()
    t1.table_id, t2.table_id = "estandar_aa", "otra_tabla"
    client.list_tables.return_value = [t1, t2]
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.list_tables()
    assert out == {"ok": True, "error": None, "tables": ["estandar_aa", "otra_tabla"]}


def test_list_tables_empty_dataset():
    from core import bq_tools
    client = _fake_client()
    client.list_tables.return_value = []
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.list_tables()
    assert out == {"ok": True, "error": None, "tables": []}


def test_get_schema_formats_fields():
    from core import bq_tools
    client = _fake_client()
    f1, f2 = MagicMock(), MagicMock()
    f1.name, f1.field_type, f1.description = "codigo", "STRING", "código de acción"
    f2.name, f2.field_type, f2.description = "puntos", "INTEGER", ""
    client.get_table.return_value = MagicMock(schema=[f1, f2])
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.get_schema("estandar_aa")
    assert out["ok"] is True
    assert "codigo STRING — código de acción" in out["schema"]
    assert "puntos INTEGER" in out["schema"]


def test_check_query_refuses_non_select():
    from core import bq_tools
    out = bq_tools.check_query("DELETE FROM estandar_aa")
    assert out["ok"] is False
    assert "SELECT" in out["error"]


def test_check_query_dry_run_reports_bytes():
    from core import bq_tools
    client = _fake_client()
    client.query.return_value = MagicMock(total_bytes_processed=12345)
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.check_query("SELECT 1")
    assert out == {"ok": True, "error": None, "bytes_processed": 12345}


def test_run_query_refuses_non_select():
    from core import bq_tools
    out = bq_tools.run_query("UPDATE estandar_aa SET x = 1")
    assert out["ok"] is False
    assert "SELECT" in out["error"]


def test_run_query_refuses_over_byte_cap(monkeypatch):
    from core import bq_tools
    monkeypatch.setenv("BQ_MAX_BYTES", "1000")
    client = _fake_client()
    # dry-run estimate exceeds the cap
    client.query.return_value = MagicMock(total_bytes_processed=5000)
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.run_query("SELECT * FROM estandar_aa")
    assert out["ok"] is False
    assert "exceeds" in out["error"].lower()


def test_run_query_truncates_rows():
    from core import bq_tools
    client = _fake_client()
    dry = MagicMock(total_bytes_processed=10)          # under default cap
    rows = [{"codigo": f"A{i:03d}"} for i in range(250)]
    live = MagicMock()
    live.result.return_value = [MagicMock(items=lambda r=r: r.items()) for r in rows]
    # query() is called twice: once dry-run, once for real
    client.query.side_effect = [dry, live]
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.run_query("SELECT codigo FROM estandar_aa", max_rows=100)
    assert out["ok"] is True
    assert len(out["rows"]) == 100
    assert out["truncated"] is True
```

- [ ] **Step 2: Run — should fail with `ModuleNotFoundError: No module named 'core.bq_tools'`**

Run: `cd agents && uv run --group dev pytest tests/test_bq_tools.py -v`
Expected: collection/import error (module missing).

- [ ] **Step 3: Implement `agents/core/bq_tools.py`**

Use Write:
```python
"""Native ADK function tools over BigQuery — replaces the LangGraph SQL agent.

Each tool returns {"ok": bool, "error": str | None, ...} and never raises into
the model: the LlmAgent recovers via the error -> fix -> retry loop the prompt
teaches. `list_tables` / `get_schema` are @cache'd for process lifetime (schemas
rarely change; engine redeploy is the natural flush). `check_query` is a free
BigQuery dry-run guard. `run_query` refuses non-SELECT, refuses scans over
BQ_MAX_BYTES (default 1 GB), and truncates to max_rows.
"""
import functools
import os

from google.cloud import bigquery

# Hard caps — env-overridable per engine without code change.
BQ_MAX_BYTES = int(os.environ.get("BQ_MAX_BYTES", str(1024 * 1024 * 1024)))  # 1 GB
BQ_MAX_ROWS = int(os.environ.get("BQ_MAX_ROWS", "100"))
LIST_TIMEOUT = 10.0
SCHEMA_TIMEOUT = 10.0
CHECK_TIMEOUT = 30.0
RUN_TIMEOUT = 60.0


def _project() -> str:
    return os.environ["GOOGLE_CLOUD_PROJECT"]


def _dataset() -> str:
    return os.environ["BIGQUERY_DATASET"]


def _client() -> bigquery.Client:
    # Created per call (not cached): the AdkApp is deepcopy'd at engine-create
    # time and a cached client holds unpicklable module refs (same reason as
    # GlobalGemini.api_client).
    return bigquery.Client(project=_project())


def _is_select(sql: str) -> bool:
    head = sql.lstrip().lstrip("(").lstrip().upper()
    return head.startswith("SELECT") or head.startswith("WITH")


@functools.cache
def list_tables() -> dict:
    """List the table names available in the configured BigQuery dataset."""
    try:
        ref = f"{_project()}.{_dataset()}"
        tables = [t.table_id for t in _client().list_tables(ref, timeout=LIST_TIMEOUT)]
        return {"ok": True, "error": None, "tables": tables}
    except Exception as e:  # noqa: BLE001 — surface to the model, never crash
        return {"ok": False, "error": str(e), "tables": []}


@functools.cache
def get_schema(table: str) -> dict:
    """Return the column schema (name, type, description) for one table."""
    try:
        ref = f"{_project()}.{_dataset()}.{table}"
        meta = _client().get_table(ref, timeout=SCHEMA_TIMEOUT)
        lines = []
        for f in meta.schema:
            desc = f" — {f.description}" if f.description else ""
            lines.append(f"{f.name} {f.field_type}{desc}")
        return {"ok": True, "error": None, "schema": "\n".join(lines)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "schema": ""}


def check_query(sql: str) -> dict:
    """Dry-run a SELECT to validate syntax and estimate scanned bytes (free)."""
    if not _is_select(sql):
        return {"ok": False, "error": "Only SELECT/WITH queries are allowed.",
                "bytes_processed": 0}
    try:
        cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = _client().query(sql, job_config=cfg, timeout=CHECK_TIMEOUT)
        return {"ok": True, "error": None,
                "bytes_processed": job.total_bytes_processed}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "bytes_processed": 0}


def run_query(sql: str, max_rows: int = BQ_MAX_ROWS) -> dict:
    """Run a SELECT and return up to max_rows result rows as dicts."""
    if not _is_select(sql):
        return {"ok": False, "error": "Only SELECT/WITH queries are allowed.",
                "rows": [], "truncated": False}
    client = _client()
    try:
        dry = client.query(
            sql,
            job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False),
            timeout=CHECK_TIMEOUT,
        )
        if dry.total_bytes_processed and dry.total_bytes_processed > BQ_MAX_BYTES:
            return {
                "ok": False,
                "error": (
                    f"Query exceeds the {BQ_MAX_BYTES} byte scan cap "
                    f"({dry.total_bytes_processed} bytes). Add filters or a LIMIT."
                ),
                "rows": [], "truncated": False,
            }
        cfg = bigquery.QueryJobConfig(maximum_bytes_billed=BQ_MAX_BYTES)
        job = client.query(sql, job_config=cfg, timeout=RUN_TIMEOUT)
        rows, truncated = [], False
        for i, row in enumerate(job.result(timeout=RUN_TIMEOUT)):
            if i >= max_rows:
                truncated = True
                break
            rows.append(dict(row.items()))
        return {"ok": True, "error": None, "rows": rows, "truncated": truncated}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "rows": [], "truncated": False}
```

- [ ] **Step 4: Run the tests — should pass**

Run: `cd agents && uv run --group dev pytest tests/test_bq_tools.py -v`
Expected: 8 tests PASS. (Deps for `google-cloud-bigquery` land in Task 7; if the import fails here, jump to Task 7 step 1–3, then return.)

- [ ] **Step 5: Commit**

```bash
git add agents/core/bq_tools.py agents/tests/test_bq_tools.py
git commit -m "feat(agents): add core/bq_tools — 4 native BigQuery function tools"
```

### Task 3: Relocate prompts into `core/prompts/` and add composition

**Files:**
- Create: `agents/core/prompts.py` and the `agents/core/prompts/` tree.

- [ ] **Step 1: Create the shared prompt fragments**

Use Write to create `agents/core/prompts/shared/whatsapp_plain.md`:
```markdown
Responde en texto plano y conversacional, en español (Latinoamérica). NO uses
Markdown (nada de **negrita**, _cursiva_, encabezados #, tablas ni enlaces con
corchetes): el formato de WhatsApp se aplica automáticamente después. Escribe
los enlaces como URLs simples.
```

Use Write to create `agents/core/prompts/shared/bq_workflow.md`:
```markdown
## Cómo consultar BigQuery (flujo obligatorio de 4 herramientas)

1. `list_tables()` — descubre qué tablas existen. SIEMPRE empieza aquí.
2. `get_schema(table)` — revisa las columnas de la tabla relevante antes de escribir SQL.
3. Escribe una consulta `SELECT` (solo SELECT/WITH). Pide únicamente las columnas necesarias.
4. `check_query(sql)` — valida sintaxis y estima bytes (es gratis). Si `ok` es false, corrige y reintenta.
5. `run_query(sql)` — ejecuta. Devuelve filas (truncadas a un máximo). Si `ok` es false, lee el `error`, corrige y reintenta.

Cada herramienta devuelve `{ok, error, ...}` — nunca lanza excepción. Ante un
error, ajusta la consulta y vuelve a intentar; no inventes datos.
```

- [ ] **Step 2: Relocate the per-agent prompt files**

Move the existing per-agent prompt content into the new tree (content is copied, then the verbose Markdown-formatting block is removed from each root). Create these files with Write, copying the body from the listed source:

| New file | Source file | Change |
|---|---|---|
| `agents/core/prompts/agent_aa/root.md` | `agents/agent_aa_app/prompts/agent_aa/instruction.md` | **Delete the entire `## 📜 Tu Estilo de Respuesta: Siempre como en WhatsApp 📱` section** (the bold/italic/links/code Markdown rules). Leave everything else. |
| `agents/core/prompts/agent_aa/rag.md` | `agents/agent_aa_app/prompts/agent_aa_rag/instruction.md` | verbatim |
| `agents/core/prompts/agent_aa/rag_description.md` | `agents/agent_aa_app/prompts/agent_aa_rag/description.md` | verbatim |
| `agents/core/prompts/agent_aa/bq.md` | `agents/agent_aa_app/prompts/agent_aa_bq/instruction.md` | verbatim |
| `agents/core/prompts/agent_aa/bq_description.md` | `agents/agent_aa_app/prompts/agent_aa_bq/description.md` | verbatim |
| `agents/core/prompts/agent_pp/root.md` | `agents/agent_pp_app/prompts/agent_pp/instruction.md` | same deletion as AA root |
| `agents/core/prompts/agent_pp/rag.md` | `agents/agent_pp_app/prompts/agent_pp_rag/instruction.md` | verbatim |
| `agents/core/prompts/agent_pp/rag_description.md` | `agents/agent_pp_app/prompts/agent_pp_rag/description.md` | verbatim |
| `agents/core/prompts/agent_pp/bq.md` | `agents/agent_pp_app/prompts/agent_pp_bq/instruction.md` | verbatim |
| `agents/core/prompts/agent_pp/bq_description.md` | `agents/agent_pp_app/prompts/agent_pp_bq/description.md` | verbatim |

> The old `text2sql/instruction.md` prompt is **not** carried over — it instructed the LangChain SQL agent, which this PR deletes. The four-tool workflow in `bq_workflow.md` replaces it. This also fixes the latent PP bug where `agent_pp_app/prompts.py` read the AA text2sql path.

- [ ] **Step 3: Create `agents/core/prompts.py` (composition)**

Use Write:
```python
"""Plain-Python prompt composition. No Jinja, no template engine.

Prompts are resolved relative to this file so they work both locally (cwd =
agents/) and inside the deployed engine (where `core` is shipped via
extra_packages and cwd differs).
"""
import os

_HERE = os.path.dirname(__file__)
_PROMPTS = os.path.join(_HERE, "prompts")


def _read(*parts: str) -> str:
    with open(os.path.join(_PROMPTS, *parts), encoding="utf-8") as f:
        return f.read()


def _join(*chunks: str) -> str:
    return "\n\n".join(c.strip() for c in chunks if c and c.strip())


def root_instruction(agent: str) -> str:
    """Root supervisor prompt: domain role + shared plain-text rule."""
    return _join(_read(agent, "root.md"), _read("shared", "whatsapp_plain.md"))


def rag_instruction(agent: str) -> str:
    return _read(agent, "rag.md")


def rag_description(agent: str) -> str:
    return _read(agent, "rag_description.md")


def bq_instruction(agent: str) -> str:
    """BQ sub-agent prompt: domain/table specifics + shared 4-tool workflow."""
    return _join(_read(agent, "bq.md"), _read("shared", "bq_workflow.md"))


def bq_description(agent: str) -> str:
    return _read(agent, "bq_description.md")
```

- [ ] **Step 4: Commit**

```bash
git add agents/core/prompts.py agents/core/prompts/
git commit -m "refactor(agents): relocate prompts to core/, extract shared rules + bq workflow"
```

### Task 4: Implement `core/agent.py:build_app` (TDD)

**Files:**
- Create: `agents/core/agent.py`, `agents/tests/test_core_agent.py`

`build_app` constructs the RAG sub-agent (Vertex AI Search — but the datastore MUST be the full resource name via `_datastore`, not the bare id today's code passes; see the 2026-07-01 update above), the BQ sub-agent (now an ordinary `LlmAgent` with the four function tools — no more `LangGraphAgent`), the root supervisor, and wraps the root in an `AdkApp`. `main_datastore_env` is the per-agent datastore env var name (`DATASTORE_AA_ID` or `DATASTORE_PP_ID`); the guides/faq/chileprunes datastores are shared.

- [ ] **Step 1: Write the failing tests**

Use Write to create `agents/tests/test_core_agent.py`:
```python
"""Shape tests for core.agent.build_app — no network (env is seeded in conftest)."""
from vertexai.agent_engines import AdkApp


def test_build_app_returns_adkapp_with_named_root():
    from core.agent import build_app
    app = build_app(
        name="aa_agent",
        display_name="Adecuación Agroindustrial",
        main_datastore_env="DATASTORE_AA_ID",
    )
    assert isinstance(app, AdkApp)
    assert app.agent.name == "aa_agent"


def test_root_has_rag_and_bq_subagents():
    from core.agent import build_app
    app = build_app(
        name="pp_agent",
        display_name="Producción Primaria",
        main_datastore_env="DATASTORE_PP_ID",
    )
    tool_names = {t.agent.name for t in app.agent.tools}
    assert tool_names == {"pp_agent_rag", "pp_agent_bq"}


def test_bq_subagent_uses_four_function_tools():
    from core.agent import build_app
    app = build_app(
        name="aa_agent",
        display_name="Adecuación Agroindustrial",
        main_datastore_env="DATASTORE_AA_ID",
    )
    bq = next(t.agent for t in app.agent.tools if t.agent.name == "aa_agent_bq")
    fn_names = {t.func.__name__ for t in bq.tools}
    assert fn_names == {"list_tables", "get_schema", "check_query", "run_query"}


def test_datastore_builds_full_resource_name():
    # Regression guard for the #43 live-deploy bug: the bare id breaks all RAG.
    from core.agent import _datastore
    assert _datastore("0001-example_123") == (
        "projects/test-project/locations/global/collections/"
        "default_collection/dataStores/0001-example_123"
    )
```

- [ ] **Step 2: Run — should fail with `ModuleNotFoundError: No module named 'core.agent'`**

Run: `cd agents && uv run --group dev pytest tests/test_core_agent.py -v`
Expected: import error.

- [ ] **Step 3: Implement `agents/core/agent.py`**

Use Write:
```python
"""Single factory for both agents. build_app(...) returns a deploy-ready AdkApp.

The agent `name` prefix (e.g. "aa_agent") derives the sub-agent names so traces
stay readable. The main datastore env var name differs per agent; guides/faq/
chileprunes datastores are shared across both.
"""
import os

from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool, agent_tool
from vertexai.agent_engines import AdkApp

from core import bq_tools, prompts
from core.llm_global import GlobalGemini


def _prefix(name: str) -> str:
    # "aa_agent" -> "agent_aa" prompt key. Names are aa_agent / pp_agent.
    return "agent_" + name.split("_", 1)[0]


def _datastore(short_id: str) -> str:
    # VertexAiSearchTool needs the FULL datastore resource name, NOT the bare id.
    # Passing the bare id makes every RAG query fail server-side with
    # "Invalid Vertex AI datastore resource name" (root-caused via Cloud Logging
    # in the #43 npe live test; all datastores live in the `global` location).
    # GOOGLE_CLOUD_PROJECT is injected by Agent Engine at runtime.
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    return (
        f"projects/{project}/locations/global/collections/"
        f"default_collection/dataStores/{short_id}"
    )


def build_app(name: str, display_name: str, main_datastore_env: str) -> AdkApp:
    key = _prefix(name)

    rag = LlmAgent(
        name=f"{name}_rag",
        model=GlobalGemini(model="gemini-3.1-flash-lite"),
        instruction=prompts.rag_instruction(key),
        description=prompts.rag_description(key),
        tools=[
            VertexAiSearchTool(data_store_id=_datastore(os.environ[main_datastore_env])),
            VertexAiSearchTool(data_store_id=_datastore(os.environ["DATASTORE_GUIDES_ID"])),
            VertexAiSearchTool(data_store_id=_datastore(os.environ["DATASTORE_FAQ_ID"])),
            VertexAiSearchTool(data_store_id=_datastore(os.environ["DATASTORE_CHILEPRUNES_CL_ID"])),
        ],
    )

    bq = LlmAgent(
        name=f"{name}_bq",
        model=GlobalGemini(model="gemini-3.5-flash"),
        instruction=prompts.bq_instruction(key),
        description=prompts.bq_description(key),
        tools=[
            bq_tools.list_tables,
            bq_tools.get_schema,
            bq_tools.check_query,
            bq_tools.run_query,
        ],
    )

    root = LlmAgent(
        name=name,
        model=GlobalGemini(model="gemini-3.5-flash"),
        instruction=prompts.root_instruction(key),
        tools=[
            agent_tool.AgentTool(agent=rag),
            agent_tool.AgentTool(agent=bq),
        ],
    )
    return AdkApp(agent=root)
```

> If the test in Step 4 reports `t.func` does not exist, ADK wrapped the plain functions in a `FunctionTool` with a different attribute. Inspect one with `vars(bq.tools[0])` and adjust the assertion in `test_bq_subagent_uses_four_function_tools` to the real attribute (commonly `.func` or `.fn`). The implementation does not change — only the test's introspection.

- [ ] **Step 4: Run the tests — should pass**

Run: `cd agents && uv run --group dev pytest tests/test_core_agent.py -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/core/agent.py agents/tests/test_core_agent.py
git commit -m "feat(agents): add core.agent.build_app — shared factory, BQ as native tools"
```

---

## Phase 2 — Slim the per-agent packages and clean up

### Task 5: Reduce `agent_aa_app` / `agent_pp_app` to shims and delete dead code

**Files:**
- Modify: `agents/agent_aa_app/agent_engine_app.py`, `agents/agent_pp_app/agent_engine_app.py`
- Delete: per-agent `agent.py`, `tools.py`, `llm_global.py`, `prompts.py`, `prompts/` trees, `utils/langgraph_agent.py` (×2), and `agents/utils/langgraph_agent.py`.

- [ ] **Step 1: Rewrite the AA shim**

Use Write to replace `agents/agent_aa_app/agent_engine_app.py`:
```python
"""AdkApp shim for Adecuación Agroindustrial — all logic lives in core."""
from core.agent import build_app

app = build_app(
    name="aa_agent",
    display_name="Adecuación Agroindustrial",
    main_datastore_env="DATASTORE_AA_ID",
)
```

- [ ] **Step 2: Rewrite the PP shim**

Use Write to replace `agents/agent_pp_app/agent_engine_app.py`:
```python
"""AdkApp shim for Producción Primaria — all logic lives in core."""
from core.agent import build_app

app = build_app(
    name="pp_agent",
    display_name="Producción Primaria",
    main_datastore_env="DATASTORE_PP_ID",
)
```

- [ ] **Step 3: Delete the dead files**

Run:
```bash
cd agents
git rm agent_aa_app/agent.py agent_aa_app/tools.py agent_aa_app/llm_global.py agent_aa_app/prompts.py
git rm -r agent_aa_app/prompts agent_aa_app/utils
git rm agent_pp_app/agent.py agent_pp_app/tools.py agent_pp_app/llm_global.py agent_pp_app/prompts.py
git rm -r agent_pp_app/prompts agent_pp_app/utils
git rm -r utils
```
Expected: all listed paths removed. (`agents/utils/` held only the orphaned `langgraph_agent.py` plus its `__pycache__`; if `git rm -r utils` reports it is not tracked, `rm -rf utils` instead.)

- [ ] **Step 4: Confirm no remaining imports of deleted modules**

Run: `grep -rn "langgraph\|SQLDatabase\|text2sql_tools\|from agent_aa_app.agent\|from agent_pp_app.agent\|agent_aa_app.tools\|agent_pp_app.tools\|\.llm_global\|agent_aa_app.prompts\|agent_pp_app.prompts" agents --include="*.py" | grep -v "/.venv/"`
Expected: zero results. Any hit is a missed reference — fix before continuing.

- [ ] **Step 5: Commit**

```bash
git add -A agents/agent_aa_app agents/agent_pp_app
git commit -m "refactor(agents): slim per-agent packages to shims; delete LangGraph/SQLDatabaseToolkit"
```

### Task 6: Update `deploy.py`

**Files:**
- Modify: `agents/deploy.py`

- [ ] **Step 1: Trim `REQUIREMENTS`**

Edit `agents/deploy.py` — replace the `REQUIREMENTS` list with:
```python
REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]>=1.135.0",
    "google-adk>=1.35.0,<2.0.0",
    "google-cloud-bigquery>=3.25.0",
    "google-cloud-discoveryengine",
]
```
(Removed: `langchain-community`, `langchain-google-vertexai`, `langgraph`, `sqlalchemy-bigquery`, `google-cloud-bigquery-storage`.)

> **Pin these to the regenerated `uv.lock` versions (`==`), not `>=` ranges.** #43 pinned `REQUIREMENTS` for reproducible engine builds (Rodrigo's REQUIREMENTS-drift finding); shipping `>=` to the engine lets a new upstream release change what the deployed engine runs vs. what the tests ran against. After Task 7 regenerates the lock, copy the resolved versions here. Also do **not** touch `read_secret`/`write_secret` (DISABLED-version handling) or `env_vars_for` (must not ship the reserved `GOOGLE_CLOUD_PROJECT`) — both landed in #43; see the 2026-07-01 update.

- [ ] **Step 2: Ship `core` with every engine + fix the PP display name**

Edit `agents/deploy.py`:

In the `AGENTS` dict, change PP's `display_name`:
```python
        "display_name": "Producción Primaria",
```

In `deploy_one`, change the `extra_packages` line so `core` ships alongside the per-agent package:
```python
        extra_packages=[cfg["module_path"], "core"],
```

> Without `"core"` in `extra_packages`, every engine import fails **at runtime on the deployed engine** — local tests still pass because `core` is on the local path. Task 11's deployed smoke test is the only thing that catches this; do not skip it.

- [ ] **Step 3: Re-run the deploy unit tests**

Run: `cd agents && uv run --group dev pytest tests/test_deploy.py -v`
Expected: existing deploy tests still PASS. If a test asserts the old PP display name or the old `REQUIREMENTS`, update the expectation in `tests/test_deploy.py` to match, then re-run.

- [ ] **Step 4: Commit**

```bash
git add agents/deploy.py agents/tests/test_deploy.py
git commit -m "chore(agents): deploy.py — drop LangChain deps, ship core/, fix PP display name"
```

### Task 7: Update `pyproject.toml` and lockfile

**Files:**
- Modify: `agents/pyproject.toml`

- [ ] **Step 1: Edit dependencies**

Edit `agents/pyproject.toml` — set `dependencies` to:
```toml
dependencies = [
    "google-adk>=1.35.0,<2.0.0",
    "google-cloud-aiplatform[adk,agent_engines]>=1.135.0",
    "google-cloud-secret-manager>=2.20.0",
    "google-cloud-discoveryengine>=0.13.0",
    "google-cloud-bigquery>=3.25.0",
    "ipykernel",
]
```
(Removed: `langchain_community`, `langchain_google_vertexai`, `langgraph`, `sqlalchemy-bigquery`, `google-cloud-bigquery-storage`.)

- [ ] **Step 2: Lock + sync**

Run:
```bash
cd agents
uv lock
uv sync --group dev
```
Expected: the four LangChain/LangGraph trees disappear from `uv.lock`; `google-cloud-bigquery` is present; no resolution errors.

- [ ] **Step 3: Commit**

```bash
git add agents/pyproject.toml agents/uv.lock
git commit -m "chore(agents): drop LangChain/LangGraph deps, add google-cloud-bigquery"
```

### Task 8: Update test fixtures and run the full agents suite

**Files:**
- Modify: `agents/tests/conftest.py`, `agents/tests/test_agent_engine_app.py`

- [ ] **Step 1: Strip the `SQLDatabase` stub from conftest**

Use Write to replace `agents/tests/conftest.py`:
```python
"""Seed placeholder env vars before any agent module is imported.

The old SQLDatabase.from_uri stub is gone — the BigQuery tools in
core/bq_tools.py construct their client lazily (per call), so importing the
agent modules no longer makes a live BigQuery call.
"""
import os

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("BIGQUERY_DATASET", "test_dataset")
os.environ.setdefault("DATASTORE_AA_ID", "test-datastore-aa")
os.environ.setdefault("DATASTORE_PP_ID", "test-datastore-pp")
os.environ.setdefault("DATASTORE_GUIDES_ID", "test-datastore-guides")
os.environ.setdefault("DATASTORE_FAQ_ID", "test-datastore-faq")
os.environ.setdefault("DATASTORE_CHILEPRUNES_CL_ID", "test-datastore-chileprunes")
```

- [ ] **Step 2: Update the shim test**

The existing `tests/test_agent_engine_app.py` imports `from agent_aa_app.agent import root_agent`, which no longer exists. Use Write to replace it:
```python
"""The deploy script imports `app` from each shim — guard against drift."""
import importlib

from vertexai.agent_engines import AdkApp


def test_aa_shim_exposes_adkapp():
    mod = importlib.import_module("agent_aa_app.agent_engine_app")
    assert isinstance(mod.app, AdkApp)
    assert mod.app.agent.name == "aa_agent"


def test_pp_shim_exposes_adkapp():
    mod = importlib.import_module("agent_pp_app.agent_engine_app")
    assert isinstance(mod.app, AdkApp)
    assert mod.app.agent.name == "pp_agent"
```

- [ ] **Step 3: Run the entire agents test suite**

Run: `cd agents && uv run --group dev pytest -v`
Expected: every test passes — `test_bq_tools.py` (8), `test_core_agent.py` (3), `test_agent_engine_app.py` (2), `test_deploy.py` (existing).

- [ ] **Step 4: Local InMemoryRunner smoke (no GCP engine, but exercises real imports)**

Run:
```bash
cd agents && uv run python -c "
import importlib
for shim in ('agent_aa_app.agent_engine_app', 'agent_pp_app.agent_engine_app'):
    app = importlib.import_module(shim).app
    print(shim, '->', app.agent.name, 'tools:', [t.agent.name for t in app.agent.tools])
"
```
Expected: both shims import cleanly and print their root name + two sub-agents. This proves the `core` import graph is intact locally (it does **not** prove `extra_packages` is correct — Task 11 does that).

- [ ] **Step 5: Commit**

```bash
git add agents/tests/conftest.py agents/tests/test_agent_engine_app.py
git commit -m "test(agents): drop SQLDatabase stub, update shim tests for build_app"
```

---

## Phase 3 — WhatsApp sanitizer (webhook side)

### Task 9: Add `_normalize_whatsapp_markdown` (TDD) and wire it in

**Files:**
- Create: `webhook-application/whatsapp_webhook/external_services/whatsapp_format.py`, `webhook-application/tests/external_services/test_whatsapp_format.py`
- Modify: `webhook-application/whatsapp_webhook/external_services/agent_client.py`

WhatsApp uses `*bold*`, `_italic_`, `~strike~`, ` ```mono``` `. The model now emits plain text (per `whatsapp_plain.md`), but as belt-and-suspenders we deterministically down-convert any Markdown that slips through.

- [ ] **Step 1: Write the failing tests**

Use Write to create `webhook-application/tests/external_services/test_whatsapp_format.py`:
```python
"""Unit tests for the deterministic WhatsApp Markdown sanitizer."""
from whatsapp_webhook.external_services.whatsapp_format import (
    normalize_whatsapp_markdown as norm,
)


def test_bold_double_asterisk_to_single():
    assert norm("Esto es **importante** ya") == "Esto es *importante* ya"


def test_triple_underscore_italics_to_single():
    assert norm("muy ___sutil___ detalle") == "muy _sutil_ detalle"


def test_markdown_link_to_bare_url():
    assert norm("Mira [la guía](https://x.co/g) aquí") == "Mira https://x.co/g aquí"


def test_heading_hashes_stripped():
    assert norm("# Título\nTexto") == "Título\nTexto"
    assert norm("### Sub\nMás") == "Sub\nMás"


def test_code_fence_language_tag_stripped():
    assert norm("```sql\nSELECT 1\n```") == "```\nSELECT 1\n```"


def test_table_pipes_collapsed_to_text():
    assert norm("| a | b |\n| - | - |\n| 1 | 2 |") == "a b\n1 2"


def test_leading_bullet_dash_kept_as_dash():
    # WhatsApp renders "- " bullets fine; leave them, just normalize "* " to "- "
    assert norm("* uno\n* dos") == "- uno\n- dos"


def test_collapses_excess_blank_lines():
    assert norm("a\n\n\n\nb") == "a\n\nb"


def test_does_not_touch_bare_brackets():
    # PR-C will add [fuente: ...] citations — the link regex must NOT eat them.
    assert norm("dato [fuente: faq]") == "dato [fuente: faq]"


def test_plain_text_unchanged():
    assert norm("Hola 👋 ¿en qué ayudo?") == "Hola 👋 ¿en qué ayudo?"
```

- [ ] **Step 2: Run — should fail (module missing)**

Run: `cd webhook-application && uv run --extra test pytest tests/external_services/test_whatsapp_format.py -v`
Expected: import error.

- [ ] **Step 3: Implement the sanitizer**

Use Write to create `webhook-application/whatsapp_webhook/external_services/whatsapp_format.py`:
```python
"""Deterministic Markdown -> WhatsApp text normalizer (pure regex, no LLM).

The agent prompt already asks for plain text; this is belt-and-suspenders for
the ~5-10% of replies where Markdown leaks through. Order matters: links before
emphasis (so a URL's punctuation isn't treated as emphasis), emphasis before
whitespace collapse.

NOTE for PR-C: the markdown-link rule only matches the full `[text](url)` form,
so bare `[fuente: ...]` citation markers introduced later are left intact (see
test_does_not_touch_bare_brackets).
"""
import re

_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_CODE_FENCE_LANG = re.compile(r"```[^\S\n]*[A-Za-z0-9_+-]+[^\S\n]*\n")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+", re.MULTILINE)
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC3 = re.compile(r"___([^_]+)___")
_ITALIC2 = re.compile(r"__([^_]+)__")
_BULLET = re.compile(r"^(\s*)\*\s+", re.MULTILINE)
_TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$", re.MULTILINE)
_BLANKS = re.compile(r"\n{3,}")


def _detable(text: str) -> str:
    out = []
    for line in text.split("\n"):
        if _TABLE_SEP.match(line):
            continue  # drop the |---|---| separator row entirely
        if line.strip().startswith("|") or " | " in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append(" ".join(c for c in cells if c))
        else:
            out.append(line)
    return "\n".join(out)


def normalize_whatsapp_markdown(text: str) -> str:
    if not text:
        return text
    text = _MD_LINK.sub(r"\2", text)          # [t](url) -> url
    text = _CODE_FENCE_LANG.sub("```\n", text)  # ```sql\n -> ```\n
    text = _HEADING.sub("", text)             # strip leading #'s
    text = _BOLD.sub(r"*\1*", text)           # **b** -> *b*
    text = _ITALIC3.sub(r"_\1_", text)        # ___i___ -> _i_
    text = _ITALIC2.sub(r"_\1_", text)        # __i__ -> _i_
    text = _BULLET.sub(r"\1- ", text)         # "* item" -> "- item"
    text = _detable(text)                     # | a | b | -> a b
    text = _BLANKS.sub("\n\n", text)          # collapse 3+ blank lines
    return text.strip()
```

- [ ] **Step 4: Run the tests — should pass**

Run: `cd webhook-application && uv run --extra test pytest tests/external_services/test_whatsapp_format.py -v`
Expected: 10 tests PASS. (If `test_table_pipes_collapsed_to_text` is off by whitespace, adjust `_detable` join — the exact expected string in the test is the contract.)

- [ ] **Step 5: Wire the sanitizer into `send_to_agent`**

Edit `webhook-application/whatsapp_webhook/external_services/agent_client.py`.

Add the import near the other relative imports (after line 18, `from ..utils.logging import get_logger`):
```python
from .whatsapp_format import normalize_whatsapp_markdown
```

In `send_to_agent`, change the success-path response build. Replace:
```python
    response_text = "".join(out).strip()
    if not response_text:
```
with:
```python
    response_text = normalize_whatsapp_markdown("".join(out))
    if not response_text:
```
(Leave the empty-response and timeout branches unchanged — they return fixed Spanish error strings that need no normalization.)

- [ ] **Step 6: Run the webhook suite end-to-end**

Run: `cd webhook-application && uv run --extra test pytest tests/ -v`
Expected: all tests pass, including the existing `test_agent_client.py`. If a `send_to_agent` test asserted an exact multi-line response that the sanitizer now reshapes, update that expectation to the normalized form.

- [ ] **Step 7: Commit**

```bash
git add webhook-application/whatsapp_webhook/external_services/whatsapp_format.py \
        webhook-application/whatsapp_webhook/external_services/agent_client.py \
        webhook-application/tests/external_services/test_whatsapp_format.py
git commit -m "feat(webhook): deterministic WhatsApp markdown sanitizer on agent replies"
```

---

## Phase 4 — Dev deploy, smoke, soak

### Task 10: Open the PR (draft) and push

**Files:** none.

- [ ] **Step 1: Push**

Run: `git push -u origin feature/agents-core-refactor`

- [ ] **Step 2: Open a draft PR**

Run:
```bash
gh pr create --draft --title "refactor(agents): shared core/ + native BQ tools + WhatsApp sanitizer (ADK 1.35)" --body "$(cat <<'EOF'
## Summary
- New agents/core/ package: shared GlobalGemini, 4 native BigQuery function tools, prompt composition, single build_app() factory
- BQ sub-agent is now an ordinary LlmAgent — LangGraphAgent, the asyncio.Lock, the lazy graph factory, and SQLDatabaseToolkit are deleted
- Per-agent packages reduced to 3-line shims
- Drops langchain-community, langchain-google-vertexai, langgraph, sqlalchemy-bigquery
- PP display name corrected to "Producción Primaria" (matches env.yaml datastore id)
- Webhook gains a deterministic WhatsApp markdown sanitizer; formatting rules removed from prompts (one plain-text hint kept)
- ADK pin UNCHANGED at >=1.35.0,<2.0.0 (2.x bump is the next PR)

## Migration note
Since #43, deploy.py keys idempotency off the stored engine resource name (not display_name / find_existing), so changing PP's display_name UPDATES the existing PP engine in place (same id) — no new engine, no orphan. Both AA and PP update in place. Verified in the #43 npe live deploy.

## Test plan
- [x] agents: bq_tools (8), core_agent (4), shim (2), deploy — all green
- [x] webhook: whatsapp_format (10) + existing suite — green
- [ ] npe deploy + DEPLOYED-engine smoke (verifies extra_packages ships core/)
- [ ] 24h npe soak, error rate near-zero
- [ ] prd deploy + smoke

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 11: Deploy to npe and run the DEPLOYED-engine smoke test

**Files:** none (CI + manual verification).

- [ ] **Step 1: Trigger the deploy workflow against npe**

Run: `gh workflow run deploy-agents.yml --ref feature/agents-core-refactor -f environment=npe`
Then watch: `gh run watch $(gh run list --workflow=deploy-agents.yml --limit=1 --json databaseId -q '.[0].databaseId')`
Expected: success. The final step prints two `reasoningEngines/<id>` lines. Per #43's resource-name keying, the PP display-name change **updates the existing PP engine in place** (same id) — it does **not** create a new engine (see the 2026-07-01 update above; verified live). Both AA and PP update in place.

- [ ] **Step 2: Confirm the secrets were rewritten**

Run:
```bash
gcloud secrets versions access latest --project=agro-extension-digital-npe --secret=engine-aa-resource-name
gcloud secrets versions access latest --project=agro-extension-digital-npe --secret=engine-pp-resource-name
```
Expected: each prints a `projects/.../reasoningEngines/<id>` resource name.

- [ ] **Step 3: DEPLOYED-engine smoke — this is the gate that proves `core/` shipped**

Run (AA):
```bash
RN=$(gcloud secrets versions access latest --project=agro-extension-digital-npe --secret=engine-aa-resource-name)
python - <<PY
import os, vertexai
from vertexai import agent_engines
vertexai.init(project="agro-extension-digital-npe", location="us-central1")
eng = agent_engines.get("$RN")
s = eng.create_session(user_id="smoke-aa")
got = False
for ev in eng.stream_query(user_id="smoke-aa", session_id=s["id"],
                           message="¿Qué puntos tiene la acción A001?"):
    for part in (ev.get("content") or {}).get("parts") or []:
        if part.get("text", "").strip():
            got = True
print("OK" if got else "EMPTY")
PY
```
Expected: `OK`. A `ModuleNotFoundError: No module named 'core'` in the engine logs means `extra_packages` is wrong (Task 6 step 2) — fix and redeploy. Repeat for PP with `engine-pp-resource-name`, `user_id="smoke-pp"`, message `"¿Qué buenas prácticas hay para el agua?"`.

- [ ] **Step 4: Confirm a BQ-routed query exercises the new tools**

Send (via the AA smoke harness above) a clearly data-shaped question, e.g. `"Dame el puntaje total de la dimensión Ambiente"`, and check the engine logs show `list_tables` / `get_schema` / `run_query` tool calls (not a LangGraph trace):
```bash
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND severity>=DEFAULT' --project=agro-extension-digital-npe --limit=50 --format='value(timestamp,textPayload)'
```
Expected: tool-call entries for the four BQ tools; no `langgraph`/`SQLDatabase` references.

### Task 12: End-to-end WhatsApp test (npe) + sanitizer confirmation

**Files:** none.

- [ ] **Step 1:** Send a real WhatsApp message via the npe test number that is likely to elicit a list or a link (e.g. ask for resources/links on a topic).

- [ ] **Step 2:** Watch the webhook logs:
Run: `gcloud logging tail 'resource.type="cloud_run_revision" AND resource.labels.service_name="webhook-app"' --project=agro-extension-digital-npe`
Expected: `agent_query.complete` log lines; reply delivered.

- [ ] **Step 3:** On the WhatsApp client, confirm the reply renders correctly — bold shows as bold (single `*`), no literal `**`, links are bare URLs, no `#` headings, no `|` table pipes.

### Task 13: Soak npe 24h, then promote to prd

**Files:** none.

- [ ] **Step 1:** Wait 24h. Then check the engine error rate:
Run: `gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND severity>=ERROR' --project=agro-extension-digital-npe --limit=100`
Expected: zero / near-zero. Investigate any pattern before promoting.

- [ ] **Step 2: Mark the PR ready and get review.** Run: `gh pr ready`.

- [ ] **Step 3: Deploy to prd** (only after review approval):
Run: `gh workflow run deploy-agents.yml --ref feature/agents-core-refactor -f environment=prd`
Then repeat Task 11 steps 2–4 against `agro-extension-digital-prd`. The prd PP engine likewise **updates in place** (same id) — the display-name change no longer creates a new engine (#43 resource-name keying).

- [ ] **Step 4:** Watch prd error rate + latency for 2h. Then merge the PR to `main`.

### Task 14: Delete the orphaned old PP engines (post-merge cleanup)

**Files:** none.

> **Likely a no-op post-#43.** With resource-name keying, the PR-A deploy updates the existing PP engine in place — it does **not** create a new one — so the display-name rename produces no orphan. Run this task ONLY if a stale engine named `"Planificación de Producción"` actually exists in an env from a *pre-#43* (find_existing-era) deploy; otherwise skip. Confirm with the list command below before deleting anything.

- [ ] **Step 1:** After prd has been green for a soak window, list engines per env and identify the stale PP engine (display_name `"Planificación de Producción"`, no longer referenced by `engine-pp-resource-name`):
```bash
for ENV in npe prd; do
  echo "== $ENV =="
  python - <<PY
import vertexai
from vertexai import agent_engines
vertexai.init(project="agro-extension-digital-$ENV", location="us-central1")
cur = open("/dev/stdin").read().strip() if False else None
for e in agent_engines.list():
    print(e.display_name, "->", e.resource_name)
PY
done
```
- [ ] **Step 2:** For each env, confirm the engine named `"Planificación de Producción"` is **not** the value in `engine-pp-resource-name`, then delete it:
```bash
RN=<old-pp-resource-name>
python -c "import vertexai;from vertexai import agent_engines;vertexai.init(project='agro-extension-digital-<env>',location='us-central1');agent_engines.get('$RN').delete(force=True)"
```
Expected: only the stale engine is removed; the active one (`"Producción Primaria"`) stays.

---

## Conversation compaction (added 2026-07-01)

**Problem.** Each `wa_id` maps to one long-lived Agent Runtime Session (`session_id == wa_id`, the get-or-create pattern from #43). Every WhatsApp turn appends events, and the full history is re-sent to Gemini on each query. Over a long user relationship this inflates token cost and per-turn latency and erodes answer quality ("lost in the middle" / context rot). The #43 live test already shows a single PP turn reaching ~42s when it fans out to RAG + BigQuery; unbounded history growth compounds that. Compaction is short-term **working-memory** hygiene — distinct from Memory Bank long-term curation (deferred to PR-C), so it can land independently.

**Native mechanism (recommended): ADK Context Compaction.** ADK ≥1.16 (we run 1.35) ships `EventsCompactionConfig`. It runs **asynchronously** in the Runner, LLM-summarizes older events over a sliding window, and writes the summary back into the Session as a new event — transparent to the webhook's `send_to_agent` (it still just streams the final answer). Two trigger strategies; **token-based wins if both are set**:

```python
# NOTE: verify the exact import paths + AdkApp threading on ADK 1.35 before coding.
from google.adk.apps import App, EventsCompactionConfig

App(
    name=name,
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        # token-based (primary): compact once the session crosses the budget,
        # keep the most recent turns raw.
        token_threshold=int(os.getenv("COMPACTION_TOKEN_THRESHOLD", "32000")),
        event_retention_size=int(os.getenv("COMPACTION_RETENTION", "6")),
        # sliding-window fallback (turn-based):
        compaction_interval=int(os.getenv("COMPACTION_INTERVAL", "20")),
        overlap_size=2,  # carry 2 prior-summary events for continuity
    ),
)
```

Summarization uses `LlmEventSummarizer` (a Gemini model, `prompt_template` customizable). Point it at a cheap model (e.g. a flash-lite) so compaction never dominates turn latency. Env knobs mirror the `BQ_MAX_BYTES` per-engine-override pattern already in this plan.

**Open questions — verify before committing (do not assume):**
- **AdkApp threading.** We deploy via `vertexai.agent_engines.AdkApp(agent=root_agent)` in `build_app`, not the bare ADK `App`. Confirm how `events_compaction_config` reaches the running app — it may need to be passed through `AdkApp`, set on the `App` that `AdkApp` wraps, or configured on the agent. This is the main unknown and gates whether compaction fits cleanly in `build_app`.
- **One owner only.** Agent Engine managed Sessions ALSO offer platform-side periodic Gemini summarization. Running both double-summarizes and wastes tokens. Pick one — prefer the **ADK-level `EventsCompactionConfig`** for explicit, testable, in-repo control unless the Agent-Engine-level path is strictly required.
- **Managed-session compatibility.** Confirm the summary events ADK writes are accepted/rendered correctly by Agent Runtime managed Sessions (they store `SessionEvents`); a deployed check is the only real proof.

**Scope call.** Small, localized to `build_app` (one config object + one env-driven test). Options: **(a)** fold into PR-A's `build_app` if the AdkApp threading is clean; **(b)** ship as its own small PR after PR-A's deploy soaks. Recommend **(a)** unless the threading turns out non-trivial, then **(b)**.

**Test:**
- Unit: `build_app(...)` attaches an `EventsCompactionConfig` with the env-derived thresholds (assert the object + values).
- Deployed (extend Task 11): drive N synthetic turns against the npe engine, then assert a **summary event appears** in the session and answers stay coherent across the compaction boundary.

---

## Roadmap — later PRs (not detailed here)

These are deliberately deferred (Rodrigo R2/R3) and each gets its own plan when its turn comes.

**PR-B — ADK 2.x bump, alone.** Bump `google-adk>=2.2.0,<3.0.0` in `pyproject.toml` + `deploy.py:REQUIREMENTS`, regen lock. Before relying on it, **verify against live ADK 2.0 docs** (Rodrigo V1): `BaseAgent` now subclasses `BaseNode`; the Event schema gained `node_info`/`output` (check Managed Sessions compatibility for already-stored prd sessions — 2.0 sessions are readable by 1.28+ but not older); audit every `except Exception:` in `core/bq_tools.py` because 2.0's auto-retry is silently disabled by broad excepts. Keep `core/llm_global.py` (Rodrigo V2). Do an explicit npe deploy to confirm the Agent Runtime build image supports 2.x before merging. Separate merge boundary so a failed smoke bisects cleanly to the bump.

**PR-C — planner + RAG quality.** Add `BuiltInPlanner` to root + BQ sub-agents, gated **off by default** (`AGENT_PLANNER=off`) until measured on real npe traffic — the "+10–15% tokens" figure in #44 is wrong; thinking tokens bill at output rate and can dwarf a 100–500-token WhatsApp reply (Rodrigo V3). Add `[fuente: <datastore>]` RAG citations — and **extend the sanitizer's link rule to not consume them** (already guarded; add a regression test). Memory Bank curation is via the **extractor prompt/topics config, not `memory_service_builder`** (Rodrigo V4); proposed categories `{business_profile, certification_stage, prior_qa, crop_or_product, season_or_phenology}`, never raw phone/geo. Strongly prefer landing the **shadow-eval harness** first or in parallel (#44's own "improvements-by-vibes" caveat; Rodrigo Q5).

---

## Self-Review

**Spec coverage (#44 Commit 1 + Commit 4 webhook side, as amended by the review):**
- Shared `core/` package, slim shims → Tasks 1–5 ✓
- 4 native BQ tools replacing LangGraph → Task 2 ✓ (hardening folded in: `{ok,…}` returns, timeouts, byte cap, non-SELECT refusal, `@cache`)
- Delete LangGraph/lock/factory/`tools.py`/3× `langgraph_agent.py` → Task 5 ✓
- Drop 4 deps from pyproject + deploy REQUIREMENTS → Tasks 6–7 ✓
- `extra_packages` ships `core` → Task 6 ✓ (+ deployed-smoke gate Task 11)
- Plain-Python prompt composition, no Jinja → Task 3 ✓
- Drop conftest SQLDatabase stub → Task 8 ✓
- PP display name correction → Task 6 ✓ (+ orphan-engine handling Tasks 11/14)
- WhatsApp sanitizer + move formatting out of prompt, keep one plain-text line → Tasks 3 & 9 ✓
- Deferred (out of scope, in roadmap): ADK 2.x (PR-B); planner, citations, Memory Bank curation, eval harness (PR-C) ✓
- Sequencing #43-first, separate bisectable PRs → "Sequencing context" + Phase 0 + Roadmap ✓

**Placeholder scan:** No TBD/"handle errors"/"similar to" — every code step has full code; deletes enumerate exact paths.

**Type consistency:** Tool dicts use a consistent `{ok, error, …}` shape across `bq_tools.py` and its tests. `build_app(name, display_name, main_datastore_env)` signature matches in `core/agent.py`, both shims (Task 5), and `test_core_agent.py`. `normalize_whatsapp_markdown` name matches across `whatsapp_format.py`, its test, and the `agent_client.py` import. Sub-agent naming (`<name>_rag`, `<name>_bq`) is consistent between `build_app` and the assertions in Task 4.

**One known introspection risk** (flagged inline at Task 4 step 3): the FunctionTool attribute exposing the wrapped function may be `.func` or `.fn` depending on the installed ADK 1.35.x patch — the test adapts, the implementation doesn't.
