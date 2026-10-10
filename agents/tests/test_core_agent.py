"""Shape tests for core.agent.build_app — no network (env is seeded in conftest)."""
from vertexai.agent_engines import AdkApp


def _subagentes(root):
    """Los AgentTool del raíz. `root.tools` también trae ofrecer_opciones, que
    es una función y no tiene `.agent`."""
    return [t for t in root.tools if hasattr(t, "agent")]


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


def test_root_has_rag_and_catalog_subagents():
    from core.agent import build_app
    app = build_app(
        name="pp_agent",
        display_name="Producción Primaria",
        main_datastore_env="DATASTORE_PP_ID",
    )
    tool_names = {t.agent.name for t in _subagentes(_root(app))}
    assert tool_names == {"pp_agent_rag", "pp_agent_catalog", "pp_agent_record"}


def test_catalog_subagent_uses_four_function_tools():
    from core.agent import build_app
    app = build_app(
        name="aa_agent",
        display_name="Adecuación Agroindustrial",
        main_datastore_env="DATASTORE_AA_ID",
    )
    bq = next(t.agent for t in _subagentes(_root(app)) if t.agent.name == "aa_agent_catalog")
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
    nombres = {t.agent.name for t in _subagentes(app._tmpl_attrs["agent"])}
    assert nombres == {"pp_agent_rag", "pp_agent_catalog", "pp_agent_record"}


def test_el_subagente_del_expediente_tiene_las_once_tools():
    from core.agent import build_app
    from core import record_tools
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    record = next(t.agent for t in _subagentes(app._tmpl_attrs["agent"])
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
    record = next(t.agent for t in _subagentes(app._tmpl_attrs["agent"])
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
    for t in _subagentes(app._tmpl_attrs["agent"]):
        assert t.agent.before_model_callback is None


def test_solo_record_tiene_las_tools_del_expediente():
    """rag y bq no heredaron las tools del expediente por accidente."""
    from core.agent import build_app
    from core import record_tools
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    nombres_expediente = {fn.__name__ for fn in record_tools.TOOLS}
    for t in _subagentes(app._tmpl_attrs["agent"]):
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

        nombres = {t.agent.name for t in _subagentes(root)}
        assert nombres == {f"{name}_rag", f"{name}_catalog", f"{name}_record"}
        assert root.before_model_callback is consent_guard.before_model

        record = next(t.agent for t in _subagentes(root) if t.agent.name == f"{name}_record")
        assert len(record.tools) == len(record_tools.TOOLS) == 11


# ------------------------------------ el catálogo reemplazó a Postgres en el grafo
def test_el_root_tiene_rag_catalogo_y_expediente():
    from core.agent import build_app
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    nombres = {t.agent.name for t in _subagentes(app._tmpl_attrs["agent"])}
    assert nombres == {"pp_agent_rag", "pp_agent_catalog", "pp_agent_record"}


def test_el_subagente_del_catalogo_tiene_las_cuatro_tools():
    from core.agent import build_app
    from core import catalog_tools
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    catalogo = next(t.agent for t in _subagentes(app._tmpl_attrs["agent"])
                    if t.agent.name == "pp_agent_catalog")
    assert len(catalogo.tools) == len(catalog_tools.TOOLS) == 4


def test_no_queda_nada_de_bigquery_en_el_paquete():
    """Un rename a medias es peor que ninguno.

    Se prohíbe lo que ROMPE o MIENTE, no la palabra: un import de un módulo que no
    existe, un nombre de variable que nadie inyecta, una dependencia que nadie usa.

    Las menciones a BigQuery EN PROSA se permiten a propósito: explican qué se
    reemplazó y por qué, y borrarlas dejaría los comentarios diciendo "la copia
    desincronizada" sin decir de qué copia hablan. Ésa es la historia que le ahorra
    a alguien reabrir la decisión en seis meses.
    """
    from pathlib import Path
    raiz = Path(__file__).resolve().parents[1]

    # los archivos borrados
    assert not (raiz / "core" / "bq_tools.py").exists()
    assert not (raiz / "tests" / "test_bq_tools.py").exists()
    for agente in ("agent_pp", "agent_aa"):
        assert not (raiz / "core" / "prompts" / agente / "bq.md").exists()
        assert not (raiz / "core" / "prompts" / agente / "bq_description.md").exists()

    # nada que pueda ejecutarse o inyectarse
    rompe = [
        "from core import bq_tools", "import bq_tools", "bq_tools.",
        "BIGQUERY_DATASET", "BQ_MAX_BYTES", "BQ_MAX_ROWS",
        "google-cloud-bigquery", "from google.cloud import bigquery",
        "prompts.bq_instruction", "prompts.bq_description",
    ]
    for patron in rompe:
        golpes = []
        for p in list(raiz.rglob("*.py")) + list(raiz.rglob("*.toml")):
            if ".venv" in str(p) or "__pycache__" in str(p):
                continue
            texto = p.read_text(encoding="utf-8")
            # la lista de patrones de este propio test no cuenta
            if p.name == "test_core_agent.py":
                continue
            if patron in texto:
                golpes.append(p.relative_to(raiz).as_posix())
        assert not golpes, f"{patron} sigue en {golpes}"


def test_el_root_nombra_al_catalogo_no_a_bq():
    from core import prompts
    for agente in ("agent_pp", "agent_aa"):
        texto = prompts.root_instruction(agente)
        assert "CATÁLOGO" in texto
        assert "Postgres" not in texto


def test_los_prompts_de_bq_ya_no_existen():
    from pathlib import Path
    raiz = Path(__file__).resolve().parents[1] / "core" / "prompts"
    for agente in ("agent_pp", "agent_aa"):
        assert not (raiz / agente / "bq.md").exists()
        assert not (raiz / agente / "bq_description.md").exists()


def test_el_root_guarda_el_adjunto_en_el_estado():
    """El expediente corre como AgentTool: el id del archivo le llega por el
    estado que deja este callback del raíz, no por el texto del pedido."""
    from core.agent import build_app
    from core import attachment_state
    for name, env in (("pp_agent", "DATASTORE_PP_ID"), ("aa_agent", "DATASTORE_AA_ID")):
        root = build_app(name=name, display_name=name, main_datastore_env=env)._tmpl_attrs["agent"]
        assert root.before_agent_callback is attachment_state.before_agent


async def test_la_instruccion_del_expediente_incluye_el_adjunto_recibido(monkeypatch):
    from core import attachment_state, producer_scope
    from core.agent import build_app

    async def sin_bloque(ctx):
        return ""

    monkeypatch.setattr(producer_scope, "for_context", sin_bloque)
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    record = next(t.agent for t in _subagentes(app._tmpl_attrs["agent"])
                  if t.agent.name == "pp_agent_record")

    class Ctx:
        user_id = PRODUCTOR
        state = {attachment_state.STATE_KEY: [
            {"id_de_adjunto": "55", "nombre_archivo": "", "recibido": 9e12}]}

    texto = record.instruction(Ctx())
    if hasattr(texto, "__await__"):
        texto = await texto
    assert texto.endswith("ADJUNTOS RECIBIDOS (del más viejo al más nuevo):\n- id_de_adjunto=55")


def test_el_root_tiene_la_tool_del_menu_y_los_subagentes_no():
    """Sólo el raíz: los eventos de un AgentTool no llegan al stream que lee
    el webhook, así que en un sub-agente la tool no dibujaría nada."""
    from core.agent import build_app
    from core import options_tools

    for name, env in (("pp_agent", "DATASTORE_PP_ID"), ("aa_agent", "DATASTORE_AA_ID")):
        root = build_app(name=name, display_name=name, main_datastore_env=env)._tmpl_attrs["agent"]
        assert options_tools.ofrecer_opciones in root.tools
        for t in root.tools:
            if hasattr(t, "agent"):
                assert options_tools.ofrecer_opciones not in t.agent.tools
