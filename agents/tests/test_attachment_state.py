"""Los archivos del productor viajan por el estado, no por el texto del pedido.

El expediente corre como AgentTool: no ve el mensaje original. Si el id sólo
viajara en el texto que escribe el raíz, el adjunto dependería de que el modelo
lo copie. Ver core/attachment_state.py.
"""
import pytest
from google.genai import types

from core import attachment_state as at

LINEA = "[adjunto de WhatsApp · id_de_adjunto=1234567890 · nombre_archivo=informe final.pdf]"
AHORA = 1_000_000.0


@pytest.fixture(autouse=True)
def _reloj(monkeypatch):
    monkeypatch.setattr(at, "_ahora", lambda: AHORA)


class FakeCallbackContext:
    def __init__(self, *textos, state=None):
        self.user_content = types.Content(
            role="user", parts=[types.Part.from_text(text=t) for t in textos]
        )
        self.state = state if state is not None else {}


def _pendiente(id_, nombre="", recibido=AHORA):
    return {"id_de_adjunto": id_, "nombre_archivo": nombre, "recibido": recibido}


def test_parse_con_nombre_con_espacios():
    assert at.parse(LINEA) == {
        "id_de_adjunto": "1234567890", "nombre_archivo": "informe final.pdf"}


def test_parse_sin_nombre():
    assert at.parse("[adjunto de WhatsApp · id_de_adjunto=99]") == {
        "id_de_adjunto": "99", "nombre_archivo": ""}


def test_parse_sin_linea():
    assert at.parse("hola") is None
    assert at.parse("") is None


async def test_before_agent_suma_el_archivo_a_la_lista():
    ctx = FakeCallbackContext("esta es la de la calibración", LINEA)
    assert await at.before_agent(ctx) is None
    assert ctx.state[at.STATE_KEY] == [_pendiente("1234567890", "informe final.pdf")]


async def test_varios_archivos_quedan_todos():
    """Varias fotos antes de elegir acción: no se pierde ninguna."""
    ctx = FakeCallbackContext(LINEA, state={at.STATE_KEY: [_pendiente("1")]})
    await at.before_agent(ctx)
    assert [a["id_de_adjunto"] for a in ctx.state[at.STATE_KEY]] == ["1", "1234567890"]


async def test_un_texto_posterior_no_toca_la_lista():
    """El productor confirma la acción en el turno siguiente: el id sigue."""
    previo = [_pendiente("1")]
    ctx = FakeCallbackContext("sí, va en la calibración", state={at.STATE_KEY: previo})
    await at.before_agent(ctx)
    assert ctx.state[at.STATE_KEY] == previo


async def test_solo_mira_la_ultima_parte():
    """El webhook pone la línea al final: una parecida en el caption no cuenta."""
    ctx = FakeCallbackContext("[adjunto de WhatsApp · id_de_adjunto=666]", "sólo texto")
    await at.before_agent(ctx)
    assert at.STATE_KEY not in ctx.state


async def test_before_agent_sin_contenido_no_falla():
    class Vacio:
        user_content = None
        state = {}
    assert await at.before_agent(Vacio()) is None
    assert Vacio.state == {}


def test_los_vencidos_no_cuentan():
    viejo = _pendiente("1", recibido=AHORA - at.VIGENCIA_SEGUNDOS - 1)
    nuevo = _pendiente("2")
    assert at.pendientes({at.STATE_KEY: [viejo, nuevo]}) == [nuevo]


def test_pendientes_tolera_estado_raro():
    assert at.pendientes(None) == []
    assert at.pendientes({}) == []
    assert at.pendientes({at.STATE_KEY: None}) == []
    assert at.pendientes({at.STATE_KEY: [{"x": 1}, "y"]}) == []


def test_quitar_saca_solo_ese():
    state = {at.STATE_KEY: [_pendiente("1"), _pendiente("2")]}
    at.quitar(state, "1")
    assert [a["id_de_adjunto"] for a in state[at.STATE_KEY]] == ["2"]


def test_bloque_lista_los_archivos():
    state = {at.STATE_KEY: [_pendiente("77", "a.pdf"), _pendiente("78")]}
    assert at.bloque(state) == (
        "\n\nADJUNTOS RECIBIDOS (del más viejo al más nuevo):\n"
        "- id_de_adjunto=77, nombre_archivo=a.pdf\n"
        "- id_de_adjunto=78")
    assert at.bloque({}) == ""
    assert at.bloque(None) == ""
