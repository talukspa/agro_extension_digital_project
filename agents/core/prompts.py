"""Plain-Python prompt composition. No Jinja, no template engine.

Prompts are resolved relative to this file so they work both locally (cwd =
agents/) and inside the deployed engine (where `core` is shipped via
extra_packages and cwd differs).
"""
import os

_HERE = os.path.dirname(__file__)
_PROMPTS = os.path.join(_HERE, "prompts")


def _read(*parts: str) -> str:
    with open(os.path.join(_PROMPTS, *parts), encoding="utf-8") as f:
        return f.read()


def _join(*chunks: str) -> str:
    return "\n\n".join(c.strip() for c in chunks if c and c.strip())


def root_instruction(agent: str) -> str:
    """Root supervisor prompt: domain role + plain-text rule + citation passthrough."""
    return _join(
        _read(agent, "root.md"),
        _read("shared", "whatsapp_plain.md"),
        _read("shared", "preserve_citations.md"),
    )


def rag_instruction(agent: str) -> str:
    """RAG sub-agent prompt: domain retrieval rules + shared citation format."""
    return _join(_read(agent, "rag.md"), _read("shared", "rag_citations.md"))


def rag_description(agent: str) -> str:
    return _read(agent, "rag_description.md")


def record_instruction(agent: str) -> str:
    """Prompt del sub-agente EXPEDIENTE: reglas del expediente + estilo WhatsApp.

    Sin `preserve_citations.md` a propósito: eso es para respuestas de RAG con
    fuente. Un dato del expediente del productor no se cita, es suyo.

    REDUNDANCIA CONOCIDA, PENDIENTE — no cortar sin medir: al menos 5 reglas de
    `record.md` están casi duplicadas en el docstring de la tool que las aplica
    (y el docstring completo, `Args` incluidos, le llega al modelo en cada
    turno igual que el prompt):

    - `adjuntar_evidencia`: dejar `estandar` vacío en la PRIMERA llamada.
    - `adjuntar_evidencia`: adjuntar no significa que la acción quede cumplida.
    - `listar_acciones_pendientes`: `incluir_las_que_ya_tienen_respaldo`.
    - `obtener_nivel_de_certificacion`: nivel oficial congelado vs recálculo.
    - `registrar_preferencia_de_contacto`: registrar antes de confirmar.

    El comportamiento medido (9/10 y 6/6, ver Task 5) se midió con la regla en
    los DOS lugares. Cortarla de uno es una apuesta de presupuesto de atención
    contra un número ya medido — la Task 10 mide comportamiento con el modelo
    real; ahí se decide con un número a la vista, no antes. Si vas a tocar
    esto sin esa medición, no lo hagas; si la vas a agregar por sexta vez,
    revisa esta lista primero.
    """
    return _join(
        _read(agent, "record.md"),
        _read("shared", "whatsapp_plain.md"),
    )


def record_description(agent: str) -> str:
    return _read(agent, "record_description.md")


def catalog_instruction(agent: str) -> str:
    """Prompt del sub-agente CATÁLOGO: el estándar en abstracto, sobre Postgres.

    Sin `preserve_citations.md`: el catálogo devuelve filas de una tabla, no
    pasajes con fuente. Las citas son de RAG.
    """
    return _join(
        _read(agent, "catalog.md"),
        _read("shared", "whatsapp_plain.md"),
    )


def catalog_description(agent: str) -> str:
    return _read(agent, "catalog_description.md")
