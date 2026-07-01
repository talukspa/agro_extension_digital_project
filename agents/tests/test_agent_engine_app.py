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
    # AdkApp stores the wrapped agent in _tmpl_attrs (internal but stable
    # template-rendering surface used by vertexai.agent_engines.create).
    assert mod.app._tmpl_attrs["agent"] is root_agent


def test_pp_shim_exposes_app_attribute():
    mod = importlib.import_module("agent_pp_app.agent_engine_app")
    assert hasattr(mod, "app"), "agent_pp_app.agent_engine_app must export `app`"


def test_pp_shim_app_wraps_root_agent():
    mod = importlib.import_module("agent_pp_app.agent_engine_app")
    from agent_pp_app.agent import root_agent
    # AdkApp stores the wrapped agent in _tmpl_attrs (internal but stable
    # template-rendering surface used by vertexai.agent_engines.create).
    assert mod.app._tmpl_attrs["agent"] is root_agent


@pytest.mark.parametrize("pkg", ["agent_aa_app", "agent_pp_app"])
def test_datastore_builds_full_resource_name(pkg):
    """VertexAiSearchTool needs the full datastore resource name, not the bare
    id — the bare id makes GenerateContent fail with 'Invalid Vertex AI
    datastore resource name'. GOOGLE_CLOUD_PROJECT is seeded by conftest."""
    agent = importlib.import_module(f"{pkg}.agent")
    got = agent._datastore("0001-example_123")
    assert got == (
        "projects/test-project/locations/global/collections/"
        "default_collection/dataStores/0001-example_123"
    )
