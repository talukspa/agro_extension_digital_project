"""Tests for the WhatsApp webhook FastAPI router.

Covers the security-critical X-Hub-Signature-256 validation on POST and the
Meta GET subscription verification handshake. All background work is stubbed so
these tests exercise ONLY the router/security logic, deterministically.
"""
import hashlib
import hmac
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from whatsapp_webhook.app import create_app
from whatsapp_webhook.utils.app_config import config

APP_SECRET = "meta-app-secret"
VERIFY_TOKEN = "test-verify-token"  # matches conftest seed


@pytest.fixture
def client():
    return TestClient(create_app())


@pytest.fixture(autouse=True)
def _secret(monkeypatch):
    """Configure a known app secret + verify token on the config singleton."""
    monkeypatch.setattr(config, "app_secret", APP_SECRET)
    monkeypatch.setattr(config, "verify_token", VERIFY_TOKEN)


def _sign(body: bytes, secret: str = APP_SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


# --------------------------------------------------------------------------- #
# POST signature validation
# --------------------------------------------------------------------------- #

def test_valid_signature_returns_200_and_schedules_handler(client):
    body = json.dumps({"object": "whatsapp_business_account", "entry": []}).encode()
    handler = AsyncMock(return_value=True)
    with patch("whatsapp_webhook.api.webhooks.receive_message_aa", handler):
        resp = client.post(
            "/estandar_aa_webhook",
            content=body,
            headers={"X-Hub-Signature-256": _sign(body)},
        )
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    # Background handler was invoked with the parsed body.
    handler.assert_awaited_once()
    assert handler.await_args.args[0] == {"object": "whatsapp_business_account", "entry": []}


def test_bad_signature_returns_403(client):
    body = b'{"entry": []}'
    resp = client.post(
        "/estandar_aa_webhook",
        content=body,
        headers={"X-Hub-Signature-256": "sha256=deadbeef"},
    )
    assert resp.status_code == 403


def test_missing_signature_header_returns_403(client):
    body = b'{"entry": []}'
    resp = client.post("/estandar_aa_webhook", content=body)
    assert resp.status_code == 403


def test_signature_over_wrong_secret_returns_403(client):
    body = b'{"entry": []}'
    resp = client.post(
        "/estandar_aa_webhook",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body, "attacker-secret")},
    )
    assert resp.status_code == 403


def test_app_secret_unset_fails_closed_403(client, monkeypatch):
    """No configured app secret must reject every POST (fail-closed)."""
    monkeypatch.setattr(config, "app_secret", None)
    body = b'{"entry": []}'
    # Even a 'correct-looking' header cannot pass without a configured secret.
    resp = client.post(
        "/estandar_aa_webhook",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body)},
    )
    assert resp.status_code == 403


def test_valid_signature_but_invalid_json_returns_400(client):
    body = b"not-json"
    resp = client.post(
        "/estandar_aa_webhook",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body)},
    )
    assert resp.status_code == 400


def test_handler_exception_still_returns_200(client):
    """WhatsApp must never see a 5xx once the signature is valid (no retries)."""
    body = b'{"entry": []}'
    handler = AsyncMock(side_effect=RuntimeError("boom"))
    with patch("whatsapp_webhook.api.webhooks.receive_message_aa", handler):
        resp = client.post(
            "/estandar_aa_webhook",
            content=body,
            headers={"X-Hub-Signature-256": _sign(body)},
        )
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_pp_endpoint_uses_pp_handler(client):
    body = b'{"entry": []}'
    handler = AsyncMock(return_value=True)
    with patch("whatsapp_webhook.api.webhooks.receive_message_pp", handler):
        resp = client.post(
            "/estandar_pp_webhook",
            content=body,
            headers={"X-Hub-Signature-256": _sign(body)},
        )
    assert resp.status_code == 200
    handler.assert_awaited_once()


# --------------------------------------------------------------------------- #
# GET verification handshake
# --------------------------------------------------------------------------- #

def test_get_verify_correct_token_echoes_challenge(client):
    resp = client.get(
        "/estandar_aa_webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "1234567890",
        },
    )
    assert resp.status_code == 200
    assert resp.text == "1234567890"
    assert resp.headers["content-type"].startswith("text/plain")


def test_get_verify_wrong_token_returns_403(client):
    resp = client.get(
        "/estandar_aa_webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "1234567890",
        },
    )
    assert resp.status_code == 403


def test_get_verify_non_digit_challenge_returns_400(client):
    resp = client.get(
        "/estandar_aa_webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "not-a-number",
        },
    )
    assert resp.status_code == 400


def test_get_verify_wrong_mode_returns_403(client):
    resp = client.get(
        "/estandar_pp_webhook",
        params={
            "hub.mode": "unsubscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "1234567890",
        },
    )
    assert resp.status_code == 403
