"""La baja de WhatsApp no puede depender de que el modelo se acuerde.

Medido sobre 5 corridas del mismo mensaje ("no me escriban más por favor"), 2
veces el agente respondió "Registré tu preferencia para no recibir más mensajes"
sin haber llamado a ninguna herramienta. Reforzar la instrucción lo bajó de 5/5
a 2/5, no a 0. El productor queda creyendo que se dio de baja y sigue dado de
alta: es un incumplimiento legal, no una respuesta imperfecta.
"""
from types import SimpleNamespace

import pytest

from core import consent_guard

PRODUCTOR = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"


def _request(texto):
    """El llm_request mínimo que el callback lee."""
    return SimpleNamespace(contents=[SimpleNamespace(
        role="user", parts=[SimpleNamespace(text=texto)])])


class _Ctx:
    user_id = PRODUCTOR


@pytest.fixture
def registrado(monkeypatch):
    """Intercepta la tool y devuelve la lista de acciones registradas."""
    hecho = []

    async def falsa(tool_context, accion):
        hecho.append(accion)
        return {"ok": True, "data": {"action": accion}}

    monkeypatch.setattr(consent_guard.record_tools,
                        "registrar_preferencia_de_contacto", falsa)
    return hecho


BAJAS = ["no me escriban más por favor", "no me manden más mensajes",
         "dame de baja", "bájame de la lista", "para de escribirme",
         "me doy de baja", "no quiero más wsp", "déjame de escribir",
         "NO ME ESCRIBAN MAS", "quiero dar de baja", "no me escribas más",
         "ya no quiero recibir los mensajes"]


async def test_toda_forma_de_pedir_la_baja_la_registra(registrado):
    for frase in BAJAS:
        registrado.clear()
        r = await consent_guard.before_model(_Ctx(), _request(frase))
        assert registrado == ["revoked"], f"no registró la baja de: {frase!r}"
        assert "baja" in r.content.parts[0].text.lower()


async def test_pedir_el_alta_la_registra(registrado):
    r = await consent_guard.before_model(
        _Ctx(), _request("sí quiero recibir los mensajes de nuevo"))
    assert registrado == ["granted"]
    assert "alta" in r.content.parts[0].text.lower()


async def test_una_consulta_normal_sigue_al_modelo(registrado):
    for frase in ["cómo va mi cumplimiento?", "qué me falta pendiente?",
                  "te mando la foto del medidor", "me escribió el auditor?"]:
        assert await consent_guard.before_model(_Ctx(), _request(frase)) is None
        assert registrado == [], f"interceptó de más: {frase!r}"


async def test_si_el_endpoint_falla_no_promete_la_baja_como_confirmada(monkeypatch):
    async def falla(tool_context, accion):
        return {"ok": False, "error": "PLATFORM_UNREACHABLE"}

    monkeypatch.setattr(consent_guard.record_tools,
                        "registrar_preferencia_de_contacto", falla)
    r = await consent_guard.before_model(_Ctx(), _request("dame de baja"))
    assert "no pude confirmarla" in r.content.parts[0].text


async def test_sin_productor_no_intercepta(registrado):
    """Un teléfono sin vincular no tiene consentimiento que registrar."""

    class SinUuid:
        user_id = "56912345678"

    assert await consent_guard.before_model(SinUuid(), _request("dame de baja")) is None
    assert registrado == []


# --- Falsos positivos: la regex no puede morder lo que no es una baja -----

FALSOS_POSITIVOS = [
    "me escribieron del auditor?",
    "no me escribió nadie?",
    "mi vecino me dijo que me dieron de baja del programa, es cierto?",
    "por qué no me mandan más las guías?",
    "no me llegó el mensaje",
    "me bajé la guía de agua",
    "el auditor no me ha escrito",
    "no me mandes la foto, mándame el documento",
    "no me quedan acciones pendientes",
]


async def test_no_muerde_falsos_positivos(registrado):
    for frase in FALSOS_POSITIVOS:
        assert await consent_guard.before_model(_Ctx(), _request(frase)) is None, \
            f"falso positivo: {frase!r}"
        assert registrado == [], f"registró de más con: {frase!r}"


# --- "dame de alta" reconocida como alta, no como baja ---------------------

async def test_dame_de_alta_no_es_una_baja(registrado):
    r = await consent_guard.before_model(_Ctx(), _request("dame de alta"))
    assert registrado == ["granted"]
    assert "alta" in r.content.parts[0].text.lower()


# --- Una baja NEGANDO la frase de alta no puede registrarse como alta -----
#
# "no vuelvan a escribirme" contiene "vuelvan a escribirme", que por sí solo
# es una alta. Sin resguardo, _PIDE_ALTA la registra como "granted": el
# productor pidió que le paren de escribir y queda confirmado como suscrito.

NEGACIONES_DE_ALTA = [
    "no vuelvan a escribirme",
    "no quiero que vuelvan a escribirme",
    "por favor no vuelvan a escribirme más",
    "no me reactiven los mensajes",
]


async def test_negar_la_frase_de_alta_no_registra_alta(registrado):
    for frase in NEGACIONES_DE_ALTA:
        r = await consent_guard.before_model(_Ctx(), _request(frase))
        assert "granted" not in registrado, \
            f"registró alta por error con: {frase!r}"
        registrado.clear()


# --- Lee el ÚLTIMO mensaje del usuario, no el primero ----------------------

async def test_lee_el_ultimo_mensaje_del_usuario_no_el_primero(registrado):
    llm_request = SimpleNamespace(contents=[
        SimpleNamespace(role="user",
                        parts=[SimpleNamespace(text="dame de baja")]),
        SimpleNamespace(role="model",
                        parts=[SimpleNamespace(text="listo, de baja")]),
        SimpleNamespace(role="user",
                        parts=[SimpleNamespace(text="cómo va mi cumplimiento?")]),
    ])
    assert await consent_guard.before_model(_Ctx(), llm_request) is None
    assert registrado == []


# --- No revienta con formas raras de llm_request ---------------------------

async def test_contents_vacio_no_revienta(registrado):
    assert await consent_guard.before_model(
        _Ctx(), SimpleNamespace(contents=[])) is None
    assert registrado == []


async def test_contents_none_no_revienta(registrado):
    assert await consent_guard.before_model(
        _Ctx(), SimpleNamespace(contents=None)) is None
    assert registrado == []


async def test_content_sin_parts_no_revienta(registrado):
    llm_request = SimpleNamespace(
        contents=[SimpleNamespace(role="user", parts=None)])
    assert await consent_guard.before_model(_Ctx(), llm_request) is None
    assert registrado == []


async def test_part_sin_text_no_revienta(registrado):
    llm_request = SimpleNamespace(
        contents=[SimpleNamespace(role="user", parts=[SimpleNamespace()])])
    assert await consent_guard.before_model(_Ctx(), llm_request) is None
    assert registrado == []


async def test_part_con_text_none_no_revienta(registrado):
    llm_request = SimpleNamespace(
        contents=[SimpleNamespace(role="user",
                                  parts=[SimpleNamespace(text=None)])])
    assert await consent_guard.before_model(_Ctx(), llm_request) is None
    assert registrado == []
