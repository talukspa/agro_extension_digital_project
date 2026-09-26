"""Resolver el wa_id al usuario de la plataforma, antes de hablarle al agente.

El agente necesita el uuid del productor para leer y escribir su expediente, y lo
toma del `user_id` con que se abre la sesión de ADK. Acá se traduce el número que
manda Meta a ese uuid.

Lo que estos tests protegen sobre todo: que esta función **nunca levante**. Corre
en el camino del mensaje del productor, así que una excepción acá se lleva el
turno completo — y la respuesta correcta a cualquier fallo es seguir sin uuid, no
caerse: RAG y el catálogo son datos públicos del estándar y siguen sirviendo.
"""
import logging

import httpx
import pytest

from whatsapp_webhook.external_services import identity

PRODUCTOR = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"
TOKEN = "token-de-prueba-no-debe-aparecer-en-los-logs"


class FakeResponse:
    """Doble de httpx.Response: sólo lo que `resolve_producer` lee."""

    def __init__(self, status_code, payload=None, json_raises=None):
        self.status_code = status_code
        self._payload = payload
        self._json_raises = json_raises

    def json(self):
        if self._json_raises is not None:
            raise self._json_raises
        return self._payload


class FakeClient:
    def __init__(self, capturado, respuesta):
        self._capturado = capturado
        self._respuesta = respuesta

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, headers=None, json=None):
        self._capturado.append({"url": url, "headers": headers, "json": json})
        if isinstance(self._respuesta, BaseException):
            raise self._respuesta
        return self._respuesta


def _parchar(monkeypatch, respuesta):
    capturado = []
    monkeypatch.setenv("CIRUELA_API_BASE", "http://app.local")
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", TOKEN)
    monkeypatch.setattr(
        identity.httpx, "AsyncClient", lambda *a, **k: FakeClient(capturado, respuesta)
    )
    return capturado


# --------------------------------------------------------------- camino normal
async def test_un_numero_vinculado_devuelve_su_uuid(monkeypatch):
    capturado = _parchar(
        monkeypatch,
        FakeResponse(200, {"success": True, "data": {"producerUserId": PRODUCTOR}}),
    )
    assert await identity.resolve_producer("56912345678") == PRODUCTOR
    assert capturado[0]["url"] == "http://app.local/api/agent/resolve-identity"
    assert capturado[0]["json"] == {"waId": "56912345678"}
    assert capturado[0]["headers"]["Authorization"] == f"Bearer {TOKEN}"


async def test_un_numero_sin_vincular_devuelve_none(monkeypatch):
    """404 no es un error del webhook: es un número que no completó su registro."""
    _parchar(
        monkeypatch,
        FakeResponse(404, {"error": {"message": "Número desconocido.", "code": "NOT_FOUND"}}),
    )
    assert await identity.resolve_producer("56900000000") is None


async def test_sin_token_no_sale_ninguna_llamada(monkeypatch):
    capturado = []
    monkeypatch.delenv("AGENT_SERVICE_TOKEN", raising=False)
    monkeypatch.setattr(
        identity.httpx, "AsyncClient", lambda *a, **k: capturado.append(1)
    )
    assert await identity.resolve_producer("56912345678") is None
    assert capturado == []


# ------------------------------------------------------- nunca levanta, jamás
@pytest.mark.parametrize(
    "respuesta",
    [
        # de red y de forma de la URL
        httpx.ConnectError("sin ruta"),
        httpx.ReadTimeout("tarde"),
        # InvalidURL NO hereda de HTTPError: ver el test de la jerarquía abajo
        httpx.InvalidURL("puerto inválido"),
        # códigos que no son 200 ni 404
        FakeResponse(401, {"error": {"code": "UNAUTHORIZED"}}),
        FakeResponse(500, {"error": {"code": "INTERNAL"}}),
        FakeResponse(503, None),
        # el cuerpo no es JSON
        FakeResponse(200, json_raises=ValueError("no es JSON")),
        # JSON válido que no es un objeto
        FakeResponse(200, ["una", "lista"]),
        FakeResponse(200, "un string"),
        FakeResponse(200, None),
        FakeResponse(200, 42),
        # objeto sin lo que se espera
        FakeResponse(200, {"success": True, "data": {}}),
        FakeResponse(200, {"success": True}),
        FakeResponse(200, {"success": True, "data": None}),
        FakeResponse(200, {"success": True, "data": ["no", "es", "dict"]}),
        # producerUserId con un tipo que no es string
        FakeResponse(200, {"data": {"producerUserId": 12345}}),
        FakeResponse(200, {"data": {"producerUserId": None}}),
        FakeResponse(200, {"data": {"producerUserId": ""}}),
    ],
)
async def test_ningun_fallo_levanta_hacia_el_llamador(monkeypatch, respuesta):
    """Corre en el camino del mensaje del productor: si levanta, se cae el turno."""
    _parchar(monkeypatch, respuesta)
    assert await identity.resolve_producer("56912345678") is None


def test_invalid_url_no_esta_en_la_jerarquia_de_http_error():
    """Documenta por qué el `except` no puede ser sólo `httpx.HTTPError`.

    Ya nos mordió en el paquete de agentes: un CIRUELA_API_BASE con un typo
    levanta `httpx.InvalidURL`, que no desciende de `HTTPError`, así que un
    `except httpx.HTTPError` lo deja pasar.
    """
    assert not issubclass(httpx.InvalidURL, httpx.HTTPError)


# ------------------------------------------------------- el token no se filtra
@pytest.mark.parametrize(
    "respuesta",
    [
        httpx.ConnectError("sin ruta"),
        FakeResponse(500, {"error": {"code": "INTERNAL"}}),
        FakeResponse(404, {"error": {"code": "NOT_FOUND"}}),
        FakeResponse(200, json_raises=ValueError("no es JSON")),
    ],
)
async def test_el_valor_del_token_no_llega_a_los_logs(monkeypatch, caplog, respuesta):
    """El nombre de la variable sí, el valor nunca."""
    _parchar(monkeypatch, respuesta)
    with caplog.at_level(logging.DEBUG):
        await identity.resolve_producer("56912345678")
    assert TOKEN not in caplog.text


async def test_el_valor_del_token_no_llega_a_los_logs_sin_token(monkeypatch, caplog):
    """El camino de "no hay token" también loguea; no puede imprimir el vacío
    como si fuera un valor ni delatar el nombre completo de otro secreto."""
    monkeypatch.delenv("AGENT_SERVICE_TOKEN", raising=False)
    with caplog.at_level(logging.DEBUG):
        assert await identity.resolve_producer("56912345678") is None
    assert "AGENT_SERVICE_TOKEN" in caplog.text or "token" in caplog.text.lower()


# ------------------------------------------- la configuración se lee por llamada
async def test_la_base_se_lee_por_llamada_no_al_importar(monkeypatch):
    """El Cloud Run se reconfigura sin redespliegue del módulo, así que una
    lectura en el import se come el cambio."""
    capturado = []
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", TOKEN)
    monkeypatch.setattr(
        identity.httpx,
        "AsyncClient",
        lambda *a, **k: FakeClient(
            capturado, FakeResponse(200, {"data": {"producerUserId": PRODUCTOR}})
        ),
    )
    monkeypatch.setenv("CIRUELA_API_BASE", "http://primera.local")
    await identity.resolve_producer("1")
    monkeypatch.setenv("CIRUELA_API_BASE", "http://segunda.local")
    await identity.resolve_producer("2")
    assert capturado[0]["url"].startswith("http://primera.local")
    assert capturado[1]["url"].startswith("http://segunda.local")


async def test_la_barra_final_de_la_base_no_duplica_la_ruta(monkeypatch):
    capturado = _parchar(
        monkeypatch, FakeResponse(200, {"data": {"producerUserId": PRODUCTOR}})
    )
    monkeypatch.setenv("CIRUELA_API_BASE", "http://app.local/")
    await identity.resolve_producer("56912345678")
    assert capturado[0]["url"] == "http://app.local/api/agent/resolve-identity"


async def test_el_uuid_llega_sin_espacios(monkeypatch):
    _parchar(monkeypatch, FakeResponse(200, {"data": {"producerUserId": f"  {PRODUCTOR}  "}}))
    assert await identity.resolve_producer("56912345678") == PRODUCTOR
