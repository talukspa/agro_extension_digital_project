"""The {ok,error} contract must reach ADK 2.x's reflect-and-retry plugin.

Regression guard: the base ReflectAndRetryToolPlugin.extract_error_from_result
returns None, so without OkContractRetryPlugin every bq_tools failure would be
recorded as a SUCCESS and never retried.
"""
from unittest.mock import MagicMock

import pytest
from google.adk.plugins import ReflectAndRetryToolPlugin

from core.retry_plugin import OkContractRetryPlugin


def _call(plugin, result):
    tool = MagicMock()
    tool.name = "run_query"
    return plugin.extract_error_from_result(
        tool=tool, tool_args={}, tool_context=MagicMock(), result=result
    )


async def test_ok_false_is_reported_as_an_error():
    err = await _call(OkContractRetryPlugin(), {"ok": False, "error": "bad column x"})
    assert err is not None
    assert err["error"] == "bad column x"
    assert err["tool"] == "run_query"


async def test_ok_false_without_message_still_reports():
    err = await _call(OkContractRetryPlugin(), {"ok": False, "error": None})
    assert err is not None
    assert "ok=False" in err["error"]


async def test_ok_true_is_not_an_error():
    assert await _call(OkContractRetryPlugin(), {"ok": True, "rows": []}) is None


@pytest.mark.parametrize("result", ["a string", None, 42, {"no_ok_key": 1}])
async def test_non_contract_results_are_ignored(result):
    assert await _call(OkContractRetryPlugin(), result) is None


async def test_base_plugin_would_have_missed_it():
    """Pins the upstream behaviour this subclass exists to correct."""
    assert await _call(ReflectAndRetryToolPlugin(), {"ok": False, "error": "x"}) is None
