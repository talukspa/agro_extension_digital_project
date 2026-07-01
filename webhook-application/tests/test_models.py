"""Tests for domain models and model_utils.

Exercises the live payload-parsing path (parse_webhook_payload), the message
content extraction / sender resolution used by the background processor, and the
outgoing/agent-request builders.
"""
import pytest

from whatsapp_webhook.utils import model_utils
from whatsapp_webhook.models.messages import (
    WhatsAppMessage,
    WhatsAppOutgoingMessage,
    AgentResponse,
    AgentRequestPayload,
    MessageProcessingContext,
)


def _payload(msg_type="text", **content):
    message = {"id": "wamid.1", "type": msg_type, "timestamp": "0", "from": "56912345678"}
    message.update(content)
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "e1",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{"wa_id": "56912345678"}],
                    "messages": [message],
                },
            }],
        }],
    }


def test_parse_valid_payload_extracts_messages():
    parsed = model_utils.parse_webhook_payload(_payload(text={"body": "hola"}))
    assert parsed is not None
    msgs = parsed.get_all_messages()
    assert len(msgs) == 1
    sender, msg = msgs[0]
    assert sender == "56912345678"
    assert msg.get_message_content() == "hola"
    assert msg.is_text_message() is True


def test_parse_invalid_payload_returns_none():
    # 'from' fails phone validation -> ValidationError -> None.
    bad = _payload(text={"body": "hi"})
    bad["entry"][0]["changes"][0]["value"]["messages"][0]["from"] = "not-a-phone!!"
    assert model_utils.parse_webhook_payload(bad) is None


def test_get_text_messages_filters_non_text():
    parsed = model_utils.parse_webhook_payload(
        _payload("audio", audio={"id": "A1", "voice": True})
    )
    assert parsed.get_all_messages()  # audio present
    assert parsed.get_text_messages() == []  # but not a text message


@pytest.mark.parametrize("mtype,content,expected_substr", [
    ("audio", {"audio": {"id": "A1", "voice": True}}, "Voice message"),
    ("image", {"image": {"id": "I1", "caption": "gato"}}, "Image: gato"),
    ("document", {"document": {"id": "D1", "filename": "x.pdf"}}, "x.pdf"),
    ("location", {"location": {"latitude": 1.0, "longitude": 2.0}}, "Location"),
    ("sticker", {"sticker": {"id": "S1"}}, "Sticker"),
    ("reaction", {"reaction": {"message_id": "m", "emoji": "🔥"}}, "Reaction"),
])
def test_get_message_content_variants(mtype, content, expected_substr):
    msg = WhatsAppMessage.model_validate(
        {"id": "x", "type": mtype, "timestamp": "0", "from": "56912345678", **content}
    )
    assert expected_substr in msg.get_message_content()


def test_agent_response_extract_text():
    ar = AgentResponse.model_validate({"content": {"parts": [{"text": "  hola  "}]}})
    assert ar.extract_text_response() == "hola"


def test_agent_response_no_content_returns_none():
    assert AgentResponse.model_validate({}).extract_text_response() is None
    assert AgentResponse.model_validate(
        {"content": {"parts": []}}).extract_text_response() is None


def test_parse_agent_response_from_event_list():
    events = [{"content": {"parts": [{"text": "respuesta"}]}}]
    assert model_utils.parse_agent_response(events) == "respuesta"


def test_parse_agent_response_empty_returns_none():
    assert model_utils.parse_agent_response([]) is None
    assert model_utils.parse_agent_response("nope") is None


def test_create_outgoing_text_message_normalizes_recipient():
    out = model_utils.create_outgoing_text_message("56912345678", "hola")
    assert isinstance(out, WhatsAppOutgoingMessage)
    assert out.to == "+56912345678"
    assert out.text.body == "hola"


def test_create_agent_request_builds_user_message():
    req = model_utils.create_agent_request("agent_aa", "u", "s", "hola")
    assert isinstance(req, AgentRequestPayload)
    assert req.new_message.role == "user"
    assert req.new_message.parts[0].text == "hola"


def test_create_processing_context_validates_url_and_strips_slash():
    ctx = model_utils.create_processing_context(
        "agent_aa", "56912345678", "https://graph.facebook.com/", "tok"
    )
    assert isinstance(ctx, MessageProcessingContext)
    assert ctx.whatsapp_api_url == "https://graph.facebook.com"
    assert ctx.session_id == "56912345678"  # defaults to user id


def test_processing_context_rejects_bad_url():
    with pytest.raises(Exception):
        model_utils.create_processing_context(
            "agent_aa", "56912345678", "ftp://bad", "tok"
        )
