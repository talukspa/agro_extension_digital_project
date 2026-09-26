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
    assert tool_names == {"pp_agent_rag", "pp_agent_bq", "pp_agent_record"}


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


# --- G1: _datastore must be idempotent -------------------------------------

def test_datastore_passes_through_an_already_qualified_name():
    """cicd/stacks/*/env.yaml holds bare ids, agents/.env holds full paths.
    Wrapping a full path again yields .../dataStores/projects/.../dataStores/<id>,
    which Vertex rejects with the SAME 'Invalid Vertex AI datastore resource
    name' error a bare id produces."""
    from core.agent import _datastore
    full = ("projects/agro-extension-digital-npe/locations/global/collections/"
            "default_collection/dataStores/0001-guias_1745450505033")
    assert _datastore(full) == full


def test_datastore_is_idempotent():
    from core.agent import _datastore
    assert _datastore(_datastore("0001-example_123")) == _datastore("0001-example_123")


# --- Task 6: EXPEDIENTE colgado del root ------------------------------------

PRODUCTOR = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"


def test_el_root_tiene_los_tres_subagentes():
    """RAG, BQ y EXPEDIENTE. El root enruta entre tres, no entre dos."""
    from core.agent import build_app
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    nombres = {t.agent.name for t in app._tmpl_attrs["agent"].tools}
    assert nombres == {"pp_agent_rag", "pp_agent_bq", "pp_agent_record"}


def test_el_subagente_del_expediente_tiene_las_once_tools():
    from core.agent import build_app
    from core import record_tools
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    record = next(t.agent for t in app._tmpl_attrs["agent"].tools
                  if t.agent.name == "pp_agent_record")
    assert len(record.tools) == len(record_tools.TOOLS) == 11


def test_el_guard_de_consentimiento_esta_en_el_root():
    from core.agent import build_app
    from core import consent_guard
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    root = app._tmpl_attrs["agent"]
    assert root.before_model_callback is consent_guard.before_model


def test_el_root_sabe_cuando_usar_el_expediente():
    """El enrutamiento se escribe en el prompt, no se adivina."""
    from core import prompts
    for agente in ("agent_pp", "agent_aa"):
        assert "EXPEDIENTE" in prompts.root_instruction(agente)


async def test_el_bloque_de_contexto_del_productor_llega_a_la_instruccion(monkeypatch):
    """El test de arriba sólo cuenta tools. Este comprueba que la instrucción
    del sub-agente record de verdad concatena el bloque de contexto del
    productor (Task 3) y no lo deja huérfano — es exactamente el hueco que
    dejó pasar el guard de consentimiento en esta misma task."""
    from core import producer_scope
    from core.agent import build_app

    async def bloque_falso(ctx):
        return "\n\nBLOQUE-DE-CONTEXTO-RECONOCIBLE"

    monkeypatch.setattr(producer_scope, "for_context", bloque_falso)

    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    record = next(t.agent for t in app._tmpl_attrs["agent"].tools
                  if t.agent.name == "pp_agent_record")

    assert callable(record.instruction)

    class Ctx:
        user_id = PRODUCTOR

    texto = record.instruction(Ctx())
    if hasattr(texto, "__await__"):
        texto = await texto

    assert "BLOQUE-DE-CONTEXTO-RECONOCIBLE" in texto
    # Y el prompt estático del expediente sigue ahí, no lo reemplazó.
    from core import prompts
    assert prompts.record_instruction("agent_pp")[:60] in texto


def test_el_guard_no_esta_en_los_subagentes():
    """Si antes que sea del root, sólo el root lo tiene: si estuviera también
    en record, la baja se registraría dos veces."""
    from core.agent import build_app
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    for t in app._tmpl_attrs["agent"].tools:
        assert t.agent.before_model_callback is None


def test_solo_record_tiene_las_tools_del_expediente():
    """rag y bq no heredaron las tools del expediente por accidente."""
    from core.agent import build_app
    from core import record_tools
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    nombres_expediente = {fn.__name__ for fn in record_tools.TOOLS}
    for t in app._tmpl_attrs["agent"].tools:
        if t.agent.name == "pp_agent_record":
            continue
        nombres_del_subagente = {getattr(tool, "__name__", None) for tool in t.agent.tools}
        assert not (nombres_del_subagente & nombres_expediente)


def test_los_dos_agentes_quedan_iguales_en_estructura():
    """Los tests de arriba sólo miran PP. aa_agent tiene que quedar igual:
    los tres sub-agentes, el guard, las 11 tools."""
    from core.agent import build_app
    from core import consent_guard, record_tools

    for name in ("pp_agent", "aa_agent"):
        env = "DATASTORE_PP_ID" if name == "pp_agent" else "DATASTORE_AA_ID"
        app = build_app(name=name, display_name=name, main_datastore_env=env)
        root = app._tmpl_attrs["agent"]

        nombres = {t.agent.name for t in root.tools}
        assert nombres == {f"{name}_rag", f"{name}_bq", f"{name}_record"}
        assert root.before_model_callback is consent_guard.before_model

        record = next(t.agent for t in root.tools if t.agent.name == f"{name}_record")
        assert len(record.tools) == len(record_tools.TOOLS) == 11
