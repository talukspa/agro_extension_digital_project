"""Tests for the GlobalGemini api_client cache.

The genai.Client is cached in a module-level dict keyed by (project, location)
and deliberately kept OFF the pydantic/Gemini instance so the engine-create
deepcopy never touches the unpicklable gRPC channel.
"""
from unittest.mock import MagicMock, patch

import core.llm_global as lg


def test_api_client_builds_once_and_caches_per_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proj-x")
    lg._CLIENT_CACHE.clear()
    with patch.object(lg.genai, "Client") as Client:
        Client.side_effect = [MagicMock(name="c1"), MagicMock(name="c2")]
        model = lg.GlobalGemini(model="gemini-3.5-flash")

        first = model.api_client
        second = model.api_client

    # One construction, same instance returned on the hot path.
    assert Client.call_count == 1
    assert first is second
    Client.assert_called_once_with(
        vertexai=True, project="proj-x", location=lg.GEMINI_LOCATION
    )
    # Cache lives in the module dict, not on the instance.
    assert lg._CLIENT_CACHE[("proj-x", lg.GEMINI_LOCATION)] is first
    assert "api_client" not in model.__dict__


def test_api_client_keys_cache_by_project(monkeypatch):
    lg._CLIENT_CACHE.clear()
    with patch.object(lg.genai, "Client") as Client:
        Client.side_effect = lambda **kw: MagicMock(name=kw["project"])
        monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proj-a")
        a = lg.GlobalGemini(model="gemini-3.5-flash").api_client
        monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proj-b")
        b = lg.GlobalGemini(model="gemini-3.5-flash").api_client

    # Distinct project -> distinct cached client.
    assert a is not b
    assert Client.call_count == 2
    assert {("proj-a", lg.GEMINI_LOCATION), ("proj-b", lg.GEMINI_LOCATION)} <= set(
        lg._CLIENT_CACHE
    )


# The AA-vs-PP parity test is retired: after this PR there is exactly one
# GlobalGemini, in core/, so asserting the two copies agree is meaningless.
