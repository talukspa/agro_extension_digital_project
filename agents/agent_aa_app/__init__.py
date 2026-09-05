"""Thin entry-point package — the AdkApp lives in agent_engine_app.

Deliberately empty: the old `from . import agent` eagerly built the whole agent
graph at package import. That module is gone (all logic moved to core/), and
importing the shim must not have side effects beyond building the app it
exports.
"""
