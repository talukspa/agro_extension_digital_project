"""Vertex AI Agent Runtime client used by the WhatsApp webhook.

Replaces the previous httpx-based client that POSTed to {APP_URL}/run and
{APP_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}. Public
signatures are preserved so callers in messages.py don't need to change.
"""
import asyncio
import hashlib
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
from .whatsapp_format import normalize_whatsapp_markdown

_logger = get_logger("agent_client")

# Timeouts — env-overridable for SRE tuning without code change.
SESSION_TIMEOUT_SECONDS = float(os.getenv("AGENT_SESSION_TIMEOUT", "15"))
QUERY_TIMEOUT_SECONDS = float(os.getenv("AGENT_QUERY_TIMEOUT", "90"))

# Vertex Agent Runtime sessions are eventually consistent: a create() that just
# reported "already exists" (or ran moments ago) can still be invisible to the
# very next stream_query()/get_session(). Bound the number of retries so the
# webhook absorbs that window instead of surfacing an empty response.
SESSION_RETRY_ATTEMPTS = int(os.getenv("AGENT_SESSION_RETRY_ATTEMPTS", "3"))

# Las sesiones del Agent Runtime rotan por ventana de tiempo: el session_id
# lleva la ventana adentro en vez de ser sólo el wa_id. Dos razones, en orden
# de importancia:
#
#   - Un nombre de sesión que la plataforma deja inutilizable deja de ser una
#     condena permanente para ese wa_id. El modo de falla es real y observado
#     (issue #70): el índice de unicidad se queda con el nombre tomado pero el
#     recurso es ilegible, así que `create` responde 400 "already exists" y el
#     `get` siguiente responde 404 — para siempre, porque no hay nada que vaya
#     a aparecer. Con la ventana adentro del id, eso se cura solo al rotar.
#   - Regenera el hilo cada SESSION_WINDOW_SECONDS sin estado extra.
#
# NO cambiar esto por un TTL sobre un session_id fijo: eso le PROGRAMA el
# estado de arriba a cada productor en cada vencimiento, convirtiendo un
# incidente aislado en una caída recurrente. El TTL de abajo sólo es sano
# porque el id rota y ningún nombre se reusa después de vencer.
SESSION_WINDOW_SECONDS = int(os.getenv("AGENT_SESSION_WINDOW", str(24 * 60 * 60)))

# La API rechaza con 400 cualquier ttl bajo 24h ("`ttl` must be at least 24
# hours"), y lo mismo un expire_time a menos de 24h. 6h no es expresable: la
# rotación del id es lo que da ventanas más cortas si alguna vez se quieren.
SESSION_TTL = os.getenv("AGENT_SESSION_TTL", "86400s")

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


def _is_session_already_exists(exc: Exception) -> bool:
    """True when a 400 from Agent Runtime means "this session already exists"."""
    return "already exists" in str(exc).lower()


def _is_session_not_found(exc: Exception) -> bool:
    """True when Agent Runtime means "this session doesn't exist (yet)".

    Mirrors _is_session_already_exists: string-match rather than a specific
    exception type, because the SDK/engine doesn't consistently wrap this as
    one exception class (a plain RuntimeError from async_stream_query, a
    google.api_core NotFound from async_get_session, etc).
    """
    return "session not found" in str(exc).lower()


def session_id_for(wa_id: str, user_id: str) -> str:
    """session_id determinístico por (wa_id, dueño, ventana de tiempo).

    Mismo wa_id y mismo dueño dentro de la misma ventana -> mismo id, que es lo
    que mantiene el hilo de la conversación. Al cruzar la ventana el id cambia y
    el engine abre una sesión nueva.

    El dueño va adentro del nombre a propósito. Agent Runtime rechaza un `get`
    cuyo user_id no coincide con el de la sesión ("Session does not belong to
    user"), así que dos identidades distintas no pueden compartir nombre sin
    romperse. Pasó de verdad: `process_message` cae al wa_id cuando
    resolve-identity falla, y un turno resuelto al uuid después del turno que
    cayó al teléfono encontraba la sesión del otro dueño. Con el dueño en el id
    eso es imposible por construcción, no por disciplina.

    Va un digest y no el uuid pelado para no dejar el id del productor en un
    resource name ni en los logs; 8 hex alcanzan de sobra para separar dos
    identidades del mismo teléfono.
    """
    owner = hashlib.sha256(user_id.encode()).hexdigest()[:8]
    return f"{wa_id}-{owner}-{int(time.time()) // SESSION_WINDOW_SECONDS}"


async def create_agent_session(
    user_id: str, app_name: str, session_id: str
) -> dict[str, Any]:
    """Get-or-create a session with a deterministic id (session_id == wa_id)."""
    engine = await get_engine(app_name)
    try:
        return await asyncio.wait_for(
            engine.async_create_session(
                user_id=user_id, session_id=session_id, ttl=SESSION_TTL
            ),
            timeout=SESSION_TIMEOUT_SECONDS,
        )
    except (gax.AlreadyExists, gax.InvalidArgument) as exc:
        # Agent Runtime does NOT surface a duplicate session as 409/AlreadyExists.
        # The engine wraps the session-service failure as a 400 INVALID_ARGUMENT
        # ("Reasoning Engine Execution failed"), with "already exists" only in
        # the nested message — so string-match to tell a duplicate apart from a
        # genuinely bad request, which must keep propagating. Catching
        # InvalidArgument wholesale here would silently swallow real 400s.
        if isinstance(exc, gax.InvalidArgument) and not _is_session_already_exists(exc):
            raise
        _logger.info(
            "agent_session.exists",
            extra={
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
            },
        )
        # "already exists" and "visible to a get" are not the same instant under
        # eventual consistency: a concurrent delivery of the same WhatsApp turn
        # can report AlreadyExists while async_get_session still 404s. Retry the
        # get (bounded, same backoff as send_to_agent) instead of propagating.
        for attempt in range(SESSION_RETRY_ATTEMPTS):
            try:
                return await asyncio.wait_for(
                    engine.async_get_session(user_id=user_id, session_id=session_id),
                    timeout=SESSION_TIMEOUT_SECONDS,
                )
            except Exception as get_exc:  # noqa: BLE001
                if not _is_session_not_found(get_exc):
                    raise
                if attempt >= SESSION_RETRY_ATTEMPTS - 1:
                    raise
                _logger.warning(
                    "agent_session.not_visible_yet_retry",
                    extra={
                        "app_name": app_name,
                        "user_id": user_id,
                        "session_id": session_id,
                        "attempt": attempt + 1,
                    },
                )
                await asyncio.sleep(0.3 * (attempt + 1))


def _to_stream_message(message: str | dict[str, Any]) -> str | dict[str, Any]:
    """Build the value passed as `async_stream_query(message=...)`.

    `message` is either plain text (str, as today) or a dict
    `{"text": ..., "file_uri": "gs://...", "mime_type": "..."}` produced by
    messages.handle_media_message for an image/PDF.

    Format verified against the INSTALLED vertexai/google-genai versions
    (plan Task 3 Step 0): `AdkApp.async_stream_query` (vertexai.agent_engines.
    templates.adk) accepts `message: Union[str, Dict[str, Any]]` and, when a
    dict is given, does `google.genai.types.Content.model_validate(message)`.
    So the dict must be a valid Content: `{"role": "user", "parts": [...]}`
    with parts shaped as `google.genai.types.Part` — `{"text": ...}` for text
    and `{"file_data": {"file_uri": ..., "mime_type": ...}}` for the GCS file.
    A plain str is left untouched; AdkApp itself wraps it as
    `Content(role="user", parts=[Part(text=message)])`.
    """
    if isinstance(message, str):
        return message
    parts: list[dict[str, Any]] = []
    text = message.get("text")
    if text:
        parts.append({"text": text})
    parts.append(
        {"file_data": {"file_uri": message["file_uri"], "mime_type": message["mime_type"]}}
    )
    return {"role": "user", "parts": parts}


async def send_to_agent(
    app_name: str, user_id: str, session_id: str, message: str | dict[str, Any]
) -> dict[str, Any]:
    """Stream a query to Agent Runtime, returning the concatenated assistant text.

    `message` is plain text (str) or a multimodal dict with a `file_uri` (see
    _to_stream_message) — e.g. a WhatsApp image/PDF uploaded to GCS by
    messages.handle_media_message.

    Retries (bounded, short backoff) when the stream fails with "Session not
    found": Agent Runtime sessions are eventually consistent, so the session
    create_agent_session() just ran (or reported "already exists" for) can
    still be invisible to this stream_query. Each retry re-asserts the session
    via create_agent_session before trying again. out/raw_events are cleared
    between attempts so a retry never duplicates text from the failed one.
    """
    stream_message = _to_stream_message(message)
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
    for attempt in range(SESSION_RETRY_ATTEMPTS):
        out.clear()
        raw_events.clear()
        try:
            async with asyncio.timeout(QUERY_TIMEOUT_SECONDS):
                async for event in engine.async_stream_query(
                    user_id=user_id, session_id=session_id, message=stream_message
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
            break
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
        except Exception as exc:  # noqa: BLE001
            if not _is_session_not_found(exc):
                raise
            if attempt >= SESSION_RETRY_ATTEMPTS - 1:
                _logger.error(
                    "agent_query.session_not_found_exhausted",
                    extra={
                        "app_name": app_name,
                        "user_id": user_id,
                        "session_id": session_id,
                        "attempts": SESSION_RETRY_ATTEMPTS,
                    },
                )
                return {
                    "response": "Error: la sesión del agente no está disponible, intenta de nuevo.",
                    "raw_response": raw_events,
                }
            _logger.warning(
                "agent_query.session_not_found_retry",
                extra={
                    "app_name": app_name,
                    "user_id": user_id,
                    "session_id": session_id,
                    "attempt": attempt + 1,
                },
            )
            await asyncio.sleep(0.3 * (attempt + 1))
            # Re-assert the session exists before retrying the stream.
            await create_agent_session(user_id, app_name, session_id)
    response_text = normalize_whatsapp_markdown("".join(out))
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
