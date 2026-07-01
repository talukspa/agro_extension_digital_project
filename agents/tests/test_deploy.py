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


def test_env_vars_for_ships_google_cloud_project(monkeypatch):
    """GOOGLE_CLOUD_PROJECT must be shipped explicitly to the engine env."""
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
    env = deploy.env_vars_for("agent_aa", "agro-extension-digital-npe")
    assert env["GOOGLE_CLOUD_PROJECT"] == "agro-extension-digital-npe"


# Idempotency is now keyed off the resource name stored in Secret Manager
# (find_existing / display_name matching was removed), so we test read_secret.
def test_read_secret_returns_stored_resource_name(monkeypatch):
    import deploy
    fake_client = MagicMock()
    fake_client.access_secret_version.return_value = MagicMock(
        payload=MagicMock(
            data=b"projects/p/locations/us-central1/reasoningEngines/123"
        )
    )
    monkeypatch.setattr(
        deploy.secretmanager, "SecretManagerServiceClient", lambda: fake_client
    )
    assert (
        deploy.read_secret("proj", "engine-aa-resource-name")
        == "projects/p/locations/us-central1/reasoningEngines/123"
    )


def test_read_secret_returns_none_when_secret_missing(monkeypatch):
    import deploy
    fake_client = MagicMock()
    fake_client.access_secret_version.side_effect = deploy.gax.NotFound("nope")
    monkeypatch.setattr(
        deploy.secretmanager, "SecretManagerServiceClient", lambda: fake_client
    )
    assert deploy.read_secret("proj", "missing") is None
