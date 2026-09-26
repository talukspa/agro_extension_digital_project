"""Los prompts del expediente existen para los dos agentes y dicen lo que deben."""
import pytest

from core import prompts


def _sin_saltos(texto: str) -> str:
    """Normaliza el wrap de línea del .md: una frase distintiva no debe
    depender de caer en una sola línea física del archivo fuente."""
    return " ".join(texto.split())


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_la_instruccion_del_expediente_existe(agente):
    texto = prompts.record_instruction(agente)
    assert len(texto) > 200


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_la_descripcion_del_expediente_existe(agente):
    assert len(prompts.record_description(agente)) > 100


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_no_anuncia_escrituras_en_futuro(agente):
    """Medido: decía "voy a adjuntar" y cerraba el turno sin adjuntar."""
    texto = prompts.record_instruction(agente)
    assert "en pasado" in texto
    assert "NUNCA anuncies en futuro" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_prohibe_pedir_el_codigo(agente):
    """Medido contra la base real: con la lista vacía pedía "el código"."""
    assert 'La palabra "código" no va nunca en un mensaje tuyo' in \
        prompts.record_instruction(agente)


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_la_instruccion_incluye_la_regla_de_whatsapp(agente):
    """Comparte el estilo con el resto: mensajes cortos, sin markdown."""
    compartido = prompts._read("shared", "whatsapp_plain.md")[:60]
    assert compartido.strip()[:40] in prompts.record_instruction(agente)


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_respaldo_cargado_no_es_accion_cumplida(agente):
    """Medido: subir un archivo se reportaba como acción "ya cumplida"."""
    texto = prompts.record_instruction(agente)
    assert "no significa que la acción quede cumplida" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_nivel_oficial_es_el_congelado(agente):
    """Medido: un recálculo distinto se presentaba como si fuera el nivel oficial."""
    texto = _sin_saltos(prompts.record_instruction(agente))
    assert "congelado al autodiagnóstico" in texto
    assert "no lo presentes como si fuera el resultado" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_primera_llamada_a_adjuntar_evidencia_deja_estandar_vacio(agente):
    """Medido: completar `estandar` a mano archivaba el respaldo en el plan
    equivocado, donde nadie lo ve."""
    texto = prompts.record_instruction(agente)
    assert "PRIMERA llamada a `adjuntar_evidencia`" in texto
    assert "`estandar` VACÍO" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_ubicar_documento_pide_lista_con_las_que_ya_tienen_respaldo(agente):
    """Medido: mirar sólo las acciones sin respaldo forzaba el calce contra la
    única que quedaba visible."""
    texto = prompts.record_instruction(agente)
    assert "`incluir_las_que_ya_tienen_respaldo` en True" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_lista_vacia_no_pide_el_codigo(agente):
    """Medido contra la base real: con la lista vacía pedía "el código"."""
    texto = _sin_saltos(prompts.record_instruction(agente))
    assert "Si la lista vino vacía, pregúntale simplemente de qué se trata." in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_nombres_de_estandar_sin_codigo_en_mayusculas(agente):
    """Los dos estándares se nombran así para el productor, nunca con el
    código en mayúsculas."""
    texto = _sin_saltos(prompts.record_instruction(agente))
    assert '"Producción Primaria" y "Adecuación Agroindustrial"' in texto
    assert "son los códigos que usan tus herramientas" in texto
    assert "nunca en un mensaje" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_la_baja_se_registra_primero_y_se_confirma_despues(agente):
    """Medido: la baja es un requisito legal, no se puede anunciar sin haberla
    registrado antes."""
    texto = prompts.record_instruction(agente)
    assert "regístrala con la herramienta PRIMERO y confírmasela DESPUÉS" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_solo_ve_el_expediente_de_este_productor(agente):
    texto = prompts.record_instruction(agente)
    assert "el expediente de ESTE productor" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_no_incluye_preserve_citations(agente):
    """Un dato del expediente del productor no se cita, es suyo — eso es para
    respuestas de RAG con fuente."""
    citas = prompts._read("shared", "preserve_citations.md")[:40].strip()
    assert citas in prompts.root_instruction(agente)
    assert citas not in prompts.record_instruction(agente)
