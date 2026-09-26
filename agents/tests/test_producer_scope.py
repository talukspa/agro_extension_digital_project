"""El bloque que le dice al modelo el alcance del productor ANTES de hablar.

Existe por dos defectos medidos en el prototipo:

1. Con una sola instalación preguntaba "¿de cuál?" ~8 de cada 10 veces. La
   instrucción ya decía "llama primero"; el modelo la ignoraba. Darle el alcance
   por adelantado lo llevó a ~9/10 respondiendo directo.
2. Con dos instalaciones preguntaba bien por nombre y después mandaba un id
   inventado ("PLADES_SANTIAGO"), porque el bloque nombraba las instalaciones
   pero no traía sus ids. El endpoint real responde 400 ID_INVALID a eso.
"""
import pytest

from core import producer_scope

ACOPIO = "2b3b6f39-f116-452e-9370-68bf49d0da16"
PLANTA = "7e30cce1-8750-47bd-80f9-f5697111424d"
EMP_UNO = "d290f1ee-6c54-4b01-90e6-d701748f0851"
EMP_DOS = "e390f1ee-6c54-4b01-90e6-d701748f0852"


def _perfil(*instalaciones):
    return {"profile": {"legalName": "Empresa Test Ciruelas S.A.",
                        "commercialName": "Test Ciruelas",
                        "installations": list(instalaciones)}}


@pytest.fixture(autouse=True)
def _clean_cache():
    """El cache es un dict a nivel de módulo: sin limpiarlo, un test contamina
    al siguiente con el alcance de un productor que ya no corresponde."""
    producer_scope._cache.clear()
    yield
    producer_scope._cache.clear()


def test_una_instalacion_no_pide_elegir():
    texto = producer_scope.render(_perfil(
        {"installationId": PLANTA, "name": "Planta de Deshidratado",
         "city": "Santiago"}))
    assert "UNA sola instalación" in texto
    assert "no hay nada que preguntar" in texto
    assert "obtener_cumplimiento" in texto
    # sin id: la instrucción es llamar sin instalacion_id, no hay nada que copiar
    assert PLANTA not in texto


def test_varias_instalaciones_traen_su_id():
    texto = producer_scope.render(_perfil(
        {"installationId": ACOPIO, "name": "Centro de Acopio", "city": "Curicó"},
        {"installationId": PLANTA, "name": "Planta de Deshidratado",
         "city": "Santiago"}))
    assert "2 instalaciones" in texto
    assert f"instalacion_id={ACOPIO}" in texto
    assert f"instalacion_id={PLANTA}" in texto
    assert "sin inventarlo" in texto


def test_una_empresa_dice_que_no_llene_empresa_id():
    texto = producer_scope.render(_perfil(
        {"installationId": PLANTA, "name": "Planta", "city": "Santiago"}))
    assert "deja empresa_id vacío" in texto


def test_varias_empresas_traen_su_id():
    texto = producer_scope.render({
        "ambiguous": True, "kind": "business", "candidates": [
            {"businessId": EMP_UNO, "legalName": "Empresa Uno S.A."},
            {"businessId": EMP_DOS, "legalName": "Empresa Dos Ltda."}]})
    assert "2 empresas" in texto
    assert f"empresa_id={EMP_UNO}" in texto
    assert f"empresa_id={EMP_DOS}" in texto
    assert "NO es el nombre de la empresa" in texto


def test_sin_instalaciones_lo_dice():
    texto = producer_scope.render(_perfil())
    assert "No tiene instalaciones activas" in texto


def test_sin_perfil_no_inventa_contexto():
    assert producer_scope.render({}) == ""
    assert producer_scope.render({"profile": None}) == ""
    assert producer_scope.render(None) == ""


# --- ids/nombres ausentes: nunca "None" en el prompt ------------------------
#
# Este archivo existe para que el modelo no invente un id derivado del
# nombre ("PLADES_SANTIAGO"). Si un candidato sin id se dejara en el bloque
# tal cual, "cópialo tal cual" haría que el modelo mande el string "None" —
# el mismo desenlace (400 ID_INVALID) con una causa distinta.


def test_instalacion_sin_id_no_colapsa_a_certeza_falsa():
    """El caso que reprodujo el revisor contra el endpoint real: con DOS
    instalaciones (una sin id), un conteo filtrado por id daba 1 y colapsaba
    a la rama de "UNA sola" — que le dice al modelo que el servidor la
    resuelve sin instalacion_id y que no hay nada que confirmar. Verificado
    contra el endpoint: sin instalacion_id y con 2 instalaciones reales, el
    servidor SIGUE devolviendo `ambiguous`. El bloque no puede prometer lo
    contrario."""
    texto = producer_scope.render(_perfil(
        {"name": "Centro de Acopio", "city": "Curicó"},  # sin installationId
        {"installationId": PLANTA, "name": "Planta de Deshidratado",
         "city": "Santiago"}))
    assert "None" not in texto
    assert "UNA sola instalación" not in texto
    assert "no hay nada que preguntar" not in texto
    # el conteo real (2) se mantiene, aunque sólo una trajo id usable
    assert "2 instalaciones" in texto
    assert f"instalacion_id={PLANTA}" in texto
    # la que no trae id no se nombra: no hay nada que copiar para ella
    assert "Centro de Acopio" not in texto


def test_instalacion_sin_nombre_usa_fallback_legible():
    texto = producer_scope.render(_perfil(
        {"installationId": ACOPIO, "city": "Curicó"},  # sin name
        {"installationId": PLANTA, "name": "Planta de Deshidratado",
         "city": "Santiago"}))
    assert "None" not in texto
    assert f"instalacion_id={ACOPIO}" in texto  # el id sigue, es lo que importa
    assert "sin nombre registrado" in texto


def test_todas_las_instalaciones_sin_id_no_afirma_que_no_tiene():
    """Mismo colapso, en el otro extremo: si NINGUNA trae id, el conteo
    filtrado da 0 y podría colapsar a "no tiene instalaciones activas" — otra
    afirmación que el servidor (que sigue viendo 2) va a contradecir."""
    texto = producer_scope.render(_perfil(
        {"name": "Centro de Acopio", "city": "Curicó"},
        {"name": "Planta", "city": "Santiago"}))
    assert "None" not in texto
    assert "No tiene instalaciones activas" not in texto
    assert "2 instalaciones" in texto


def test_empresa_ambigua_sin_id_se_omite_pero_el_conteo_no_baja():
    """Mismo colapso en el eje de empresas: el conteo tiene que ser el que YA
    estableció el servidor con `ambiguous: true` (2), no cuántos candidatos
    trajeron id (1) — si no, el bloque diría "1 empresa" y la siguiente
    llamada con empresa_id vacío volvería a encontrar 2 y a devolver
    `ambiguous`, contradiciendo lo que se le acaba de decir al modelo."""
    texto = producer_scope.render({
        "ambiguous": True, "kind": "business", "candidates": [
            {"legalName": "Empresa Sin Id S.A."},  # sin businessId
            {"businessId": EMP_DOS, "legalName": "Empresa Dos Ltda."}]})
    assert "None" not in texto
    assert "2 empresas" in texto
    assert "1 empresas" not in texto
    assert f"empresa_id={EMP_DOS}" in texto
    assert "Empresa Sin Id" not in texto
    # tampoco se colapsa al caso de "empresa única": el servidor YA dijo que
    # hay más de una, y ese caso instruye dejar empresa_id vacío siempre.
    assert "ÚNICA empresa" not in texto


def test_empresa_ambigua_sin_nombre_usa_fallback_legible():
    texto = producer_scope.render({
        "ambiguous": True, "kind": "business", "candidates": [
            {"businessId": EMP_UNO},  # sin legalName ni commercialName
            {"businessId": EMP_DOS, "legalName": "Empresa Dos Ltda."}]})
    assert "None" not in texto
    assert f"empresa_id={EMP_UNO}" in texto
    assert "sin nombre registrado" in texto


def test_todas_las_empresas_sin_id_no_da_bloque():
    texto = producer_scope.render({
        "ambiguous": True, "kind": "business",
        "candidates": [{"legalName": "Empresa Sin Id S.A."}]})
    assert texto == ""


# --- forma inesperada del endpoint: degrada a "", no revienta --------------


def test_installations_no_es_lista_no_revienta():
    assert producer_scope.render(
        {"profile": {"commercialName": "T", "installations": {"a": 1}}}
    ) == ""


def test_candidates_no_es_lista_no_revienta():
    assert producer_scope.render(
        {"ambiguous": True, "kind": "business", "candidates": "no-es-lista"}
    ) == ""


def test_profile_no_es_dict_no_revienta():
    assert producer_scope.render({"profile": "no-es-dict"}) == ""


async def test_sin_uuid_no_llama_a_nadie(monkeypatch):
    """Un teléfono sin vincular no tiene alcance que consultar."""
    llamadas = []
    monkeypatch.setattr(producer_scope.record_tools, "_http_client",
                        lambda: llamadas.append(1))

    class Ctx:
        user_id = "56912345678"

    assert await producer_scope.for_context(Ctx()) == ""
    assert llamadas == []


# --- cache: por productor, no global; no vuelve a pegarle al endpoint; ------
# --- un fallo no lo envenena para toda la sesión. ---------------------------

PRODUCTOR_A = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"
PRODUCTOR_B = "a2a2a2a2-6c54-4b01-90e6-d701748f0899"


class Ctx:
    def __init__(self, user_id):
        self.user_id = user_id


async def test_cache_es_por_productor_no_global(monkeypatch):
    """Un engine de Agent Engine sirve muchas sesiones en el mismo proceso: si
    el cache fuera un único slot, el productor A vería el alcance del
    productor B — la misma fuga que este diseño evita en las otras capas."""
    respuestas = {
        PRODUCTOR_A: {"ok": True, "data": _perfil(
            {"installationId": PLANTA, "name": "Planta A", "city": "Santiago"})},
        PRODUCTOR_B: {"ok": True, "data": _perfil(
            {"installationId": ACOPIO, "name": "Planta B", "city": "Curicó"})},
    }

    async def fake_post(path, payload, tool_context):
        return respuestas[tool_context.user_id]

    monkeypatch.setattr(producer_scope.record_tools, "_post", fake_post)

    texto_a = await producer_scope.for_context(Ctx(PRODUCTOR_A))
    texto_b = await producer_scope.for_context(Ctx(PRODUCTOR_B))

    assert "Planta A" in texto_a
    assert "Planta A" not in texto_b
    assert "Planta B" in texto_b
    assert "Planta B" not in texto_a


async def test_segunda_llamada_no_vuelve_a_pegarle_al_endpoint(monkeypatch):
    llamadas = []

    async def fake_post(path, payload, tool_context):
        llamadas.append(1)
        return {"ok": True, "data": _perfil(
            {"installationId": PLANTA, "name": "Planta", "city": "Santiago"})}

    monkeypatch.setattr(producer_scope.record_tools, "_post", fake_post)

    await producer_scope.for_context(Ctx(PRODUCTOR_A))
    await producer_scope.for_context(Ctx(PRODUCTOR_A))

    assert len(llamadas) == 1


async def test_fallo_del_endpoint_no_se_cachea(monkeypatch):
    """Un fallo NO se cachea: se reintenta en la próxima vuelta.

    El turno de WhatsApp siguiente llega segundos después. Si acá se cacheara
    un `{}` (que `render` convierte en ""), una caída momentánea de la
    plataforma dejaría al productor sin contexto durante TODA la sesión —
    justo cuando el bloque es lo que evita que el modelo invente ids. Cachear
    sólo éxitos (mismo criterio que `list_tables`/`get_schema` en
    core/bq_tools.py) deja que la próxima vuelta lo reintente sola, sin que
    nadie tenga que reiniciar la sesión.
    """
    llamadas = []

    async def fake_post(path, payload, tool_context):
        llamadas.append(1)
        if len(llamadas) == 1:
            return {"ok": False, "error": "PLATFORM_UNREACHABLE: TimeoutError"}
        return {"ok": True, "data": _perfil(
            {"installationId": PLANTA, "name": "Planta", "city": "Santiago"})}

    monkeypatch.setattr(producer_scope.record_tools, "_post", fake_post)

    primero = await producer_scope.for_context(Ctx(PRODUCTOR_A))
    assert primero == ""

    segundo = await producer_scope.for_context(Ctx(PRODUCTOR_A))
    assert "Planta" in segundo
    assert len(llamadas) == 2
