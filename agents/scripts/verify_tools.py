#!/usr/bin/env python
"""Standalone check that both agents are wired to every tool they should have.

This is deliberately OUTSIDE tests/: it imports the two deploy shims exactly the
way `deploy.py` does, so it exercises the real import path that ships to Agent
Runtime rather than a pytest-shaped approximation.

Two modes:

  python scripts/verify_tools.py
      Offline. Stubs google.auth and the Postgres connection, then (a) walks the
      agent graph and (b) actually CALLS all four catalog tools, asserting each
      honours the {ok, error, ...} contract. Needs no credentials.

  python scripts/verify_tools.py --live
      Hits the real Postgres catalog with CATALOG_DSN. Proves the tools work against
      the actual dataset — list_tables/get_schema/check_query/run_query for real.
      Requires CATALOG_DSN con el rol agent_catalog_reader.

  python scripts/verify_tools.py --runner
      THE REAL GATE. Everything above, plus it actually drives both agents with
      real questions through InMemoryRunner and asserts the MODEL reaches for
      the tools — routing, prompts and tool declarations exercised together.
      Costs live Gemini + Postgres + Vertex AI Search calls; run it against npe.

      Note it probes the BQ sub-agent DIRECTLY as well as through the root.
      AgentTool runs a sub-agent in its own invocation, so its function calls
      never appear in the root runner's event stream — checking only the root
      reports "no tools called" even when the reply plainly contains live
      catalog data. That false negative is exactly what this layout avoids.

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
CATALOG_TOOLS = ("list_tables", "get_schema", "check_query", "run_query")
EXPECTED_DATASTORES = 4

_PLACEHOLDER_ENV = {
    "GOOGLE_CLOUD_PROJECT": "verify-project",
    "CATALOG_DSN": "verify_dataset",
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
    missing = [k for k in ("GOOGLE_CLOUD_PROJECT", "CATALOG_DSN")
               if not os.environ.get(k)]
    if missing:
        sys.exit(f"--live needs {', '.join(missing)} set (y acceso al catálogo).")


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
            check("all 4 catalog tools", names == sorted(CATALOG_TOOLS), ", ".join(names))

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


def _mock_postgres_conn() -> MagicMock:
    """Doble de la conexión de psycopg: sólo lo que catalog_tools usa.

    `cursor.description` va con objetos que tienen `.name`, no tuplas — psycopg lo
    expone así, y un doble con tuplas hace fallar el código que sí funciona contra
    la base real.
    """
    columna = MagicMock()
    columna.name = "question_number"
    cur = MagicMock()
    cur.__enter__ = lambda self: self
    cur.__exit__ = lambda self, *a: False
    cur.description = [columna]
    cur.fetchall.return_value = [("questions",)]
    conn = MagicMock()
    conn.__enter__ = lambda self: self
    conn.__exit__ = lambda self, *a: False
    conn.cursor.return_value = cur
    return conn


def verify_tools_are_callable(live: bool) -> None:
    mode = "LIVE against real Postgres" if live else "offline, Postgres mocked"
    print(f"\n[2] invoking all 4 catalog tools ({mode})")
    from core import catalog_tools

    def run_all() -> None:
        out = catalog_tools.list_tables()
        check("list_tables() ok", out.get("ok") is True, out.get("error") or
              f"{len(out.get('tables', []))} table(s)")

        out = catalog_tools.get_schema("questions")
        check("get_schema('questions') ok", out.get("ok") is True,
              out.get("error") or f"{len(out.get('schema','').splitlines())} column(s)")

        out = catalog_tools.check_query(
            "SELECT question_number FROM questions LIMIT 1" if live else "SELECT 1")
        check("check_query() EXPLAIN ok", out.get("ok") is True,
              out.get("error") or "plan devuelto")

        out = catalog_tools.run_query(
            "SELECT question_number FROM questions LIMIT 5" if live else "SELECT 1",
            max_rows=5)
        check("run_query() ok", out.get("ok") is True,
              out.get("error") or f"{len(out.get('rows', []))} row(s)")

    if live:
        run_all()
    else:
        with patch.object(catalog_tools, "_connect",
                          return_value=_mock_postgres_conn()):
            run_all()

    print("\n[3] guardrails actually refuse what they claim to")
    for sql, why in [
        ("DELETE FROM t", "non-SELECT"),
        ("SELECT 1; DROP TABLE t", "multi-statement script"),
    ]:
        for fn in (catalog_tools.check_query, catalog_tools.run_query):
            out = fn(sql)
            check(f"{fn.__name__} refuses {why}", out.get("ok") is False,
                  (out.get("error") or "")[:60])


PROBES = [
    ("BQ", "¿Cuántas acciones tiene el estándar? Consulta la base de datos.",
     {"list_tables", "get_schema", "check_query", "run_query"}),
    ("RAG", "¿Qué dice la guía sobre el manejo del agua?",
     set()),  # tool names are datastore-specific; we only require a sub-agent call
]


async def _drive(root, question: str) -> tuple[set[str], str]:
    """Run one question through the real agent; return (tools called, reply)."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=root, app_name="verify")
    session = await runner.session_service.create_session(
        app_name="verify", user_id="verify-user"
    )
    called: set[str] = set()
    reply: list[str] = []
    async for event in runner.run_async(
        user_id="verify-user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=question)]),
    ):
        for part in (event.content.parts if event.content else []) or []:
            if getattr(part, "function_call", None):
                called.add(part.function_call.name)
            if getattr(part, "text", None) and event.author == root.name:
                reply.append(part.text)
    return called, "".join(reply).strip()


def verify_agents_actually_call_tools() -> None:
    """THE REAL GATE: does the model actually invoke the tools we wired?

    Static wiring proves the tools exist. This proves the agent reaches for
    them on a real question — the only check that exercises routing, the
    prompts, and the tool declarations together.
    """
    import asyncio

    print("\n[4] driving the real agents (live Gemini + Postgres + Vertex Search)")
    for module_name, expected_root in SHIMS.items():
        root = root_of(module_name)
        print(f"\n  {module_name}")

        # (a) Root level: does the supervisor route to the right sub-agent?
        for label, question, _ in PROBES:
            try:
                called, reply = asyncio.run(_drive(root, question))
            except Exception as e:  # noqa: BLE001 — report, don't abort the sweep
                check(f"{label} probe ran", False, f"{type(e).__name__}: {str(e)[:90]}")
                continue
            sub_called = {c for c in called if c.endswith(("_rag", "_bq"))}
            check(f"{label} probe delegated to a sub-agent",
                  bool(sub_called), ", ".join(sorted(sub_called)) or "none")
            check(f"{label} probe produced an answer", bool(reply),
                  (reply[:70] + "...") if reply else "empty")

        # (b) Sub-agent level: does the BQ agent actually reach for its tools?
        #
        # This must drive the sub-agent DIRECTLY. AgentTool runs it in its own
        # invocation, so its function calls never surface in the root runner's
        # event stream — probing only the root shows "no tools called" even
        # when the answer plainly contains live catalog data.
        bq_agent = next(
            (t.agent for t in root.tools if t.agent.name.endswith("_bq")), None
        )
        if bq_agent is None:
            check("BQ sub-agent found", False)
            continue
        try:
            called, reply = asyncio.run(
                _drive(bq_agent, "¿Cuántas filas tiene la tabla principal? "
                                 "Usa las herramientas para averiguarlo.")
            )
        except Exception as e:  # noqa: BLE001
            check("BQ sub-agent probe ran", False, f"{type(e).__name__}: {str(e)[:90]}")
            continue
        hit = {"list_tables", "get_schema", "check_query", "run_query"} & called
        check("BQ sub-agent invoked its Postgres tools", bool(hit),
              ", ".join(sorted(hit)) or "none called")
        check("BQ sub-agent started with list_tables", "list_tables" in called,
              "workflow step 1" if "list_tables" in called else "skipped discovery")
        check("BQ sub-agent produced an answer", bool(reply),
              (reply[:70] + "...") if reply else "empty")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true",
                    help="hit real Postgres with your ADC instead of mocks")
    ap.add_argument("--runner", action="store_true",
                    help="THE REAL GATE: drive both agents with real questions "
                         "and assert the model actually calls the tools "
                         "(costs live Gemini/Postgres/Search calls)")
    args = ap.parse_args()

    if args.live or args.runner:
        require_live_env()
    else:
        seed_offline_env()

    print(f"Verifying agent tool wiring "
          f"({'LIVE' if args.live else 'offline'}) "
          f"project={os.environ.get('GOOGLE_CLOUD_PROJECT')}")

    verify_graph()
    verify_tools_are_callable(args.live or args.runner)
    if args.runner:
        verify_agents_actually_call_tools()

    print()
    if _failures:
        print(f"FAILED — {len(_failures)} check(s): " + "; ".join(_failures))
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
