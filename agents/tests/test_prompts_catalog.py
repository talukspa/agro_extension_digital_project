"""Los prompts del catálogo, ya sobre Postgres.

Cada test de acá corresponde a una forma concreta de romperse en silencio. Los
nombres de columna de Postgres en un ejemplo de SQL no dan error: le enseñan al
modelo a escribir consultas que fallan, o peor, consultas que devuelven cero filas
y parecen una respuesta.
"""
import pytest

from core import prompts

AGENTES = ["agent_pp", "agent_aa"]

# Todo lo que era de Postgres y no puede sobrevivir en el prompt nuevo.
COLUMNAS_VIEJAS = [
    "estandar_pp", "estandar_aa", "recursos_pp", "recursos_aa",
    "buena_practica", "medio_de_verificacion", "link_recursos",
    "Postgres", "bigquery",
]


def _plano(texto: str) -> str:
    """Normaliza los saltos, para que un reformateo del .md no rompa un test."""
    return " ".join(texto.split())


@pytest.mark.parametrize("agente", AGENTES)
def test_la_instruccion_del_catalogo_existe(agente):
    assert len(prompts.catalog_instruction(agente)) > 300


@pytest.mark.parametrize("agente", AGENTES)
def test_la_descripcion_del_catalogo_existe(agente):
    assert len(prompts.catalog_description(agente)) > 150


@pytest.mark.parametrize("agente", AGENTES)
@pytest.mark.parametrize("vieja", COLUMNAS_VIEJAS)
def test_no_menciona_nada_de_bigquery(agente, vieja):
    """Un ejemplo con los nombres viejos le enseña al modelo a escribir consultas
    que fallan."""
    assert vieja not in prompts.catalog_instruction(agente)


@pytest.mark.parametrize("agente", AGENTES)
def test_nombra_las_dos_tablas_de_postgres(agente):
    texto = prompts.catalog_instruction(agente)
    assert "questions" in texto
    assert "standards" in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_el_estandar_se_resuelve_por_el_join(agente):
    """`questions.standard_code` está VACÍO en las 264 filas: filtrar por esa
    columna devuelve cero filas SIN error, que es el peor modo de falla posible.
    El prompt tiene que mandar al JOIN y desaconsejar la columna por su nombre."""
    plano = _plano(prompts.catalog_instruction(agente))
    assert "standard_id" in plano
    assert "standards.code" in plano
    # y tiene que advertirlo explícitamente, no sólo omitirlo
    assert "standard_code" in plano
    assert "NO LA USES" in plano or "no la uses" in plano.lower()
    # la advertencia sirve si dice la consecuencia
    assert "cero filas" in plano


@pytest.mark.parametrize("agente", AGENTES)
def test_no_ensena_a_filtrar_por_standard_code(agente):
    """Un ejemplo de SQL con `WHERE standard_code = ...` es peor que no tener
    ejemplo: el modelo copia el que ve."""
    plano = _plano(prompts.catalog_instruction(agente))
    for mal in ("WHERE standard_code =", "where standard_code =",
                "AND standard_code =", "and standard_code ="):
        assert mal not in plano


@pytest.mark.parametrize("agente", AGENTES)
def test_ofrece_las_dos_fuentes_de_material_de_apoyo(agente):
    """`link` es una URL por pregunta; `resources` trae tipo, detalle y varias
    (pdf, web, curso). Postgres sólo tenía la primera, así que el prompt viejo no
    podía nombrar la segunda."""
    plano = _plano(prompts.catalog_instruction(agente))
    # las DOS descritas como fuentes distintas, no sólo nombradas de pasada
    assert "`link` — una URL por acción" in plano
    assert "`resources` — jsonb con el material completo" in plano
    assert "no hay otra columna" not in plano


@pytest.mark.parametrize("agente", AGENTES)
def test_dice_que_solo_ve_las_activas(agente):
    """El rol filtra `is_active` en su política, así que el agente no puede ver
    requisitos derogados. El prompt tiene que decirlo, o el modelo va a escribir
    el filtro por su cuenta y a explicarle al productor una restricción que no
    existe."""
    plano = _plano(prompts.catalog_instruction(agente))
    assert "is_active" in plano
    assert "acciones **activas**" in plano
    # y la ausencia del contrario: "activas" sola sobrevive dentro de
    # "activas y derogadas", que es lo opuesto de la regla
    for contrario in ("y derogadas", "activas y derogadas", "todas las acciones,"):
        assert contrario not in plano, contrario


@pytest.mark.parametrize("agente", AGENTES)
def test_la_descripcion_separa_del_expediente(agente):
    """La frontera que la medición de enrutamiento comprueba: "la acción P001" es
    del catálogo, "la acción P001 de mi plan" es del expediente."""
    plano = _plano(prompts.catalog_description(agente))
    assert "plan" in plano.lower()
    assert "expediente" in plano.lower()


@pytest.mark.parametrize("agente", AGENTES)
def test_la_descripcion_no_reclama_lo_conceptual(agente):
    """Era la única duda de enrutamiento que quedaba: `bq_description.md` citaba
    "huella hídrica" como ejemplo propio mientras `rag_description.md` reclamaba
    el apoyo conceptual. La descripción nueva no puede reclamar explicar
    conceptos: eso es de RAG."""
    plano = _plano(prompts.catalog_description(agente)).lower()
    assert "explicar el concepto" not in plano
    assert "apoyo conceptual" not in plano


@pytest.mark.parametrize("agente", AGENTES)
def test_el_codigo_de_ejemplo_es_del_estandar_del_agente(agente):
    """PP usa P001 y AA usa A001, como ya hace el resto del repo."""
    texto = prompts.catalog_instruction(agente)
    esperado = "P0" if agente == "agent_pp" else "A0"
    assert esperado in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_la_instruccion_incluye_la_regla_de_whatsapp(agente):
    compartido = prompts._read("shared", "whatsapp_plain.md")
    assert _plano(compartido)[:40] in _plano(prompts.catalog_instruction(agente))
