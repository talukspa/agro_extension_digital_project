"""Tests for message orchestration (whatsapp_webhook.messages).

Focus: audio path (incl. the error-ack regression that used to raise NameError),
text path, the fire-and-forget background task + done-callback error logging, and
PII masking of the wa_id in acknowledgment logs.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from whatsapp_webhook import messages
from whatsapp_webhook.models.messages import WhatsAppMessage
from whatsapp_webhook.utils.app_config import config

AA = config.aa_app_name  # "agent_aa"
WA_ID = "56912345678"


def _text_msg(body="hola"):
    return WhatsAppMessage.model_validate(
        {"id": "wamid.1", "type": "text", "timestamp": "0", "from": WA_ID,
         "text": {"body": body}}
    )


def _audio_msg(audio_id="AUDIO123"):
    return WhatsAppMessage.model_validate(
        {"id": "wamid.2", "type": "audio", "timestamp": "0", "from": WA_ID,
         "audio": {"id": audio_id, "voice": True}}
    )


@pytest.fixture(autouse=True)
def _wsp(monkeypatch):
    # Ensure the WhatsApp config used by the audio/ack paths is populated.
    # AA and PP have distinct outbound tokens.
    monkeypatch.setattr(config, "aa_wsp_token", "test-wsp-token-aa")
    monkeypatch.setattr(config, "pp_wsp_token", "test-wsp-token-pp")


# --------------------------------------------------------------------------- #
# Routing
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_text_message_routes_to_agent_and_acks():
    with patch.object(messages, "create_agent_session", AsyncMock()) as sess, \
         patch.object(messages, "send_to_agent",
                      AsyncMock(return_value={"response": "respuesta agente"})), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.process_message(WA_ID, _text_msg(), AA)

    sess.assert_awaited_once()
    send.assert_awaited_once()
    # The agent's response is what gets sent back to the user.
    sent_payload = send.await_args.args[1]
    assert sent_payload["text"]["body"] == "respuesta agente"


@pytest.mark.asyncio
async def test_audio_message_routes_to_handle_audio():
    with patch.object(messages, "create_agent_session", AsyncMock()), \
         patch.object(messages, "handle_audio_message", AsyncMock()) as h:
        await messages.process_message(WA_ID, _audio_msg("A1"), AA)
    h.assert_awaited_once_with(WA_ID, "A1", AA)


@pytest.mark.asyncio
async def test_unsupported_type_sends_fallback_ack():
    msg = WhatsAppMessage.model_validate(
        {"id": "wamid.3", "type": "image", "timestamp": "0", "from": WA_ID,
         "image": {"id": "IMG"}}
    )
    with patch.object(messages, "create_agent_session", AsyncMock()), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.process_message(WA_ID, msg, AA)
    send.assert_awaited_once()
    assert "texto y audio" in send.await_args.args[1]["text"]["body"]


# --------------------------------------------------------------------------- #
# Audio happy path + error regression
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_handle_audio_happy_path_transcribes_and_replies():
    with patch.object(messages, "download_whatsapp_media",
                      AsyncMock(return_value=b"oggbytes")), \
         patch.object(messages, "transcribe_audio_file",
                      AsyncMock(return_value="hola mundo")), \
         patch.object(messages, "send_message_to_agent",
                      AsyncMock(return_value="respuesta")) as agent, \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.handle_audio_message(WA_ID, "A1", AA)

    agent.assert_awaited_once_with(WA_ID, AA, WA_ID, "hola mundo")
    send.assert_awaited_once()
    assert send.await_args.args[1]["text"]["body"] == "respuesta"


@pytest.mark.asyncio
async def test_handle_audio_download_failure_sends_error_ack():
    with patch.object(messages, "download_whatsapp_media",
                      AsyncMock(return_value=None)), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.handle_audio_message(WA_ID, "A1", AA)
    send.assert_awaited_once()
    assert "descargar" in send.await_args.args[1]["text"]["body"]


@pytest.mark.asyncio
async def test_handle_audio_empty_transcript_sends_error_ack():
    with patch.object(messages, "download_whatsapp_media",
                      AsyncMock(return_value=b"oggbytes")), \
         patch.object(messages, "transcribe_audio_file",
                      AsyncMock(return_value=None)), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.handle_audio_message(WA_ID, "A1", AA)
    send.assert_awaited_once()
    assert "entender" in send.await_args.args[1]["text"]["body"]


@pytest.mark.asyncio
async def test_handle_audio_exception_path_sends_error_ack_no_nameerror():
    """Regression: the except branch references facebook_app_url — it must be
    in scope so we send the audio-error ack instead of raising NameError."""
    with patch.object(messages, "download_whatsapp_media",
                      AsyncMock(side_effect=RuntimeError("network"))), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        # Must NOT raise.
        await messages.handle_audio_message(WA_ID, "A1", AA)
    send.assert_awaited_once()
    assert "Error procesando tu audio" in send.await_args.args[1]["text"]["body"]


@pytest.mark.asyncio
async def test_handle_audio_unknown_app_name_short_circuits():
    with patch.object(messages, "download_whatsapp_media", AsyncMock()) as dl:
        await messages.handle_audio_message(WA_ID, "A1", "agent_unknown")
    dl.assert_not_awaited()


# --------------------------------------------------------------------------- #
# send_message_to_agent error handling
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_send_message_to_agent_value_error_returns_config_message():
    with patch.object(messages, "send_to_agent", AsyncMock(side_effect=ValueError("x"))):
        out = await messages.send_message_to_agent(WA_ID, AA, WA_ID, "hi")
    assert "no configurado" in out


@pytest.mark.asyncio
async def test_send_message_to_agent_generic_error_returns_comm_message():
    with patch.object(messages, "send_to_agent", AsyncMock(side_effect=RuntimeError("x"))):
        out = await messages.send_message_to_agent(WA_ID, AA, WA_ID, "hi")
    assert "comunicación" in out.lower()


# --------------------------------------------------------------------------- #
# Acknowledgment / PII masking
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_ack_masks_wa_id_in_logs(caplog):
    with patch.object(messages, "send_whatsapp_message", AsyncMock()), \
         caplog.at_level("INFO"):
        ok = await messages._send_whatsapp_acknowledgment(WA_ID, "hola", AA)
    assert ok is True
    # The raw wa_id must never appear verbatim; a masked form should.
    assert WA_ID not in caplog.text
    assert "56*******78" in caplog.text


@pytest.mark.asyncio
async def test_ack_unknown_app_returns_false():
    ok = await messages._send_whatsapp_acknowledgment(WA_ID, "hola", "agent_unknown")
    assert ok is False


@pytest.mark.asyncio
async def test_ack_uses_per_app_token():
    """AA and PP are separate WABAs: each app's outbound send must use its own
    access token (a shared token 401s against the other app's number)."""
    PP = config.pp_app_name
    with patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages._send_whatsapp_acknowledgment(WA_ID, "hola", AA)
        await messages._send_whatsapp_acknowledgment(WA_ID, "hola", PP)
    aa_call, pp_call = send.await_args_list
    # send_whatsapp_message(to, message, url, token) — token is arg 3.
    assert aa_call.args[3] == "test-wsp-token-aa"
    assert aa_call.args[2].startswith(config.aa_facebook_app_url)
    assert pp_call.args[3] == "test-wsp-token-pp"
    assert pp_call.args[2].startswith(config.pp_facebook_app_url)


@pytest.mark.asyncio
async def test_ack_missing_app_token_returns_false_without_sending(monkeypatch):
    """When the app's token is unset the send is skipped (fail-closed), not
    attempted with a wrong/empty token."""
    monkeypatch.setattr(config, "aa_wsp_token", None)
    with patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        ok = await messages._send_whatsapp_acknowledgment(WA_ID, "hola", AA)
    assert ok is False
    send.assert_not_awaited()


# --------------------------------------------------------------------------- #
# Fire-and-forget background task + done callback
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_process_incoming_schedules_background_task():
    with patch.object(messages, "_process_webhook_in_background", AsyncMock()) as bg:
        result = await messages.receive_message_aa({"entry": []})
        # Give the scheduled task a chance to run.
        await asyncio.sleep(0)
    assert result is True
    bg.assert_awaited_once()


@pytest.mark.asyncio
async def test_background_task_exception_is_logged_via_done_callback(caplog):
    """A crash in background processing must be surfaced by the done-callback,
    not swallowed silently."""
    async def _boom(body, app_name):
        raise RuntimeError("kaboom")

    with patch.object(messages, "_process_webhook_in_background", _boom), \
         caplog.at_level("ERROR"):
        await messages.process_incoming_webhook_payload({"entry": []}, AA)
        # Let the task run and its done-callback fire.
        await asyncio.sleep(0)
        await asyncio.sleep(0)

    assert "Background webhook processing failed" in caplog.text
    # The done-callback must discard the finished task from the retention set.
    assert len(messages._background_tasks) == 0


@pytest.mark.asyncio
async def test_cancelled_background_task_does_not_raise_in_callback(caplog):
    """Cancellation (e.g. Cloud Run evicting the worker) is not a processing
    failure: the done-callback must skip it, not call t.exception() and let a
    CancelledError escape into asyncio's 'Exception in callback' handler."""
    started = asyncio.Event()

    async def _hang(body, app_name):
        started.set()
        await asyncio.Event().wait()  # never completes until cancelled

    with patch.object(messages, "_process_webhook_in_background", _hang), \
         caplog.at_level("ERROR"):
        await messages.process_incoming_webhook_payload({"entry": []}, AA)
        await started.wait()
        (task,) = tuple(messages._background_tasks)
        task.cancel()
        # Let cancellation propagate and the done-callback settle.
        for _ in range(4):
            await asyncio.sleep(0)

    assert "Exception in callback" not in caplog.text
    assert "CancelledError" not in caplog.text
    assert "Background webhook processing failed" not in caplog.text
    # The callback still discards the task from the retention set.
    assert len(messages._background_tasks) == 0


@pytest.mark.asyncio
async def test_process_webhook_in_background_parses_and_dispatches():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "e1",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{"wa_id": WA_ID}],
                    "messages": [{"id": "wamid.1", "type": "text",
                                  "timestamp": "0", "from": WA_ID,
                                  "text": {"body": "hola"}}],
                },
            }],
        }],
    }
    with patch.object(messages, "process_message", AsyncMock()) as pm:
        await messages._process_webhook_in_background(payload, AA)
    pm.assert_awaited_once()
    assert pm.await_args.args[0] == WA_ID


@pytest.mark.asyncio
async def test_process_webhook_in_background_invalid_payload_returns_early():
    with patch.object(messages, "parse_webhook_payload", return_value=None), \
         patch.object(messages, "process_message", AsyncMock()) as pm:
        await messages._process_webhook_in_background({"garbage": True}, AA)
    pm.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_webhook_in_background_message_error_sends_ack():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "e1",
            "changes": [{
                "field": "messages",
                "value": {
                    "contacts": [{"wa_id": WA_ID}],
                    "messages": [{"id": "wamid.1", "type": "text",
                                  "timestamp": "0", "from": WA_ID,
                                  "text": {"body": "hola"}}],
                },
            }],
        }],
    }
    with patch.object(messages, "process_message",
                      AsyncMock(side_effect=RuntimeError("x"))), \
         patch.object(messages, "_send_whatsapp_acknowledgment",
                      AsyncMock()) as ack:
        await messages._process_webhook_in_background(payload, AA)
    ack.assert_awaited_once()
    assert "Error procesando mensaje" in ack.await_args.args[1]
