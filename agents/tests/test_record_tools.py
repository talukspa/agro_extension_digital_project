"""Las tools del expediente: contrato, identidad y cuerpos exactos."""
import httpx
import pytest

from core import record_tools


class FakeToolContext:
    """Lo mínimo que las tools leen de un ToolContext real: user_id."""

    def __init__(self, user_id):
        self.user_id = user_id


PRODUCTOR = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"


async def test_sin_uuid_la_tool_se_niega_y_no_llama_a_nadie(monkeypatch):
    """Un teléfono sin vincular llega como user_id: no es un productor."""
    llamadas = []
    monkeypatch.setattr(record_tools.httpx, "AsyncClient",
                        lambda *a, **k: llamadas.append(1))
    r = await record_tools.obtener_perfil_empresa(FakeToolContext("56912345678"))
    assert r == {"ok": False, "error": "SESSION_WITHOUT_PRODUCER"}
    assert llamadas == []


async def test_producer_user_id_no_es_parametro_de_ninguna_tool():
    """La propiedad de seguridad: el modelo no puede elegir de quién es el expediente."""
    import inspect
    for fn in record_tools.TOOLS:
        params = set(inspect.signature(fn).parameters)
        assert "producer_user_id" not in params, fn.__name__
        assert "producerUserId" not in params, fn.__name__
        assert "productor" not in params, fn.__name__


# --- _post: identidad, cuerpo de la respuesta y manejo de errores ----------


class FakeResponse:
    """Doble de httpx.Response: sólo lo que `_post` lee."""

    def __init__(self, status_code, json_data=None, json_raises=False):
        self.status_code = status_code
        self._json_data = json_data
        self._json_raises = json_raises

    def json(self):
        if self._json_raises:
            raise ValueError("cuerpo no es JSON")
        return self._json_data


class FakeAsyncClient:
    """Doble del cliente httpx: mismo rol que el `_client` fake de
    test_bq_tools.py, pero async — soporta `async with` y `await .post(...)`."""

    def __init__(self, response=None, raise_exc=None):
        self._response = response
        self._raise_exc = raise_exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def post(self, *args, **kwargs):
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._response


def _stub_client(monkeypatch, response=None, raise_exc=None):
    monkeypatch.setattr(record_tools, "_http_client",
                        lambda: FakeAsyncClient(response, raise_exc))


def _productor_ctx():
    return FakeToolContext(PRODUCTOR)


async def test_post_camino_feliz_devuelve_la_data(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_client(monkeypatch, response=FakeResponse(200, {"data": {"x": 1}}))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": True, "data": {"x": 1}}


async def test_post_400_con_error_de_codigo(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_client(monkeypatch, response=FakeResponse(
        400, {"error": {"code": "ID_INVALID"}}))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "ID_INVALID"}


async def test_post_400_con_error_de_texto(monkeypatch):
    """Arreglo 5: `error` como string no debe colapsar a un código genérico."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_client(monkeypatch, response=FakeResponse(400, {"error": "texto plano"}))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "texto plano"}


async def test_post_respuesta_no_json(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_client(monkeypatch, response=FakeResponse(500, json_raises=True))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "NON_JSON_RESPONSE_HTTP_500"}


async def test_post_respuesta_json_que_no_es_objeto(monkeypatch):
    """Arreglo 2: JSON válido pero no dict (lista, string, null, número) no
    debe levantar AttributeError al llamar .get() sobre él."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    for cuerpo in [["algo"], "texto", None, 42]:
        _stub_client(monkeypatch, response=FakeResponse(200, cuerpo))
        r = await record_tools._post("business-profile", {}, _productor_ctx())
        assert r["ok"] is False
        assert r["error"].startswith("NON_OBJECT_RESPONSE_HTTP_"), cuerpo


async def test_post_excepcion_que_no_hereda_de_httpx_http_error(monkeypatch):
    """Arreglo 1: httpx.InvalidURL NO hereda de httpx.HTTPError. Se usa la
    excepción real (no un mock) para probar exactamente ese hueco: un
    `except httpx.HTTPError` la deja escapar hacia el llamador en vez de
    volver {ok, error}."""
    assert not issubclass(httpx.InvalidURL, httpx.HTTPError)
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    exc = httpx.InvalidURL("URL inválida")
    _stub_client(monkeypatch, raise_exc=exc)
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "PLATFORM_UNREACHABLE: InvalidURL"}


async def test_post_identidad_de_sesion_gana_sobre_el_payload(monkeypatch):
    """Arreglo 3: un payload con `producerUserId` no debe pisar la identidad
    que vino de tool_context.user_id."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    capturado = {}

    class ClienteQueCaptura(FakeAsyncClient):
        async def post(self, *args, **kwargs):
            capturado.update(kwargs.get("json", {}))
            return FakeResponse(200, {"data": {}})

    monkeypatch.setattr(record_tools, "_http_client", lambda: ClienteQueCaptura())
    otro_uuid = "00000000-0000-0000-0000-000000000000"
    await record_tools._post(
        "business-profile", {"producerUserId": otro_uuid}, _productor_ctx())
    assert capturado["producerUserId"] == PRODUCTOR


# --- _scope: qué campos de alcance sobreviven al filtro ---------------------


@pytest.mark.parametrize("valor,esperado", [
    ("", False),
    ("   ", False),
    ("  abc  ", "abc"),
    (42, False),
    (True, False),
])
def test_scope_filtra_segun_el_valor(valor, esperado):
    out = record_tools._scope(campo=valor)
    if esperado is False:
        assert "campo" not in out
    else:
        assert out["campo"] == esperado


# --- producer_id: qué formas cuentan como un uuid de productor --------------


@pytest.mark.parametrize("valor,esperado", [
    (PRODUCTOR, PRODUCTOR),
    (PRODUCTOR.upper(), PRODUCTOR.upper()),
    (f"  {PRODUCTOR}  ", PRODUCTOR),
    ("56912345678", None),
    (None, None),
    (12345, None),
])
def test_producer_id_valida_la_forma(valor, esperado):
    assert record_tools.producer_id(valor) == esperado
