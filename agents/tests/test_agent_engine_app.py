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
    assert mod.app.agent is root_agent
