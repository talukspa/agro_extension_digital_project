"""Vertex AI Agent Runtime client used by the WhatsApp webhook.

Replaces the previous httpx-based client that POSTed to {APP_URL}/run and
{APP_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}. Public
signatures are preserved so callers in messages.py don't need to change.
"""
import logging
import os
from functools import lru_cache
from typing import Any

import vertexai
from google.api_core import exceptions as gax
from google.cloud import secretmanager
from vertexai import agent_engines


@lru_cache(maxsize=1)
def _init() -> None:
    vertexai.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
    )


@lru_cache(maxsize=2)
def get_engine(app_name: str):
    """Resolve the reasoningEngine resource name from Secret Manager and cache the client.

    `app_name` is the existing aa/pp key from app_config (e.g. config.aa_app_name).
    """
    _init()
    short = "aa" if "aa" in app_name.lower() else "pp"
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    secret_id = f"engine-{short}-resource-name"
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    sm = secretmanager.SecretManagerServiceClient()
    resource_name = sm.access_secret_version(request={"name": name}).payload.data.decode()
    return agent_engines.get(resource_name)


async def create_agent_session(
    user_id: str, app_name: str, session_id: str
) -> dict[str, Any]:
    """Get-or-create a session with a deterministic id (session_id == wa_id)."""
    engine = get_engine(app_name)
    try:
        return await engine.async_create_session(
            user_id=user_id, session_id=session_id
        )
    except gax.AlreadyExists:
        logging.info(
            "Session %s already exists for user %s on %s",
            session_id, user_id, app_name,
        )
        return await engine.async_get_session(
            user_id=user_id, session_id=session_id
        )


async def send_to_agent(
    app_name: str, user_id: str, session_id: str, message: str
) -> dict[str, Any]:
    """Stream a query to Agent Runtime, returning the concatenated assistant text."""
    engine = get_engine(app_name)
    logging.info(f"Sending message to agent {app_name} for user {user_id}")
    out: list[str] = []
    raw_events: list[dict] = []
    async for event in engine.async_stream_query(
        user_id=user_id, session_id=session_id, message=message
    ):
        raw_events.append(event)
        # event["content"]["parts"][i] is either {"text": ...} (assistant token)
        # or {"function_call": ...} / {"function_response": ...} (tool events).
        # The `if text:` guard naturally skips tool-call parts.
        content = event.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if text:
                out.append(text)
    response_text = "".join(out).strip()
    if not response_text:
        logging.warning(
            f"Empty response from agent {app_name}: {len(raw_events)} events"
        )
        return {
            "response": "Error: Could not extract text from agent response.",
            "raw_response": raw_events,
        }
    return {"response": response_text, "raw_response": raw_events}
