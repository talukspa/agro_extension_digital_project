#!/usr/bin/env python
"""Standalone check that both agents are wired to every tool they should have.

This is deliberately OUTSIDE tests/: it imports the two deploy shims exactly the
way `deploy.py` does, so it exercises the real import path that ships to Agent
Runtime rather than a pytest-shaped approximation.

Two modes:

  python scripts/verify_tools.py
      Offline. Stubs google.auth and the BigQuery client, then (a) walks the
      agent graph and (b) actually CALLS all four BigQuery tools, asserting each
      honours the {ok, error, ...} contract. Needs no credentials.

  python scripts/verify_tools.py --live
      Hits real BigQuery with the caller's ADC. Proves the tools work against
      the actual dataset — list_tables/get_schema/check_query/run_query for real.
      Requires GOOGLE_CLOUD_PROJECT + BIGQUERY_DATASET and BigQuery read access.

Exit code is 0 only if every check passes, so it is usable as a CI or
pre-deploy gate.

NOTE: passing here does NOT prove `core/` ships correctly to the engine — that
is what the deployed smoke test covers. This verifies wiring, not packaging.
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys
from unittest.mock import MagicMock, patch

SHIMS = {
    "agent_aa_app.agent_engine_app": "aa_agent",
    "agent_pp_app.agent_engine_app": "pp_agent",
}
BQ_TOOLS = ("list_tables", "get_schema", "check_query", "run_query")
EXPECTED_DATASTORES = 4

_PLACEHOLDER_ENV = {
    "GOOGLE_CLOUD_PROJECT": "verify-project",
    "BIGQUERY_DATASET": "verify_dataset",
    "DATASTORE_AA_ID": "ds-aa",
    "DATASTORE_PP_ID": "ds-pp",
    "DATASTORE_GUIDES_ID": "ds-guides",
    "DATASTORE_FAQ_ID": "ds-faq",
    "DATASTORE_CHILEPRUNES_CL_ID": "ds-cp",
}

_failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{f' — {detail}' if detail else ''}")
    if not ok:
        _failures.append(label)


def seed_offline_env() -> None:
    """Agent Engine injects these at runtime; offline we supply placeholders."""
    for key, value in _PLACEHOLDER_ENV.items():
        os.environ.setdefault(key, value)
    # aiplatform tries to resolve the placeholder project via
    # cloudresourcemanager and logs a full 401 traceback when it can't. It
    # recovers fine; the noise just buries this script's own output.
    import logging

    logging.getLogger("google.cloud.aiplatform").setLevel(logging.CRITICAL)
    logging.getLogger("google.auth").setLevel(logging.CRITICAL)

    import google.auth
    from google.auth.credentials import AnonymousCredentials

    google.auth.default = lambda *a, **k: (
        AnonymousCredentials(),
        os.environ["GOOGLE_CLOUD_PROJECT"],
    )


def require_live_env() -> None:
    missing = [k for k in ("GOOGLE_CLOUD_PROJECT", "BIGQUERY_DATASET")
               if not os.environ.get(k)]
    if missing:
        sys.exit(f"--live needs {', '.join(missing)} set (and BigQuery read access).")


def root_of(module_name: str):
    """AdkApp exposes no public .agent; _tmpl_attrs is the accessor deploy uses."""
    return importlib.import_module(module_name).app._tmpl_attrs["agent"]


def tool_name(t) -> str:
    """ADK keeps plain functions in .tools and wraps them later, in
    canonical_tools(). Tolerate either shape."""
    fn = getattr(t, "func", None) or getattr(t, "fn", None) or t
    return getattr(fn, "__name__", None) or getattr(t, "name", "<unnamed>")


def verify_graph() -> None:
    print("\n[1] agent graph — both engines, every sub-agent, every tool")
    for module_name, expected_root in SHIMS.items():
        print(f"\n  {module_name}")
        root = root_of(module_name)
        check("root name", root.name == expected_root, root.name)

        subs = {t.agent.name: t.agent for t in root.tools}
        check("two sub-agents", set(subs) == {f"{expected_root}_rag",
                                             f"{expected_root}_bq"},
              ", ".join(sorted(subs)))

        bq = subs.get(f"{expected_root}_bq")
        if bq:
            names = sorted(tool_name(t) for t in bq.tools)
            check("all 4 BigQuery tools", names == sorted(BQ_TOOLS), ", ".join(names))

        rag = subs.get(f"{expected_root}_rag")
        if rag:
            check(f"{EXPECTED_DATASTORES} search datastores",
                  len(rag.tools) == EXPECTED_DATASTORES, f"{len(rag.tools)} found")
            bad = [
                t for t in rag.tools
                if not str(getattr(t, "data_store_id", "")).startswith("projects/")
            ]
            # A bare datastore id makes every RAG query fail server-side.
            check("datastores use full resource names", not bad,
                  f"{len(bad)} bare id(s)" if bad else "all fully qualified")


def _mock_bigquery_client() -> MagicMock:
    client = MagicMock()
    table = MagicMock()
    table.table_id = "estandar_aa"
    client.list_tables.return_value = [table]
    field = MagicMock()
    field.name, field.field_type, field.description = "codigo", "STRING", "código"
    client.get_table.return_value = MagicMock(schema=[field])
    job = MagicMock(total_bytes_processed=1234)
    job.result.return_value = [MagicMock(items=lambda: {"codigo": "A001"}.items())]
    client.query.return_value = job
    return client


def verify_tools_are_callable(live: bool) -> None:
    mode = "LIVE against real BigQuery" if live else "offline, BigQuery mocked"
    print(f"\n[2] invoking all 4 BigQuery tools ({mode})")
    from core import bq_tools

    dataset = os.environ.get("BIGQUERY_DATASET", "?")
    table_for_schema = None

    def run_all() -> None:
        nonlocal table_for_schema
        out = bq_tools.list_tables()
        check("list_tables() ok", out.get("ok") is True, out.get("error") or
              f"{len(out.get('tables', []))} table(s) in {dataset}")
        tables = out.get("tables") or []
        table_for_schema = tables[0] if tables else "estandar_aa"

        out = bq_tools.get_schema(table_for_schema)
        check(f"get_schema({table_for_schema!r}) ok", out.get("ok") is True,
              out.get("error") or f"{len(out.get('schema','').splitlines())} column(s)")

        out = bq_tools.check_query(f"SELECT 1 FROM `{table_for_schema}` LIMIT 1"
                                   if live else "SELECT 1")
        check("check_query() dry-run ok", out.get("ok") is True,
              out.get("error") or f"{out.get('bytes_processed')} bytes")

        out = bq_tools.run_query(f"SELECT * FROM `{table_for_schema}` LIMIT 5"
                                 if live else "SELECT 1", max_rows=5)
        check("run_query() ok", out.get("ok") is True,
              out.get("error") or f"{len(out.get('rows', []))} row(s)")

    if live:
        run_all()
    else:
        with patch.object(bq_tools, "_client", return_value=_mock_bigquery_client()):
            run_all()

    print("\n[3] guardrails actually refuse what they claim to")
    for sql, why in [
        ("DELETE FROM t", "non-SELECT"),
        ("SELECT 1; DROP TABLE t", "multi-statement script"),
    ]:
        for fn in (bq_tools.check_query, bq_tools.run_query):
            out = fn(sql)
            check(f"{fn.__name__} refuses {why}", out.get("ok") is False,
                  (out.get("error") or "")[:60])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true",
                    help="hit real BigQuery with your ADC instead of mocks")
    args = ap.parse_args()

    if args.live:
        require_live_env()
    else:
        seed_offline_env()

    print(f"Verifying agent tool wiring "
          f"({'LIVE' if args.live else 'offline'}) "
          f"project={os.environ.get('GOOGLE_CLOUD_PROJECT')}")

    verify_graph()
    verify_tools_are_callable(args.live)

    print()
    if _failures:
        print(f"FAILED — {len(_failures)} check(s): " + "; ".join(_failures))
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
