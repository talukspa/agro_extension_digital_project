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
