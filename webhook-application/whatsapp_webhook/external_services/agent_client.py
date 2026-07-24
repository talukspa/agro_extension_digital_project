"""Vertex AI Agent Runtime client used by the WhatsApp webhook.

Replaces the previous httpx-based client that POSTed to {APP_URL}/run and
{APP_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}. Public
signatures are preserved so callers in messages.py don't need to change.
"""
import asyncio
import os
import time
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

# TTL (seconds) for the resolved Secret Manager resource_name cache. Keeps
# the per-message access_secret_version RPC off the hot path while staying
# responsive to deploy.py rotating the engine within one TTL window.
SECRET_TTL_SECONDS = float(os.getenv("AGENT_SECRET_TTL", "45"))

# Cache the AgentEngine handle by RESOURCE NAME, not by app_name. When
# deploy.py rewrites the Secret Manager value (a new engine has replaced
# the old one), the SM lookup returns the new resource_name and we miss
# the cache → fresh handle. Dead handles for prior resource_names linger
# in memory but cost nothing. This avoids the stale-handle outage that a
# per-app_name @lru_cache would cause after redeploy.
_engine_cache: dict[str, Any] = {}

# Short-lived cache of app_name -> (resource_name, expiry_monotonic). Avoids
# calling access_secret_version on every message while staying rotation-aware
# within SECRET_TTL_SECONDS.
_resource_name_cache: dict[str, tuple[str, float]] = {}


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


async def _resolve_resource_name(app_name: str) -> str:
    """Return the reasoningEngine resource_name for app_name.

    Served from a short TTL cache; on miss/expiry the blocking Secret Manager
    RPC runs in a worker thread so it never stalls the async event loop.
    """
    now = time.monotonic()
    cached = _resource_name_cache.get(app_name)
    if cached is not None and cached[1] > now:
        return cached[0]

    short = _short_for(app_name)
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    secret_id = f"engine-{short}-resource-name"
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    resource_name = await asyncio.to_thread(
        lambda: _sm_client()
        .access_secret_version(request={"name": name})
        .payload.data.decode()
    )
    _resource_name_cache[app_name] = (resource_name, now + SECRET_TTL_SECONDS)
    return resource_name


async def get_engine(app_name: str):
    """Resolve the reasoningEngine and return an AgentEngine handle.

    The resolved resource_name is served from a TTL cache (see
    SECRET_TTL_SECONDS) so access_secret_version does not run on every message,
    while a rotated engine is still picked up within one TTL window. The
    AgentEngine handle is cached per unique resource_name to amortize the SDK
    fetch. Both blocking RPCs run via asyncio.to_thread to keep the event loop
    free.
    """
    await asyncio.to_thread(_init)
    resource_name = await _resolve_resource_name(app_name)
    cached = _engine_cache.get(resource_name)
    if cached is None:
        cached = await asyncio.to_thread(agent_engines.get, resource_name)
        _engine_cache[resource_name] = cached
    return cached


async def create_agent_session(
    user_id: str, app_name: str, session_id: str
) -> dict[str, Any]:
    """Get-or-create a session with a deterministic id (session_id == wa_id)."""
    engine = await get_engine(app_name)
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
    engine = await get_engine(app_name)
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
                # Skip partial (incremental) streaming events: when the engine
                # streams token-by-token it emits partial events plus a final
                # cumulative one, so collecting partials would duplicate text
                # N-fold. Whether partials appear depends on the engine's
                # streaming config; guarding here is safe either way.
                if event.get("partial"):
                    continue
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
