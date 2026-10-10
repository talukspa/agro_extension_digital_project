"""Del `ofrecer_opciones` del agente al mensaje de WhatsApp (puro, sin red)."""
import pytest

from whatsapp_webhook.interactive import (
    DEFAULT_BODY,
    AgentReply,
    Option,
    build_reply_messages,
    numbered_fallback,
    parse_options,
)

SIETE = [Option(f"Opción {i}", f"Descripción {i}") for i in range(1, 8)]


# ----------------------------------------------------------------- parse_options
def test_parse_options_ok():
    args = {"opciones": [{"titulo": "Qué me falta", "descripcion": "Pendientes"},
                         {"titulo": "Menú principal"}], "boton": "Ver"}
    assert parse_options(args) == (
        [Option("Qué me falta", "Pendientes"), Option("Menú principal", "")], "Ver"
    )


def test_parse_options_boton_vacio_usa_el_de_siempre():
    assert parse_options({"opciones": [{"titulo": "A"}], "boton": ""})[1] == "Ver opciones"


@pytest.mark.parametrize("args", [
    None,
    "texto",
    {},
    {"opciones": []},
    {"opciones": [{"titulo": f"O{i}"} for i in range(11)]},
    {"opciones": [{"titulo": ""}]},
    {"opciones": [{"titulo": "x" * 25}]},
    {"opciones": [{"titulo": "A", "descripcion": "x" * 73}]},
    {"opciones": [{"titulo": "A"}, {"titulo": " a "}]},
    {"opciones": ["A"]},
    {"opciones": [{"titulo": "A"}], "boton": "x" * 21},
])
def test_parse_options_rechaza_lo_que_whatsapp_no_acepta(args):
    assert parse_options(args) is None


# ---------------------------------------------------------- build_reply_messages
def test_sin_opciones_es_texto():
    assert build_reply_messages(AgentReply("Hola")) == [
        {"type": "text", "text": {"body": "Hola", "preview_url": False}}
    ]


def test_tres_cortas_son_botones():
    msgs = build_reply_messages(AgentReply("¿Seguimos?", [Option("Sí"), Option("No"), Option("Menú principal")]))
    assert len(msgs) == 1
    assert msgs[0]["interactive"]["type"] == "button"
    assert msgs[0]["interactive"]["body"]["text"] == "¿Seguimos?"


def test_tres_con_un_titulo_de_21_es_lista():
    msgs = build_reply_messages(AgentReply("Elige", [Option("A"), Option("B"), Option("x" * 21)]))
    assert msgs[0]["interactive"]["type"] == "list"


def test_siete_es_lista_con_descripciones_y_boton():
    msgs = build_reply_messages(AgentReply("Hola", SIETE, "Ver opciones"))
    inter = msgs[0]["interactive"]
    assert inter["type"] == "list"
    assert inter["action"]["button"] == "Ver opciones"
    assert inter["action"]["sections"][0]["rows"][0] == {
        "id": "opt_1", "title": "Opción 1", "description": "Descripción 1"
    }


def test_texto_largo_va_aparte_y_el_interactivo_con_cuerpo_corto():
    largo = "x" * 1100
    msgs = build_reply_messages(AgentReply(largo, SIETE))
    assert msgs[0] == {"type": "text", "text": {"body": largo, "preview_url": False}}
    assert msgs[1]["interactive"]["body"]["text"] == DEFAULT_BODY


def test_sin_texto_con_opciones_usa_el_cuerpo_por_defecto():
    """Review Focus 1: el modelo llamó la tool pero no escribió nada."""
    msgs = build_reply_messages(AgentReply("", SIETE))
    assert len(msgs) == 1
    assert msgs[0]["interactive"]["body"]["text"] == DEFAULT_BODY


# --------------------------------------------------------------- numbered_fallback
def test_fallback_numerado_con_texto():
    body = numbered_fallback(AgentReply("Hola", [Option("Sí"), Option("No")]), include_text=True)["text"]["body"]
    assert body.startswith("Hola")
    assert "1. Sí" in body and "2. No" in body
    # Review Focus 5: le dice cómo contestar.
    assert "Responde con el número" in body


def test_fallback_numerado_sin_texto_no_lo_repite():
    body = numbered_fallback(AgentReply("Hola", [Option("Sí")]), include_text=False)["text"]["body"]
    assert "Hola" not in body
    assert "1. Sí" in body
