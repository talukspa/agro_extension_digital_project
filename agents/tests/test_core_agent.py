"""Shape tests for core.agent.build_app — no network (env is seeded in conftest)."""
from vertexai.agent_engines import AdkApp


def _root(app: AdkApp):
    """AdkApp exposes NO public `.agent` — verified: hasattr(AdkApp, "agent") is
    False. The wrapped agent lives in `_tmpl_attrs`, the internal-but-stable
    template surface `vertexai.agent_engines.create()` itself reads. This is the
    same accessor the pre-existing tests/test_agent_engine_app.py used (B1)."""
    return app._tmpl_attrs["agent"]


def _tool_name(t):
    """ADK 1.35 leaves plain functions in `LlmAgent.tools` untouched — the
    FunctionTool wrapping happens later, in canonical_tools(), so neither
    `.func` nor `.fn` exists at this point (verified). Accept either shape so a
    future ADK patch that wraps eagerly doesn't break this assertion."""
    fn = getattr(t, "func", None) or getattr(t, "fn", None) or t
    return getattr(fn, "__name__", None) or getattr(t, "name", None)


def test_build_app_returns_adkapp_with_named_root():
    from core.agent import build_app
    app = build_app(
        name="aa_agent",
        display_name="Adecuación Agroindustrial",
        main_datastore_env="DATASTORE_AA_ID",
    )
    assert isinstance(app, AdkApp)
    assert _root(app).name == "aa_agent"


def test_root_has_rag_and_bq_subagents():
    from core.agent import build_app
    app = build_app(
        name="pp_agent",
        display_name="Producción Primaria",
        main_datastore_env="DATASTORE_PP_ID",
    )
    tool_names = {t.agent.name for t in _root(app).tools}
    assert tool_names == {"pp_agent_rag", "pp_agent_bq"}


def test_bq_subagent_uses_four_function_tools():
    from core.agent import build_app
    app = build_app(
        name="aa_agent",
        display_name="Adecuación Agroindustrial",
        main_datastore_env="DATASTORE_AA_ID",
    )
    bq = next(t.agent for t in _root(app).tools if t.agent.name == "aa_agent_bq")
    fn_names = {_tool_name(t) for t in bq.tools}
    assert fn_names == {"list_tables", "get_schema", "check_query", "run_query"}


def test_datastore_builds_full_resource_name():
    # Regression guard for the #43 live-deploy bug: the bare id breaks all RAG.
    from core.agent import _datastore
    assert _datastore("0001-example_123") == (
        "projects/test-project/locations/global/collections/"
        "default_collection/dataStores/0001-example_123"
    )
