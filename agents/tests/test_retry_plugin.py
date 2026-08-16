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


# --- F2: exceeding the retry cap must NOT raise -----------------------------

async def test_exceeding_max_retries_returns_guidance_instead_of_raising():
    """ADK defaults throw_exception_if_retry_exceeded=True, which would break
    the 'tools never raise into the model' contract core/bq_tools.py rests on.
    build_app must pass False — this pins the behaviour end to end."""
    from unittest.mock import MagicMock

    plugin = OkContractRetryPlugin(
        max_retries=2, throw_exception_if_retry_exceeded=False
    )
    tool = MagicMock()
    tool.name = "run_query"
    ctx = MagicMock()
    ctx.invocation_id = "inv-f2"

    outs = []
    for _ in range(4):  # two retries, then two past the cap
        outs.append(
            await plugin.after_tool_callback(
                tool=tool,
                tool_args={"sql": "SELECT 1"},
                tool_context=ctx,
                result={"ok": False, "error": "bad column x"},
            )
        )
    assert all(isinstance(o, dict) for o in outs), "plugin raised past the cap"


def test_build_app_disables_the_raise_on_exceeded():
    from core.agent import build_app

    app = build_app(
        name="aa_agent",
        display_name="Adecuación Agroindustrial",
        main_datastore_env="DATASTORE_AA_ID",
    )
    plugin = app._tmpl_attrs["plugins"][0]
    assert isinstance(plugin, OkContractRetryPlugin)
    assert plugin.throw_exception_if_retry_exceeded is False
