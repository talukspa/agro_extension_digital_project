"""Native ADK function tools over BigQuery — replaces the LangGraph SQL agent.

Each tool returns {"ok": bool, "error": str | None, ...} and never raises into
the model: the LlmAgent recovers via the error -> fix -> retry loop the prompt
teaches. `list_tables` / `get_schema` memoize SUCCESSES ONLY — the @cache sits
on an inner helper that raises, so a transient BigQuery error is never frozen
in for the process lifetime (schemas rarely change; engine redeploy is the
natural flush). `check_query` is a free BigQuery dry-run guard. `run_query`
refuses non-SELECT, refuses scans over BQ_MAX_BYTES (default 1 GB), and
truncates to max_rows.

Caps are read PER CALL, never bound at import: import-time binding made them
untestable (monkeypatch.setenv runs after import) and silently ignored any
per-engine env override.
"""
import functools
import os

from google.cloud import bigquery

# Hard caps — env-overridable per engine without code change. Read per call.
_DEFAULT_MAX_BYTES = 1024 * 1024 * 1024  # 1 GB
_DEFAULT_MAX_ROWS = 100
LIST_TIMEOUT = 10.0
SCHEMA_TIMEOUT = 10.0
CHECK_TIMEOUT = 30.0
RUN_TIMEOUT = 60.0


def _project() -> str:
    return os.environ["GOOGLE_CLOUD_PROJECT"]


def _dataset() -> str:
    return os.environ["BIGQUERY_DATASET"]


def _max_bytes() -> int:
    return int(os.environ.get("BQ_MAX_BYTES", str(_DEFAULT_MAX_BYTES)))


def _max_rows() -> int:
    return int(os.environ.get("BQ_MAX_ROWS", str(_DEFAULT_MAX_ROWS)))


def _client() -> bigquery.Client:
    # Created per call (not cached): the AdkApp is deepcopy'd at engine-create
    # time and a cached client holds unpicklable module refs (same reason as
    # GlobalGemini.api_client).
    return bigquery.Client(project=_project())


def _is_select(sql: str) -> bool:
    """True only for a SINGLE read-only statement.

    The multi-statement check is not decoration: BigQuery executes scripts, so
    `SELECT 1; DROP TABLE t` would pass a first-token-only guard and run the
    DROP. Read-only IAM (roles/bigquery.dataViewer) is the real backstop, but a
    guard whose error says "Only SELECT/WITH queries are allowed" should not
    claim more than it enforces.

    A semicolon inside a string literal is refused too. That is a deliberate
    false negative: erring toward refusal costs the model one rewrite, while
    erring the other way costs a executed statement we never intended to allow.
    """
    stripped = sql.strip().rstrip(";").strip()
    if ";" in stripped:
        return False
    head = stripped.lstrip("(").lstrip().upper()
    return head.startswith("SELECT") or head.startswith("WITH")


@functools.cache
def _list_tables_cached() -> tuple:
    """Raises on failure — so functools.cache never memoizes an error."""
    ref = f"{_project()}.{_dataset()}"
    return tuple(t.table_id for t in _client().list_tables(ref, timeout=LIST_TIMEOUT))


def list_tables() -> dict:
    """List the table names available in the configured BigQuery dataset."""
    try:
        return {"ok": True, "error": None, "tables": list(_list_tables_cached())}
    except Exception as e:  # noqa: BLE001 — surface to the model, never crash
        return {"ok": False, "error": str(e), "tables": []}


@functools.cache
def _get_schema_cached(table: str) -> str:
    """Raises on failure — so functools.cache never memoizes an error."""
    ref = f"{_project()}.{_dataset()}.{table}"
    meta = _client().get_table(ref, timeout=SCHEMA_TIMEOUT)
    lines = []
    for f in meta.schema:
        desc = f" — {f.description}" if f.description else ""
        lines.append(f"{f.name} {f.field_type}{desc}")
    return "\n".join(lines)


def get_schema(table: str) -> dict:
    """Return the column schema (name, type, description) for one table."""
    try:
        return {"ok": True, "error": None, "schema": _get_schema_cached(table)}
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


def run_query(sql: str, max_rows: int = 100) -> dict:
    """Run a SELECT and return up to max_rows result rows as dicts."""
    if not _is_select(sql):
        return {"ok": False, "error": "Only SELECT/WITH queries are allowed.",
                "rows": [], "truncated": False}
    # BQ_MAX_ROWS is a ceiling on whatever the model asked for, not a default.
    max_rows = min(max_rows, _max_rows())
    cap = _max_bytes()
    client = _client()
    try:
        dry = client.query(
            sql,
            job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False),
            timeout=CHECK_TIMEOUT,
        )
        if dry.total_bytes_processed and dry.total_bytes_processed > cap:
            return {
                "ok": False,
                "error": (
                    f"Query exceeds the {cap} byte scan cap "
                    f"({dry.total_bytes_processed} bytes). Add filters or a LIMIT."
                ),
                "rows": [], "truncated": False,
            }
        cfg = bigquery.QueryJobConfig(maximum_bytes_billed=cap)
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
