"""Unit tests for agents/deploy.py pure helpers.

Network-touching paths (vertexai.init, agent_engines.create/list, Secret
Manager) are NOT tested here — they are covered by Phase 3's live smoke
test against the dev project.
"""
from unittest.mock import MagicMock

import pytest


def test_env_vars_for_collects_required_runtime_keys(monkeypatch):
    """env_vars_for must read exactly the runtime + telemetry env keys."""
    import importlib
    import deploy
    for k, v in {
        "DATASTORE_AA_ID": "ds-aa",
        "DATASTORE_PP_ID": "ds-pp",
        "DATASTORE_GUIDES_ID": "ds-g",
        "DATASTORE_FAQ_ID": "ds-faq",
        "DATASTORE_CHILEPRUNES_CL_ID": "ds-cl",
        "BIGQUERY_DATASET": "ds-bq",
    }.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("OTEL_CAPTURE_MESSAGE_CONTENT", raising=False)
    importlib.reload(deploy)  # TELEMETRY_ENV is materialized at import
    env = deploy.env_vars_for("agent_aa")
    assert env["DATASTORE_AA_ID"] == "ds-aa"
    assert env["BIGQUERY_DATASET"] == "ds-bq"
    # Telemetry must be on by default.
    assert env["GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"] == "true"
    # Message-content capture is OFF by default to keep PII out of traces.
    assert env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == "false"


def test_env_vars_for_message_content_capture_opt_in(monkeypatch):
    """Operators can flip OTEL_CAPTURE_MESSAGE_CONTENT to opt back in."""
    import importlib
    import deploy
    for k, v in {
        "DATASTORE_AA_ID": "ds-aa",
        "DATASTORE_PP_ID": "ds-pp",
        "DATASTORE_GUIDES_ID": "ds-g",
        "DATASTORE_FAQ_ID": "ds-faq",
        "DATASTORE_CHILEPRUNES_CL_ID": "ds-cl",
        "BIGQUERY_DATASET": "ds-bq",
    }.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("OTEL_CAPTURE_MESSAGE_CONTENT", "true")
    importlib.reload(deploy)
    env = deploy.env_vars_for("agent_aa")
    assert env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == "true"


def test_env_vars_for_raises_when_required_key_missing(monkeypatch):
    monkeypatch.delenv("DATASTORE_AA_ID", raising=False)
    import deploy
    with pytest.raises(KeyError):
        deploy.env_vars_for("agent_aa")


def test_find_existing_returns_resource_name_on_match(monkeypatch):
    import deploy
    fake = MagicMock(
        display_name="Adecuación Agroindustrial",
        resource_name="projects/p/locations/us-central1/reasoningEngines/123",
    )
    monkeypatch.setattr(deploy.agent_engines, "list", lambda: [fake])
    assert deploy.find_existing("Adecuación Agroindustrial") == fake.resource_name


def test_find_existing_returns_none_on_no_match(monkeypatch):
    import deploy
    monkeypatch.setattr(deploy.agent_engines, "list", lambda: [])
    assert deploy.find_existing("nope") is None
