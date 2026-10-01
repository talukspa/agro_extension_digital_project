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


class CapturingAsyncClient:
    """Doble del cliente httpx: mismo rol que el `_client` fake de
    test_catalog_tools.py, pero async — soporta `async with` y `await .post(...)`.
    Además guarda los `args`/`kwargs` de cada `post` en `llamadas`, para
    afirmar el cuerpo y la URL exactos que armó `_post`. Es el único doble de
    cliente en este archivo: nada depende de que el cliente NO capture, así
    que mantener uno que sí lo hace evita la duda de cuál usar."""

    def __init__(self, response=None, raise_exc=None):
        self._response = response
        self._raise_exc = raise_exc
        self.llamadas: list[dict] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def post(self, *args, **kwargs):
        self.llamadas.append({"args": args, "kwargs": kwargs})
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._response


def _stub_capturing_client(monkeypatch, response=None, raise_exc=None):
    """Instala un CapturingAsyncClient y devuelve su lista de llamadas (se va
    llenando in situ a medida que la tool llama a `post`)."""
    cliente = CapturingAsyncClient(response or FakeResponse(200, {"data": {}}),
                                   raise_exc)
    monkeypatch.setattr(record_tools, "_http_client", lambda: cliente)
    return cliente.llamadas


def _productor_ctx():
    return FakeToolContext(PRODUCTOR)


async def test_post_camino_feliz_devuelve_la_data(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_capturing_client(monkeypatch, response=FakeResponse(200, {"data": {"x": 1}}))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": True, "data": {"x": 1}}


async def test_post_400_con_error_de_codigo(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_capturing_client(monkeypatch, response=FakeResponse(
        400, {"error": {"code": "ID_INVALID"}}))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "ID_INVALID"}


async def test_post_400_con_error_de_texto(monkeypatch):
    """Arreglo 5: `error` como string no debe colapsar a un código genérico."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_capturing_client(monkeypatch, response=FakeResponse(400, {"error": "texto plano"}))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "texto plano"}


async def test_post_respuesta_no_json(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_capturing_client(monkeypatch, response=FakeResponse(500, json_raises=True))
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "NON_JSON_RESPONSE_HTTP_500"}


async def test_post_respuesta_json_que_no_es_objeto(monkeypatch):
    """Arreglo 2: JSON válido pero no dict (lista, string, null, número) no
    debe levantar AttributeError al llamar .get() sobre él."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    for cuerpo in [["algo"], "texto", None, 42]:
        _stub_capturing_client(monkeypatch, response=FakeResponse(200, cuerpo))
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
    _stub_capturing_client(monkeypatch, raise_exc=exc)
    r = await record_tools._post("business-profile", {}, _productor_ctx())
    assert r == {"ok": False, "error": "PLATFORM_UNREACHABLE: InvalidURL"}


async def test_post_identidad_de_sesion_gana_sobre_el_payload(monkeypatch):
    """Arreglo 3: un payload con `producerUserId` no debe pisar la identidad
    que vino de tool_context.user_id."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch, FakeResponse(200, {"data": {}}))
    otro_uuid = "00000000-0000-0000-0000-000000000000"
    await record_tools._post(
        "business-profile", {"producerUserId": otro_uuid}, _productor_ctx())
    assert llamadas[0]["kwargs"]["json"]["producerUserId"] == PRODUCTOR


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


# --- las once tools: registro, rutas y cuerpos exactos ----------------------


async def test_las_once_tools_estan_registradas():
    nombres = {fn.__name__ for fn in record_tools.TOOLS}
    assert nombres == {
        "obtener_perfil_empresa",
        "obtener_avance_del_plan",
        "listar_acciones_pendientes",
        "obtener_detalle_de_accion",
        "obtener_cumplimiento",
        "obtener_nivel_de_certificacion",
        "registrar_labor",
        "adjuntar_evidencia",
        "enviar_mensaje_al_auditor",
        "leer_conversacion_de_accion",
        "registrar_preferencia_de_contacto",
    }


@pytest.mark.parametrize("fn,kwargs,ruta", [
    (record_tools.obtener_perfil_empresa, {}, "business-profile"),
    (record_tools.obtener_avance_del_plan, {}, "plan-status"),
    (record_tools.listar_acciones_pendientes, {}, "pending-actions"),
    (record_tools.obtener_detalle_de_accion, {"codigo_accion": "A001"}, "action"),
    (record_tools.obtener_cumplimiento, {}, "compliance"),
    (record_tools.obtener_nivel_de_certificacion, {}, "certification-level"),
    (record_tools.registrar_labor,
     {"estandar": "PRODUCCION_PRIMARIA", "datos": {}}, "labor-log"),
    (record_tools.adjuntar_evidencia,
     {"codigo_accion": "A001", "id_de_adjunto": "wamid.X"}, "evidence"),
    (record_tools.enviar_mensaje_al_auditor,
     {"codigo_accion": "A001", "texto": "hola"}, "auditor-message"),
    (record_tools.leer_conversacion_de_accion,
     {"codigo_accion": "A001"}, "action-messages"),
    (record_tools.registrar_preferencia_de_contacto,
     {"accion": "granted"}, "consent"),
], ids=lambda v: v if isinstance(v, str) else getattr(v, "__name__", str(v)))
async def test_cada_tool_llama_a_su_ruta(monkeypatch, fn, kwargs, ruta):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await fn(_productor_ctx(), **kwargs)
    assert llamadas[0]["args"][0].endswith(f"/api/agent/{ruta}")


async def test_el_cuerpo_de_perfil_lleva_el_productor_y_nada_mas(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok-test")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.obtener_perfil_empresa(_productor_ctx())
    assert len(llamadas) == 1
    llamada = llamadas[0]
    assert llamada["kwargs"]["json"] == {"producerUserId": PRODUCTOR}
    assert llamada["args"][0].endswith("/api/agent/business-profile")
    assert llamada["kwargs"]["headers"]["Authorization"] == "Bearer tok-test"


async def test_el_alcance_vacio_no_viaja(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.obtener_cumplimiento(_productor_ctx(), instalacion_id="   ")
    assert llamadas[0]["kwargs"]["json"] == {"producerUserId": PRODUCTOR}


async def test_el_alcance_con_valor_si_viaja(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    inst = "7e30cce1-8750-47bd-80f9-f5697111424d"
    await record_tools.obtener_cumplimiento(_productor_ctx(), instalacion_id=inst)
    assert llamadas[0]["kwargs"]["json"] == {
        "producerUserId": PRODUCTOR, "installationId": inst}


async def test_adjuntar_evidencia_no_elige_estandar_por_su_cuenta(monkeypatch):
    """El primer intento va sin estandar: la ambigüedad la resuelve el servidor."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.adjuntar_evidencia(_productor_ctx(),
                                          codigo_accion="A001",
                                          id_de_adjunto="wamid.ABC")
    assert llamadas[0]["kwargs"]["json"] == {
        "producerUserId": PRODUCTOR, "questionCode": "A001",
        "mediaId": "wamid.ABC"}


async def test_registrar_labor_manda_el_payload_del_productor(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.registrar_labor(
        _productor_ctx(), estandar="PRODUCCION_PRIMARIA",
        datos={"supply_source": "pozo", "monthly_consumption_m3": 120})
    assert llamadas[0]["kwargs"]["json"] == {
        "producerUserId": PRODUCTOR,
        "standardCode": "PRODUCCION_PRIMARIA",
        "payload": {"supply_source": "pozo", "monthly_consumption_m3": 120}}


async def test_la_ambiguedad_llega_como_exito(monkeypatch):
    """ok: True, o el retry plugin gastaría reintentos en algo que necesita
    la respuesta de una persona."""
    ambigua = {"data": {"ambiguous": True, "kind": "installation",
                        "candidates": [{"installationId": "x", "name": "Planta"}]}}
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    _stub_capturing_client(monkeypatch, FakeResponse(200, ambigua))
    r = await record_tools.obtener_cumplimiento(_productor_ctx())
    assert r["ok"] is True
    assert r["data"]["ambiguous"] is True


async def test_listar_acciones_incluir_con_respaldo_manda_la_llave(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.listar_acciones_pendientes(
        _productor_ctx(), incluir_las_que_ya_tienen_respaldo=True)
    assert llamadas[0]["kwargs"]["json"]["includeWithEvidence"] is True


async def test_listar_acciones_sin_incluir_no_manda_la_llave(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.listar_acciones_pendientes(_productor_ctx())
    assert "includeWithEvidence" not in llamadas[0]["kwargs"]["json"]


async def test_registrar_preferencia_de_contacto_revoked(monkeypatch):
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.registrar_preferencia_de_contacto(_productor_ctx(), "revoked")
    assert llamadas[0]["kwargs"]["json"] == {
        "producerUserId": PRODUCTOR, "action": "revoked"}


async def test_enviar_mensaje_al_auditor_manda_el_cuerpo_exacto(monkeypatch):
    """La única de las cuatro escrituras sin este test: si alguien cambia
    `text` por `message`, o invierte código y texto en el payload, esta es la
    que lo detecta — el mensaje quedaría publicado con el campo equivocado en
    el expediente de una persona."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.enviar_mensaje_al_auditor(
        _productor_ctx(), codigo_accion="A001", texto="¿cuándo revisan esto?")
    assert llamadas[0]["kwargs"]["json"] == {
        "producerUserId": PRODUCTOR, "questionCode": "A001",
        "text": "¿cuándo revisan esto?"}


async def test_adjuntar_evidencia_con_nombre_en_blanco_no_manda_la_llave(monkeypatch):
    """Un nombre de archivo con sólo espacios no es lo mismo que ausente: sin
    pasar por `_scope()` viajaría `"fileName": " "` y el adjunto quedaría con
    nombre visible en blanco en el expediente, en vez de sin nombre."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.adjuntar_evidencia(
        _productor_ctx(), codigo_accion="A001", id_de_adjunto="wamid.ABC",
        nombre_archivo="   ")
    assert "fileName" not in llamadas[0]["kwargs"]["json"]


async def test_registrar_labor_con_codigo_en_blanco_no_manda_la_llave(monkeypatch):
    """Un código de acción con sólo espacios no calza con ningún código real:
    sin pasar por `_scope()` viajaría `"questionCode": " "` y la labor
    quedaría sin vincular a ninguna acción, con `ok: True` igual — nadie se
    entera."""
    monkeypatch.setenv("AGENT_SERVICE_TOKEN", "tok")
    llamadas = _stub_capturing_client(monkeypatch)
    await record_tools.registrar_labor(
        _productor_ctx(), estandar="PRODUCCION_PRIMARIA", datos={"x": 1},
        codigo_accion="   ")
    assert "questionCode" not in llamadas[0]["kwargs"]["json"]
