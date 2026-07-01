"""Tests for logging utilities (mask_pii, StructuredLogger, configuration)."""
import logging
from unittest.mock import patch

import pytest

from whatsapp_webhook.utils import logging as wlog


# --------------------------------------------------------------------------- #
# mask_pii
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("value,expected", [
    (None, "****"),
    ("", "****"),
    ("1234", "****"),        # <= 4 fully masked
    ("56912345678", "56*******78"),
    ("+56912345678", "+5********78"),
])
def test_mask_pii(value, expected):
    assert wlog.mask_pii(value) == expected


# --------------------------------------------------------------------------- #
# configure_app_logging
# --------------------------------------------------------------------------- #

def test_configure_app_logging_valid_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    log = wlog.configure_app_logging()
    assert log.name == "whatsapp_webhook"


def test_configure_app_logging_invalid_level_defaults_info(monkeypatch, capsys):
    monkeypatch.setenv("LOG_LEVEL", "NONSENSE")
    wlog.configure_app_logging()
    assert "Invalid LOG_LEVEL" in capsys.readouterr().out


def test_setup_logging_lowers_noise_libraries(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    wlog.setup_logging()
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("google").level == logging.WARNING


# --------------------------------------------------------------------------- #
# StructuredLogger
# --------------------------------------------------------------------------- #

def test_get_logger_returns_structured_logger():
    log = wlog.get_logger("mymod", {"app_name": "agent_aa"})
    assert isinstance(log, wlog.StructuredLogger)
    assert log.context == {"app_name": "agent_aa"}


def test_structured_logger_sanitizes_user_id_in_extra(caplog):
    log = wlog.get_logger("mymod")
    with caplog.at_level("INFO"):
        log.info("hi", extra={"user_id": "56912345678"})
    assert "56912345678" not in caplog.text
    # sanitized form present in the record's user_id attribute
    rec = caplog.records[-1]
    assert getattr(rec, "user_id") == "56*******78"


def test_structured_logger_short_user_id_masked():
    log = wlog.get_logger("mymod")
    assert log._sanitize_user_id("abc") == "****"
    assert log._sanitize_user_id("56912345678") == "56*******78"


def test_structured_logger_warning_and_error(caplog):
    log = wlog.get_logger("mymod")
    with caplog.at_level("WARNING"):
        log.warning("warn-msg", extra={"k": "v"})
        log.error("err-msg", exc_info=False)
    text = caplog.text
    assert "warn-msg" in text
    assert "err-msg" in text


def test_structured_logger_debug_gated_by_level(monkeypatch, caplog):
    log = wlog.get_logger("mymod")
    log.is_debug = False
    with caplog.at_level("DEBUG"):
        log.debug("should-not-appear", extra={"x": 1})
    assert "should-not-appear" not in caplog.text
    log.is_debug = True
    log.logger.setLevel(logging.DEBUG)
    with caplog.at_level("DEBUG", logger=log.logger.name):
        log.debug("should-appear")
    assert "should-appear" in caplog.text


def test_log_webhook_verification_success_and_failure(caplog):
    log = wlog.get_logger("webhook")
    with caplog.at_level("INFO"):
        log.log_webhook_verification("agent_aa", "subscribe", True, {"challenge": "1"})
        log.log_webhook_verification("agent_aa", "subscribe", False)
    assert "verification successful" in caplog.text
    assert "verification failed" in caplog.text


def test_sanitize_payload_hides_secrets():
    log = wlog.get_logger("mymod")
    out = log._sanitize_payload({"token": "abc", "keep": "me"})
    assert out["token"] == "***HIDDEN***"
    assert out["keep"] == "me"


def test_log_helpers_emit_info(caplog):
    log = wlog.get_logger("mymod")
    with caplog.at_level("INFO"):
        log.log_message_received("text", "u", "agent_aa")
        log.log_agent_request("u", "agent_aa")
        log.log_whatsapp_response("u", "agent_aa", 200)
        log.log_webhook_processing("agent_aa", "start")
        log.log_agent_session_creation("u", "agent_aa", "aa", "url")
        log.log_agent_message_request("u", "agent_aa", "aa", "url")
    assert "Message received" in caplog.text
    assert "Sending request to agent" in caplog.text
