"""La tool del menú sólo valida los límites de WhatsApp: el webhook la dibuja.

Cada límite que no se valide acá termina en un menú descartado en el webhook
(el productor recibe texto pelado) en vez de un reintento del modelo.
"""
import pytest

from core.options_tools import Opcion, ofrecer_opciones

MENU = [
    {"titulo": "Subir un verificador", "descripcion": "Foto o documento para una acción de tu plan"},
    {"titulo": "Mi avance y puntaje", "descripcion": "Cómo vas en tu plan y tu nivel"},
    {"titulo": "Qué me falta", "descripcion": "Acciones pendientes y próximas fechas"},
    {"titulo": "Conocer el estándar", "descripcion": "Qué pide, dimensiones y puntajes"},
    {"titulo": "Sustentabilidad", "descripcion": "Buenas prácticas para producir mejor"},
    {"titulo": "Registrar una labor", "descripcion": "Algo que hiciste en campo o planta"},
    {"titulo": "Hablar con el auditor", "descripcion": "Dejar o leer mensajes"},
]


def test_el_menu_principal_es_valido():
    r = ofrecer_opciones(MENU)
    assert r == {
        "ok": True,
        "data": {
            "opciones_ofrecidas": 7,
            "nota": "Las opciones ya se muestran al productor; no escribas nada más.",
        },
    }


def test_acepta_instancias_de_opcion():
    """ADK puede entregar los items ya convertidos al modelo pydantic."""
    r = ofrecer_opciones([Opcion(titulo="Sí"), Opcion(titulo="No")])
    assert r["ok"] is True


@pytest.mark.parametrize("opciones", [[], [{"titulo": f"Op {i}"} for i in range(11)]])
def test_rechaza_cero_o_mas_de_diez(opciones):
    r = ofrecer_opciones(opciones)
    assert r["ok"] is False and "entre 1 y 10" in r["error"]


def test_rechaza_titulo_vacio():
    r = ofrecer_opciones([{"titulo": "  "}])
    assert r["ok"] is False and "no tiene título" in r["error"]


def test_rechaza_titulo_de_25():
    r = ofrecer_opciones([{"titulo": "x" * 25}])
    assert r["ok"] is False and "24" in r["error"]


def test_acepta_titulo_de_24():
    assert ofrecer_opciones([{"titulo": "x" * 24}])["ok"] is True


def test_rechaza_descripcion_de_73():
    r = ofrecer_opciones([{"titulo": "A", "descripcion": "x" * 73}])
    assert r["ok"] is False and "72" in r["error"]


def test_rechaza_titulos_repetidos_sin_importar_mayusculas():
    r = ofrecer_opciones([{"titulo": "Qué me falta"}, {"titulo": " qué me falta "}])
    assert r["ok"] is False and "repetido" in r["error"]


def test_rechaza_boton_de_21():
    r = ofrecer_opciones([{"titulo": "A"}], boton="x" * 21)
    assert r["ok"] is False and "20" in r["error"]


def test_boton_vacio_usa_el_de_siempre():
    """Un framework de function-calling puede mandar "" por un opcional."""
    assert ofrecer_opciones([{"titulo": "A"}], boton="")["ok"] is True
