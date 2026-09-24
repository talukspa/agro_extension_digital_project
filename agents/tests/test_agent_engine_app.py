"""The deploy script imports `app` from each shim — guard against drift."""
import importlib

from vertexai.agent_engines import AdkApp


def test_aa_shim_exposes_adkapp():
    mod = importlib.import_module("agent_aa_app.agent_engine_app")
    assert isinstance(mod.app, AdkApp)
    # AdkApp has no public `.agent` — _tmpl_attrs is the accessor (B1).
    assert mod.app._tmpl_attrs["agent"].name == "aa_agent"


def test_pp_shim_exposes_adkapp():
    mod = importlib.import_module("agent_pp_app.agent_engine_app")
    assert isinstance(mod.app, AdkApp)
    assert mod.app._tmpl_attrs["agent"].name == "pp_agent"


def test_wa_shim_exposes_adkapp():
    """Smoke test real del copiloto: que el engine module IMPORTE.

    Es lo único que prueba que build_wa_app() arma de verdad — LlmAgent,
    GlobalGemini, el prompt compuesto desde disco y las diez tools. Si algo de
    eso está roto, sin este test se descubre recién cuando el deploy construye
    el engine.
    """
    mod = importlib.import_module("agent_wa_app.agent_engine_app")
    assert isinstance(mod.app, AdkApp)
    agent = mod.app._tmpl_attrs["agent"]
    assert agent.name == "wa_agent"
    # Las diez tools de /api/agent/*, ni una menos.
    assert len(agent.tools) == 10


def test_wa_no_lleva_las_tools_de_bigquery():
    """El copiloto lee el expediente por HTTP, no por SQL.

    El ADR de #52 saca BigQuery del camino del agente; si build_wa_app() heredara
    las tools de BQ, este agente le daría al modelo una segunda vía a los datos
    que nadie revisó para este caso de uso.
    """
    mod = importlib.import_module("agent_wa_app.agent_engine_app")
    nombres = {getattr(t, "__name__", getattr(t, "name", "")) for t in mod.app._tmpl_attrs["agent"].tools}
    assert not (nombres & {"list_tables", "get_schema", "check_query", "run_query"})
    assert "obtener_perfil_empresa" in nombres


def test_wa_instruction_no_promete_citas_de_rag():
    """El copiloto no tiene sub-agente RAG: enseñarle el formato [fuente: ...]
    sería enseñarle un contrato que nunca va a recibir."""
    from core import prompts
    texto = prompts.wa_instruction("agent_wa")
    assert "copiloto de certificación" in texto
    # whatsapp_plain.md sí se compone; preserve_citations.md no.
    assert "NO uses" in texto and "Markdown" in texto
    assert "[fuente:" not in texto
