"""Vertex AI Agent Runtime client used by the WhatsApp webhook.

Replaces the previous httpx-based client that POSTed to {APP_URL}/run and
{APP_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}. Public
signatures are preserved so callers in messages.py don't need to change.
"""
import asyncio
import os
from functools import lru_cache
from typing import Any

import vertexai
from google.api_core import exceptions as gax
from google.cloud import secretmanager
from vertexai import agent_engines

from ..utils.app_config import config
from ..utils.logging import get_logger

_logger = get_logger("agent_client")

# Timeouts — env-overridable for SRE tuning without code change.
SESSION_TIMEOUT_SECONDS = float(os.getenv("AGENT_SESSION_TIMEOUT", "15"))
QUERY_TIMEOUT_SECONDS = float(os.getenv("AGENT_QUERY_TIMEOUT", "90"))

# Cache the AgentEngine handle by RESOURCE NAME, not by app_name. When
# deploy.py rewrites the Secret Manager value (a new engine has replaced
# the old one), the SM lookup returns the new resource_name and we miss
# the cache → fresh handle. Dead handles for prior resource_names linger
# in memory but cost nothing. This avoids the stale-handle outage that a
# per-app_name @lru_cache would cause after redeploy.
_engine_cache: dict[str, Any] = {}


@lru_cache(maxsize=1)
def _init() -> None:
    vertexai.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
    )


@lru_cache(maxsize=1)
def _sm_client() -> secretmanager.SecretManagerServiceClient:
    """One Secret Manager client reused across messages.

    get_engine() runs on the per-message hot path (twice per turn); building a
    fresh client there opens a new gRPC channel + ADC handshake each time.
    """
    return secretmanager.SecretManagerServiceClient()


def _short_for(app_name: str) -> str:
    """Map app_name to the 'aa' / 'pp' Secret Manager key suffix.

    Fails loud on unknown values rather than silently routing to PP, which
    a substring fallback used to do.
    """
    if app_name == config.aa_app_name:
        return "aa"
    if app_name == config.pp_app_name:
        return "pp"
    raise ValueError(
        f"Unknown agent app_name: {app_name!r}. Expected one of "
        f"{config.aa_app_name!r}, {config.pp_app_name!r}."
    )


def get_engine(app_name: str):
    """Resolve the reasoningEngine and return an AgentEngine handle.

    Reads the resource name from Secret Manager on every call (the secret
    rotates whenever deploy.py creates/updates an engine), but caches the
    AgentEngine handle per unique resource_name to amortize the SDK fetch.
    """
    _init()
    short = _short_for(app_name)
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    secret_id = f"engine-{short}-resource-name"
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    resource_name = (
        _sm_client().access_secret_version(request={"name": name}).payload.data.decode()
    )
    cached = _engine_cache.get(resource_name)
    if cached is None:
        cached = agent_engines.get(resource_name)
        _engine_cache[resource_name] = cached
    return cached


async def create_agent_session(
    user_id: str, app_name: str, session_id: str
) -> dict[str, Any]:
    """Get-or-create a session with a deterministic id (session_id == wa_id)."""
    engine = get_engine(app_name)
    try:
        return await asyncio.wait_for(
            engine.async_create_session(user_id=user_id, session_id=session_id),
            timeout=SESSION_TIMEOUT_SECONDS,
        )
    except gax.AlreadyExists:
        _logger.info(
            "agent_session.exists",
            extra={
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
            },
        )
        return await asyncio.wait_for(
            engine.async_get_session(user_id=user_id, session_id=session_id),
            timeout=SESSION_TIMEOUT_SECONDS,
        )


async def send_to_agent(
    app_name: str, user_id: str, session_id: str, message: str
) -> dict[str, Any]:
    """Stream a query to Agent Runtime, returning the concatenated assistant text."""
    engine = get_engine(app_name)
    _logger.info(
        "agent_query.start",
        extra={
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
        },
    )
    out: list[str] = []
    raw_events: list[dict] = []
    try:
        async with asyncio.timeout(QUERY_TIMEOUT_SECONDS):
            async for event in engine.async_stream_query(
                user_id=user_id, session_id=session_id, message=message
            ):
                raw_events.append(event)
                # event["content"]["parts"][i] is either {"text": ...} (assistant
                # token) or {"function_call": ...} / {"function_response": ...}
                # (tool events). The `if text:` guard skips tool-call parts.
                content = event.get("content") or {}
                for part in content.get("parts") or []:
                    text = part.get("text")
                    if text:
                        out.append(text)
    except TimeoutError:
        _logger.error(
            "agent_query.timeout",
            extra={
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
                "timeout_s": QUERY_TIMEOUT_SECONDS,
                "events_received": len(raw_events),
            },
        )
        return {
            "response": "Error: el agente excedió el tiempo de respuesta.",
            "raw_response": raw_events,
        }
    response_text = "".join(out).strip()
    if not response_text:
        _logger.warning(
            "agent_query.empty_response",
            extra={
                "app_name": app_name,
                "user_id": user_id,
                "events_received": len(raw_events),
            },
        )
        return {
            "response": "Error: Could not extract text from agent response.",
            "raw_response": raw_events,
        }
    _logger.info(
        "agent_query.complete",
        extra={
            "app_name": app_name,
            "user_id": user_id,
            "events_received": len(raw_events),
            "response_chars": len(response_text),
        },
    )
    return {"response": response_text, "raw_response": raw_events}
