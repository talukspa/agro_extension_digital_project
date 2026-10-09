"""El menú de opciones tocables: el agente raíz decide qué ofrecer, el webhook
lo dibuja como botones o lista de WhatsApp.

Esta tool NO envía nada. El webhook lee los `args` de la llamada en el stream de
Agent Runtime (`webhook-application/.../agent_client.send_to_agent`). Por eso
vive en el RAÍZ: los sub-agentes corren como `AgentTool` y sus eventos internos
no llegan a ese stream.

Lo único que hace es validar los límites de la Cloud API para que el modelo
corrija con el contrato {ok, error} de core/retry_plugin.py ANTES de que el
webhook tenga que descartar el menú. Nunca trunca: un título cortado a la mitad
es peor que un reintento. El webhook re-valida con los mismos números (otro
deploy, no puede importar este módulo).

Ver docs/superpowers/specs/2026-10-09-menu-opciones-whatsapp-design.md.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

MAX_OPCIONES = 10
MAX_TITULO = 24
MAX_DESCRIPCION = 72
MAX_BOTON = 20


class Opcion(BaseModel):
    titulo: str
    descripcion: str = ""


def _como_dict(opcion: Any) -> dict:
    """ADK puede entregar cada item como `Opcion` o como dict crudo."""
    if isinstance(opcion, BaseModel):
        return opcion.model_dump()
    return opcion if isinstance(opcion, dict) else {}


def _error(motivo: str) -> dict:
    return {"ok": False, "error": motivo}


def ofrecer_opciones(opciones: list[Opcion], boton: str = "Ver opciones") -> dict:
    """Muestra al productor opciones tocables (botones o lista de WhatsApp)
    junto a tu respuesta.

    Úsala al saludar (con el menú principal), al terminar una respuesta (2 a 4
    siguientes pasos), cuando el productor no sabe qué pedir, o para que elija
    entre varias cosas. Tu texto NO repite las opciones: van sólo acá. Cuando
    toque una, te llega como su mensaje el título de la opción.

    Args:
        opciones: de 1 a 10. `titulo` de hasta 24 caracteres, sin repetir;
            `descripcion` opcional, de hasta 72.
        boton: el texto del botón que abre la lista, hasta 20 caracteres.
    """
    items = [_como_dict(o) for o in (opciones or [])]
    if not 1 <= len(items) <= MAX_OPCIONES:
        return _error(
            f"Ofrece entre 1 y {MAX_OPCIONES} opciones; mandaste {len(items)}."
        )
    vistos: set[str] = set()
    for i, opcion in enumerate(items, 1):
        titulo = str(opcion.get("titulo") or "").strip()
        descripcion = str(opcion.get("descripcion") or "").strip()
        if not titulo:
            return _error(f"La opción {i} no tiene título.")
        if len(titulo) > MAX_TITULO:
            return _error(
                f'El título "{titulo}" tiene {len(titulo)} caracteres; el máximo '
                f"es {MAX_TITULO}. Acórtalo."
            )
        if len(descripcion) > MAX_DESCRIPCION:
            return _error(
                f'La descripción de "{titulo}" tiene {len(descripcion)} caracteres; '
                f"el máximo es {MAX_DESCRIPCION}. Acórtala."
            )
        if titulo.casefold() in vistos:
            return _error(f'El título "{titulo}" está repetido.')
        vistos.add(titulo.casefold())
    # Vacío = el de siempre: el webhook pone "Ver opciones".
    if len((boton or "").strip()) > MAX_BOTON:
        return _error(f"El texto del botón debe tener hasta {MAX_BOTON} caracteres.")
    return {"ok": True, "data": {"opciones_ofrecidas": len(items)}}


TOOLS: list = [ofrecer_opciones]
