"""Tests for the WhatsApp API client (send + media download).

httpx is mocked; we assert URL/payload construction, the `+` normalization of
the recipient, that the recipient is masked in logs (PII), and the media
download success + failure branches.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from whatsapp_webhook.external_services import whatsapp_client as wc


class _FakeAsyncClient:
    """Minimal async context-manager stand-in for httpx.AsyncClient."""

    def __init__(self, *, post=None, get=None):
        self._post = post
        self._get = get

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json=None, headers=None):
        return self._post(url, json, headers)

    async def get(self, url, headers=None):
        return self._get(url, headers)


def _resp(json_data, status=200):
    r = MagicMock()
    r.json.return_value = json_data
    r.raise_for_status = MagicMock()
    r.status_code = status
    return r


# --------------------------------------------------------------------------- #
# Message builders
# --------------------------------------------------------------------------- #

def test_create_text_message_structure():
    msg = wc.create_text_message("hola", preview_url=True)
    assert msg == {"type": "text", "text": {"body": "hola", "preview_url": True}}


def test_create_image_message_with_and_without_caption():
    assert wc.create_image_message("m1") == {"type": "image", "image": {"id": "m1"}}
    withcap = wc.create_image_message("m1", "cap")
    assert withcap["image"]["caption"] == "cap"


def test_create_document_message():
    doc = wc.create_document_message("m1", "file.pdf", "cap")
    assert doc["document"] == {"id": "m1", "filename": "file.pdf", "caption": "cap"}


# --------------------------------------------------------------------------- #
# send_whatsapp_message
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_send_message_builds_payload_and_normalizes_recipient():
    captured = {}

    def _post(url, json, headers):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _resp({"messages": [{"id": "wamid.out"}]})

    with patch.object(wc.httpx, "AsyncClient", lambda timeout=None: _FakeAsyncClient(post=_post)):
        result = await wc.send_whatsapp_message(
            "56912345678", wc.create_text_message("hi"),
            "https://graph.facebook.com/v22.0/PHONE/messages", "TOKEN",
        )

    assert result == {"messages": [{"id": "wamid.out"}]}
    assert captured["url"].endswith("/messages")
    # Recipient normalized to E.164 with leading '+'.
    assert captured["json"]["to"] == "+56912345678"
    assert captured["json"]["messaging_product"] == "whatsapp"
    assert captured["json"]["type"] == "text"
    assert captured["headers"]["Authorization"] == "Bearer TOKEN"


@pytest.mark.asyncio
async def test_send_message_masks_recipient_in_logs(caplog):
    def _post(url, json, headers):
        return _resp({"ok": True})

    with patch.object(wc.httpx, "AsyncClient", lambda timeout=None: _FakeAsyncClient(post=_post)), \
         caplog.at_level("INFO"):
        await wc.send_whatsapp_message(
            "56912345678", wc.create_text_message("hi"), "https://x/messages", "T"
        )
    assert "56912345678" not in caplog.text
    assert "+5********78" in caplog.text or "56*******78" in caplog.text


@pytest.mark.asyncio
async def test_send_message_raises_on_http_error():
    def _post(url, json, headers):
        r = MagicMock()
        r.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
            "boom", request=MagicMock(), response=MagicMock()))
        return r

    with patch.object(wc.httpx, "AsyncClient", lambda timeout=None: _FakeAsyncClient(post=_post)):
        with pytest.raises(httpx.HTTPStatusError):
            await wc.send_whatsapp_message("56912345678", {"type": "text"}, "https://x", "T")


# --------------------------------------------------------------------------- #
# download_whatsapp_media
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_download_media_success():
    calls = []

    def _get(url, headers=None):
        calls.append(url)
        if len(calls) == 1:
            return _resp({"url": "https://cdn.example/media/xyz"})
        r = MagicMock()
        r.raise_for_status = MagicMock()
        r.content = b"AUDIODATA"
        return r

    with patch.object(wc.httpx, "AsyncClient", lambda timeout=None: _FakeAsyncClient(get=_get)):
        out = await wc.download_whatsapp_media("MID", "https://graph.facebook.com/v22.0", "T")
    assert out == b"AUDIODATA"
    # First call resolves the media metadata endpoint by id.
    assert calls[0] == "https://graph.facebook.com/v22.0/MID"
    assert calls[1] == "https://cdn.example/media/xyz"


@pytest.mark.asyncio
async def test_download_media_missing_url_returns_none():
    def _get(url, headers=None):
        return _resp({"no_url": True})

    with patch.object(wc.httpx, "AsyncClient", lambda timeout=None: _FakeAsyncClient(get=_get)):
        out = await wc.download_whatsapp_media("MID", "https://base", "T")
    assert out is None


@pytest.mark.asyncio
async def test_download_media_http_error_returns_none():
    def _get(url, headers=None):
        r = MagicMock()
        resp = MagicMock()
        resp.status_code = 404
        resp.text = "not found"
        r.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
            "boom", request=MagicMock(), response=resp))
        return r

    with patch.object(wc.httpx, "AsyncClient", lambda timeout=None: _FakeAsyncClient(get=_get)):
        out = await wc.download_whatsapp_media("MID", "https://base", "T")
    assert out is None


@pytest.mark.asyncio
async def test_download_media_generic_error_returns_none():
    def _get(url, headers=None):
        raise RuntimeError("boom")

    with patch.object(wc.httpx, "AsyncClient", lambda timeout=None: _FakeAsyncClient(get=_get)):
        out = await wc.download_whatsapp_media("MID", "https://base", "T")
    assert out is None
