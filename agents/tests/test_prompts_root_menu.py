"""Las reglas del menú en el prompt raíz.

Mismo estilo que tests/test_prompts_record.py: cada regla afirma que la frase
correcta está y que un marcador antónimo natural NO está.
"""
import pytest

from core import prompts

AGENTES = ["agent_pp", "agent_aa"]
MENU = [
    ("Subir un verificador", "Foto o documento para una acción de tu plan"),
    ("Mi avance y puntaje", "Cómo vas en tu plan y tu nivel"),
    ("Qué me falta", "Acciones pendientes y próximas fechas"),
    ("Conocer el estándar", "Qué pide, dimensiones y puntajes"),
    ("Sustentabilidad", "Buenas prácticas para producir mejor"),
    ("Registrar una labor", "Algo que hiciste en campo o planta"),
    ("Hablar con el auditor", "Dejar o leer mensajes"),
]


def _plano(texto: str) -> str:
    return " ".join(texto.split())


@pytest.mark.parametrize("agente", AGENTES)
def test_el_saludo_obliga_el_menu_principal(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "llama SIEMPRE a `ofrecer_opciones` con este menú principal" in texto
    assert "sin menú" not in texto.lower()


@pytest.mark.parametrize("agente", AGENTES)
@pytest.mark.parametrize("titulo,descripcion", MENU)
def test_el_menu_principal_tiene_las_siete_opciones(agente, titulo, descripcion):
    texto = _plano(prompts.root_instruction(agente))
    assert f'titulo "{titulo}", descripcion "{descripcion}"' in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_los_titulos_del_menu_caben_en_whatsapp(agente):
    for titulo, descripcion in MENU:
        assert len(titulo) <= 24 and len(descripcion) <= 72


@pytest.mark.parametrize("agente", AGENTES)
def test_cierra_con_siguientes_pasos_no_con_la_frase_fija(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "llama a `ofrecer_opciones` con 2 a 4 siguientes pasos" in texto
    assert "¿Hay algo más en lo que pueda ayudarte" not in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_el_texto_no_repite_las_opciones(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "Tu texto NUNCA repite ni numera las opciones" in texto
    assert "numéralas" not in texto.lower()


@pytest.mark.parametrize("agente", AGENTES)
def test_no_ofrece_opciones_cuando_el_productor_tiene_que_escribir(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "NO la uses cuando el productor esté en medio de algo que tiene que escribir él" in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_el_toque_llega_como_su_mensaje(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "trátalo como si lo hubiera escrito" in texto
