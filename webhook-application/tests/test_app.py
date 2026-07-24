"""Tests for the FastAPI app factory and health/root endpoints."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from whatsapp_webhook import app as app_module
from whatsapp_webhook.app import create_app, get_version
from whatsapp_webhook.utils.app_config import config


@pytest.fixture
def client():
    return TestClient(create_app())


def test_get_version_reads_pyproject():
    # Running from the package root, pyproject.toml is present.
    assert get_version() == "0.1.0"


def test_get_version_falls_back_to_unknown():
    with patch("builtins.open", side_effect=OSError("nope")):
        assert get_version() == "unknown"


def test_create_app_registers_routes(client):
    paths = {r.path for r in client.app.routes if hasattr(r, "path")}
    assert "/health" in paths
    assert "/" in paths
    assert "/estandar_aa_webhook" in paths
    assert "/estandar_pp_webhook" in paths


def test_health_endpoint_reports_env_and_version(client, monkeypatch):
    monkeypatch.setattr(config, "environment", "staging")
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["version"] == "0.1.0"
    assert body["environment"] == "staging"


def test_root_endpoint(client, monkeypatch):
    monkeypatch.setattr(config, "environment", "production")
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == "WhatsApp Webhook Service"
    assert body["status"] == "running"
    assert body["environment"] == "production"
