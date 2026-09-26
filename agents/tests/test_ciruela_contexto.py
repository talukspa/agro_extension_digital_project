"""El bloque de contexto del productor: lo que el modelo ve antes de hablar.

Existe por un defecto medido: con dos instalaciones el agente preguntaba bien
por nombre y después mandaba un id inventado ("PLADES_SANTIAGO"), porque el
bloque nombraba las instalaciones pero no traía sus ids. El endpoint real
responde 400 ID_INVALID a eso.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent_wa_ciruela"))

from ciruela_agent import tools as T  # noqa: E402

ACOPIO = "2b3b6f39-f116-452e-9370-68bf49d0da16"
PLANTA = "7e30cce1-8750-47bd-80f9-f5697111424d"


def _con_alcance(alcance):
    T._alcance_cache = alcance
    try:
        return T.contexto_del_productor()
    finally:
        T._alcance_cache = None


def _perfil(*instalaciones):
    return {"profile": {"legalName": "Empresa Test Ciruelas S.A.",
                        "installations": list(instalaciones)}}


def test_una_instalacion_no_pide_elegir():
    texto = _con_alcance(_perfil(
        {"installationId": PLANTA, "name": "Planta de Deshidratado", "city": "Santiago"}))
    assert "UNA sola instalación" in texto
    assert "no hay nada que preguntar" in texto
    assert "obtener_cumplimiento" in texto
    # sin id: la instrucción es llamar sin instalacion_id, no hay nada que copiar
    assert PLANTA not in texto


def test_varias_instalaciones_traen_su_id():
    texto = _con_alcance(_perfil(
        {"installationId": ACOPIO, "name": "Centro de Acopio", "city": "Curicó"},
        {"installationId": PLANTA, "name": "Planta de Deshidratado", "city": "Santiago"}))
    assert "2 instalaciones" in texto
    # el defecto: nombrarlas sin dar los ids obliga al modelo a inventarlos
    assert f"instalacion_id={ACOPIO}" in texto
    assert f"instalacion_id={PLANTA}" in texto
    assert "sin inventarlo" in texto


EMP_UNO = "d290f1ee-6c54-4b01-90e6-d701748f0851"
EMP_DOS = "e390f1ee-6c54-4b01-90e6-d701748f0852"


def test_varias_empresas_traen_su_id():
    """El mismo defecto que las instalaciones, en el eje de la empresa.

    Medido: con el bloque nombrando las empresas pero sin sus ids, el agente
    mandó `businessId: "Empresa Test Ciruelas S.A."` y el endpoint respondió 400.
    En la llamada que fallaba era un registro de labor, así que el dato que el
    productor acababa de reportar se perdió.
    """
    texto = _con_alcance({"ambiguous": True, "kind": "business", "candidates": [
        {"businessId": EMP_UNO, "legalName": "Empresa Uno S.A."},
        {"businessId": EMP_DOS, "legalName": "Empresa Dos Ltda."}]})
    assert "2 empresas" in texto
    assert "Empresa Uno S.A." in texto and "Empresa Dos Ltda." in texto
    assert f"empresa_id={EMP_UNO}" in texto
    assert f"empresa_id={EMP_DOS}" in texto
    assert "NO es el nombre de la empresa" in texto


def test_una_empresa_dice_que_no_llene_empresa_id():
    texto = _con_alcance(_perfil(
        {"installationId": PLANTA, "name": "Planta", "city": "Santiago"}))
    assert "deja empresa_id vacío" in texto


def test_sin_perfil_no_inventa_contexto():
    assert _con_alcance({}) == ""
    assert _con_alcance({"profile": None}) == ""


# ------------------------------------------------ la baja no pasa por el modelo
from types import SimpleNamespace  # noqa: E402

from ciruela_agent import agent as A  # noqa: E402


def _pide(texto):
    """Arma el llm_request mínimo que el callback necesita leer."""
    return SimpleNamespace(contents=[SimpleNamespace(
        role="user", parts=[SimpleNamespace(text=texto)])])


def _corre(texto, monkeypatch):
    llamadas = []
    monkeypatch.setattr(A, "registrar_preferencia_de_contacto",
                        lambda accion: llamadas.append(accion) or {"action": accion})
    respuesta = A._consentimiento_antes_del_modelo(None, _pide(texto))
    dijo = respuesta.content.parts[0].text if respuesta else None
    return llamadas, dijo


BAJAS = ["no me escriban más por favor", "no me manden más mensajes", "dame de baja",
         "bájame de la lista", "para de escribirme", "me doy de baja",
         "no quiero más wsp", "déjame de escribir"]


def test_toda_forma_de_pedir_la_baja_la_registra(monkeypatch):
    for frase in BAJAS:
        llamadas, dijo = _corre(frase, monkeypatch)
        assert llamadas == ["revoked"], f"no registró la baja de: {frase!r}"
        assert dijo and "baja" in dijo.lower()


def test_pedir_el_alta_la_registra(monkeypatch):
    llamadas, dijo = _corre("sí quiero recibir los mensajes de nuevo", monkeypatch)
    assert llamadas == ["granted"]
    assert dijo and "alta" in dijo.lower()


def test_una_consulta_normal_sigue_al_modelo(monkeypatch):
    for frase in ["cómo va mi cumplimiento?", "qué me falta pendiente?",
                  "te mando la foto del medidor", "me escribió el auditor?"]:
        llamadas, dijo = _corre(frase, monkeypatch)
        assert llamadas == [] and dijo is None, f"interceptó de más: {frase!r}"


def test_si_el_endpoint_falla_no_promete_la_baja_como_confirmada(monkeypatch):
    monkeypatch.setattr(A, "registrar_preferencia_de_contacto",
                        lambda accion: {"error": "PLATAFORMA_CAIDA"})
    respuesta = A._consentimiento_antes_del_modelo(None, _pide("dame de baja"))
    dijo = respuesta.content.parts[0].text
    assert "no pude confirmarla" in dijo
