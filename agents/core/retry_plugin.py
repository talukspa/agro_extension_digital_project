"""Bridge ADK 2.x's reflect-and-retry plugin to our {ok, error} tool contract.

`core/bq_tools.py` deliberately never raises into the model: every tool returns
`{"ok": bool, "error": str | None, ...}` so the LlmAgent can read the error and
fix its SQL. That contract has one consequence under ADK 2.x that is easy to
miss:

`ReflectAndRetryToolPlugin` decides a tool failed in two ways —
`on_tool_error_callback` when the tool *raises*, and `extract_error_from_result`
when the tool *returns* something error-shaped. The base
`extract_error_from_result` returns None (verified in adk 2.7.0 source), i.e. it
detects nothing by default. So a tool that catches its exception and returns
`{"ok": False}` reads as a SUCCESS: the plugin resets the failure counter and no
reflection guidance is ever produced.

This subclass teaches it our contract. Without it, adopting the plugin would be
a silent no-op for every BigQuery tool — which is the concrete form of the
"broad excepts defeat 2.0's retry" concern raised in the #44 review.
"""
from typing import Any, Optional

from google.adk.plugins import ReflectAndRetryToolPlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


class OkContractRetryPlugin(ReflectAndRetryToolPlugin):
    """Treats `{"ok": False, "error": ...}` as a failure worth reflecting on."""

    async def extract_error_from_result(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
        result: Any,
    ) -> Optional[dict[str, Any]]:
        if isinstance(result, dict) and result.get("ok") is False:
            return {
                "tool": tool.name,
                "error": result.get("error") or "tool reported ok=False",
            }
        return None
