"""Unit tests for the rewritten Vertex AI Agent Runtime client.

Tests are async (pytest-asyncio is already configured in pyproject.toml).
All network calls are stubbed via mocks — no GCP creds required.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.api_core import exceptions as gax


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    # Reset the init cache and the per-resource-name engine dict so each test
    # gets a clean slate.
    from whatsapp_webhook.external_services import agent_client
    agent_client._init.cache_clear()
    agent_client._sm_client.cache_clear()
    agent_client._engine_cache.clear()
    agent_client._resource_name_cache.clear()


@pytest.mark.asyncio
async def test_create_agent_session_returns_existing_on_already_exists():
    """get_or_create semantics: AlreadyExists -> async_get_session is called."""
    from whatsapp_webhook.external_services import agent_client

    engine = MagicMock()
    engine.async_create_session = AsyncMock(side_effect=gax.AlreadyExists("dup"))
    engine.async_get_session = AsyncMock(return_value={"id": "+56999", "events": []})
    with patch.object(agent_client, "get_engine", return_value=engine):
        out = await agent_client.create_agent_session(
            user_id="+56999", app_name="agent_aa", session_id="+56999",
        )
    assert out["id"] == "+56999"
    engine.async_get_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_agent_session_returns_existing_on_invalid_argument_already_exists():
    """Agent Runtime reports a duplicate session as 400 INVALID_ARGUMENT, not 409.

    The engine wraps the session-service error as "Reasoning Engine Execution
    failed" and only the nested message says "already exists", so catching
    gax.AlreadyExists alone lets the duplicate escape and kills every message
    from a returning user (session_id == wa_id is deterministic).
    """
    from whatsapp_webhook.external_services import agent_client

    engine = MagicMock()
    engine.async_create_session = AsyncMock(
        side_effect=gax.InvalidArgument(
            "400 Reasoning Engine Execution failed. Exception: 400 "
            "INVALID_ARGUMENT. {'error': {'code': 400, 'message': \"Session "
            "with user-provided ID 'projects/1/locations/us-central1/"
            "reasoningEngines/2/sessions/56999' already exists.\", 'status': "
            "'INVALID_ARGUMENT'}}"
        )
    )
    engine.async_get_session = AsyncMock(return_value={"id": "+56999", "events": []})
    with patch.object(agent_client, "get_engine", return_value=engine):
        out = await agent_client.create_agent_session(
            user_id="+56999", app_name="agent_aa", session_id="+56999",
        )
    assert out["id"] == "+56999"
    engine.async_get_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_agent_session_propagates_unrelated_invalid_argument():
    """A 400 that is NOT a duplicate session must still surface, not be swallowed."""
    from whatsapp_webhook.external_services import agent_client

    engine = MagicMock()
    engine.async_create_session = AsyncMock(
        side_effect=gax.InvalidArgument("400 user_id must not be empty")
    )
    engine.async_get_session = AsyncMock()
    with patch.object(agent_client, "get_engine", return_value=engine):
        with pytest.raises(gax.InvalidArgument):
            await agent_client.create_agent_session(
                user_id="", app_name="agent_aa", session_id="+56999",
            )
    engine.async_get_session.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_agent_session_returns_new_when_absent():
    from whatsapp_webhook.external_services import agent_client

    engine = MagicMock()
    engine.async_create_session = AsyncMock(return_value={"id": "+56999"})
    with patch.object(agent_client, "get_engine", return_value=engine):
        out = await agent_client.create_agent_session(
            user_id="+56999", app_name="agent_aa", session_id="+56999",
        )
    assert out["id"] == "+56999"
    engine.async_create_session.assert_awaited_once_with(
        user_id="+56999", session_id="+56999",
    )


@pytest.mark.asyncio
async def test_create_agent_session_handles_exists_then_not_visible():
    """Entregas concurrentes del mismo turno: un create() reporta AlreadyExists
    mientras el primer get_session() todavía no ve esa sesión (consistencia
    eventual). create_agent_session no debe propagar: reintenta el get acotado
    y devuelve la sesión apenas sea visible."""
    from whatsapp_webhook.external_services import agent_client

    engine = MagicMock()
    engine.async_create_session = AsyncMock(side_effect=gax.AlreadyExists("dup"))
    get_calls = {"n": 0}

    async def fake_get_session(*, user_id, session_id):
        get_calls["n"] += 1
        if get_calls["n"] == 1:
            raise RuntimeError("Session not found. Please create it using .create_session()")
        return {"id": session_id, "events": []}

    engine.async_get_session = fake_get_session
    with patch.object(agent_client, "get_engine", return_value=engine):
        out = await agent_client.create_agent_session(
            user_id="uuid-1", app_name="agent_aa", session_id="56999",
        )
    assert out["id"] == "56999"
    assert get_calls["n"] == 2  # reintentó una vez


@pytest.mark.asyncio
async def test_create_agent_session_exists_then_never_visible_propagates(monkeypatch):
    """Si tras agotar los reintentos la sesión sigue sin ser visible, el error
    debe propagar (no quedar colgado ni devolver algo falso)."""
    from whatsapp_webhook.external_services import agent_client

    monkeypatch.setattr(agent_client, "SESSION_RETRY_ATTEMPTS", 2)
    engine = MagicMock()
    engine.async_create_session = AsyncMock(side_effect=gax.AlreadyExists("dup"))

    async def always_not_found(*, user_id, session_id):
        raise RuntimeError("Session not found. Please create it using .create_session()")

    engine.async_get_session = always_not_found
    with patch.object(agent_client, "get_engine", return_value=engine):
        with pytest.raises(RuntimeError, match="Session not found"):
            await agent_client.create_agent_session(
                user_id="uuid-1", app_name="agent_aa", session_id="56999",
            )


@pytest.mark.asyncio
async def test_send_to_agent_concatenates_assistant_text():
    """Multiple events with text parts -> concatenated response string."""
    from whatsapp_webhook.external_services import agent_client

    async def fake_stream(*, user_id, session_id, message):
        yield {"content": {"parts": [{"text": "Hola "}]}}
        yield {"content": {"parts": [{"function_call": {"name": "search"}}]}}
        yield {"content": {"parts": [{"text": "mundo."}]}}

    engine = MagicMock()
    engine.async_stream_query = lambda **kw: fake_stream(**kw)
    with patch.object(agent_client, "get_engine", return_value=engine):
        result = await agent_client.send_to_agent(
            app_name="agent_aa", user_id="+56999", session_id="+56999",
            message="hola",
        )
    assert result["response"] == "Hola mundo."
    assert len(result["raw_response"]) == 3


@pytest.mark.asyncio
async def test_send_to_agent_returns_error_payload_when_no_text():
    """Tool-call-only stream -> empty string -> error payload."""
    from whatsapp_webhook.external_services import agent_client

    async def fake_stream(*, user_id, session_id, message):
        yield {"content": {"parts": [{"function_call": {"name": "search"}}]}}

    engine = MagicMock()
    engine.async_stream_query = lambda **kw: fake_stream(**kw)
    with patch.object(agent_client, "get_engine", return_value=engine):
        result = await agent_client.send_to_agent(
            app_name="agent_aa", user_id="+56999", session_id="+56999",
            message="hola",
        )
    assert "Error" in result["response"]


def test_short_for_known_app_names_round_trip(monkeypatch):
    """_short_for must map the configured aa_app_name and pp_app_name."""
    from whatsapp_webhook.external_services import agent_client
    assert agent_client._short_for("agent_aa") == "aa"
    assert agent_client._short_for("agent_pp") == "pp"


def test_short_for_raises_on_unknown_app_name():
    """Anything outside config.aa_app_name / config.pp_app_name fails loud."""
    from whatsapp_webhook.external_services import agent_client
    with pytest.raises(ValueError, match="Unknown agent app_name"):
        agent_client._short_for("agent_xx")


@pytest.mark.asyncio
async def test_send_to_agent_times_out_with_error_payload(monkeypatch):
    """A hung stream must hit the configured timeout, not block forever."""
    from whatsapp_webhook.external_services import agent_client
    # Shrink the timeout to keep the test fast.
    monkeypatch.setattr(agent_client, "QUERY_TIMEOUT_SECONDS", 0.05)

    async def hanging_stream(*, user_id, session_id, message):
        # Yields once then sleeps forever
        yield {"content": {"parts": [{"text": "starting"}]}}
        await asyncio.sleep(10)

    engine = MagicMock()
    engine.async_stream_query = lambda **kw: hanging_stream(**kw)
    with patch.object(agent_client, "get_engine", return_value=engine):
        result = await agent_client.send_to_agent(
            app_name="agent_aa", user_id="+56999", session_id="+56999",
            message="hola",
        )
    assert "Error" in result["response"]
    assert "tiempo" in result["response"].lower()


@pytest.mark.asyncio
async def test_send_to_agent_recovers_from_eventual_consistency(monkeypatch):
    """La sesión recién creada puede no ser visible al primer stream_query
    (consistencia eventual). send_to_agent debe reintentar y completar, sin
    duplicar el texto del intento fallido."""
    from whatsapp_webhook.external_services import agent_client

    calls = {"n": 0}

    async def fake_stream_query(*, user_id, session_id, message):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("Session not found. Please create it using .create_session()")
        # segundo intento: la sesión ya es visible
        yield {"content": {"parts": [{"text": "hola productor"}]}}

    engine = MagicMock()
    engine.async_stream_query = lambda **kw: fake_stream_query(**kw)

    monkeypatch.setattr(agent_client, "create_agent_session", AsyncMock())
    with patch.object(agent_client, "get_engine", return_value=engine):
        res = await agent_client.send_to_agent(
            app_name="agent_aa", user_id="uuid-1", session_id="56999",
            message="hola",
        )
    assert res["response"] == "hola productor"
    assert calls["n"] == 2  # reintentó una vez
    agent_client.create_agent_session.assert_awaited_once_with(
        "uuid-1", "agent_aa", "56999",
    )


@pytest.mark.asyncio
async def test_send_to_agent_gives_up_gracefully(monkeypatch):
    """Si "Session not found" persiste tras agotar los reintentos, send_to_agent
    no debe propagar la excepción: debe devolver un payload de error, igual que
    hace hoy con el timeout."""
    from whatsapp_webhook.external_services import agent_client

    # Keep the test fast: 2 attempts -> a single 0.3s backoff.
    monkeypatch.setattr(agent_client, "SESSION_RETRY_ATTEMPTS", 2)
    monkeypatch.setattr(agent_client, "create_agent_session", AsyncMock())

    async def always_not_found(*, user_id, session_id, message):
        raise RuntimeError("Session not found. Please create it using .create_session()")
        yield  # pragma: no cover

    engine = MagicMock()
    engine.async_stream_query = lambda **kw: always_not_found(**kw)
    with patch.object(agent_client, "get_engine", return_value=engine):
        result = await agent_client.send_to_agent(
            app_name="agent_aa", user_id="uuid-1", session_id="56999",
            message="hola",
        )
    assert "response" in result
    assert "Error" in result["response"]


@pytest.mark.asyncio
async def test_get_engine_picks_up_secret_rotation(monkeypatch):
    """Re-reading SM means a rewritten resource_name -> fresh engine handle.

    TTL is forced to 0 so the resolved resource_name is never served from cache,
    exercising rotation on back-to-back calls.
    """
    from whatsapp_webhook.external_services import agent_client

    # Disable the resource_name TTL cache so every call re-reads Secret Manager.
    monkeypatch.setattr(agent_client, "SECRET_TTL_SECONDS", 0.0)

    versions = iter([
        b"projects/p/locations/us-central1/reasoningEngines/OLD",
        b"projects/p/locations/us-central1/reasoningEngines/NEW",
    ])

    class FakeSM:
        def access_secret_version(self, request):
            data = MagicMock()
            data.payload.data = next(versions)
            return data

    monkeypatch.setattr(
        agent_client.secretmanager, "SecretManagerServiceClient", lambda: FakeSM()
    )
    seen: list[str] = []

    def fake_get(name):
        seen.append(name)
        m = MagicMock()
        m.resource_name = name
        return m

    monkeypatch.setattr(agent_client.agent_engines, "get", fake_get)
    monkeypatch.setattr(agent_client, "_init", lambda: None)

    first = await agent_client.get_engine("agent_aa")
    second = await agent_client.get_engine("agent_aa")
    assert first is not second
    assert seen == [
        "projects/p/locations/us-central1/reasoningEngines/OLD",
        "projects/p/locations/us-central1/reasoningEngines/NEW",
    ]
