"""El archivo del productor viaja por el estado, no por el texto del pedido.

El expediente corre como AgentTool: no ve el mensaje original. Si el id sólo
viajara en el texto que escribe el raíz, el adjunto dependería de que el modelo
lo copie. Ver core/attachment_state.py.
"""
from google.genai import types

from core import attachment_state

LINEA = "[adjunto de WhatsApp · id_de_adjunto=1234567890 · nombre_archivo=informe.pdf]"


class FakeCallbackContext:
    def __init__(self, *textos, state=None):
        self.user_content = types.Content(
            role="user", parts=[types.Part.from_text(text=t) for t in textos]
        )
        self.state = state if state is not None else {}


def test_parse_con_nombre():
    assert attachment_state.parse(LINEA) == {
        "id_de_adjunto": "1234567890", "nombre_archivo": "informe.pdf"}


def test_parse_sin_nombre():
    assert attachment_state.parse("[adjunto de WhatsApp · id_de_adjunto=99]") == {
        "id_de_adjunto": "99", "nombre_archivo": ""}


def test_parse_sin_linea():
    assert attachment_state.parse("hola") is None
    assert attachment_state.parse("") is None


async def test_before_agent_guarda_el_archivo_en_el_estado():
    ctx = FakeCallbackContext("esta es la de la calibración", LINEA)
    assert await attachment_state.before_agent(ctx) is None
    assert ctx.state[attachment_state.STATE_KEY] == {
        "id_de_adjunto": "1234567890", "nombre_archivo": "informe.pdf"}


async def test_un_texto_posterior_no_borra_el_archivo_pendiente():
    """El productor confirma la acción en el turno siguiente: el id sigue."""
    previo = {"id_de_adjunto": "1", "nombre_archivo": ""}
    ctx = FakeCallbackContext("sí, va en la calibración",
                              state={attachment_state.STATE_KEY: previo})
    await attachment_state.before_agent(ctx)
    assert ctx.state[attachment_state.STATE_KEY] == previo


async def test_un_archivo_nuevo_reemplaza_al_anterior():
    ctx = FakeCallbackContext(LINEA, state={
        attachment_state.STATE_KEY: {"id_de_adjunto": "1", "nombre_archivo": ""}})
    await attachment_state.before_agent(ctx)
    assert ctx.state[attachment_state.STATE_KEY]["id_de_adjunto"] == "1234567890"


async def test_before_agent_sin_contenido_no_falla():
    class Vacio:
        user_content = None
        state = {}
    assert await attachment_state.before_agent(Vacio()) is None
    assert Vacio.state == {}


def test_bloque_con_y_sin_archivo():
    state = {attachment_state.STATE_KEY: {"id_de_adjunto": "77", "nombre_archivo": "a.pdf"}}
    assert attachment_state.bloque(state) == (
        "\n\nADJUNTO RECIBIDO: id_de_adjunto=77, nombre_archivo=a.pdf")
    assert attachment_state.bloque({}) == ""
    assert attachment_state.bloque(None) == ""
    # Borrado por adjuntar_evidencia: el estado queda en None.
    assert attachment_state.bloque({attachment_state.STATE_KEY: None}) == ""
