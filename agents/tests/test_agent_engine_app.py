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
