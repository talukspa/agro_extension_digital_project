"""Opciones tocables de WhatsApp: de la llamada `ofrecer_opciones` del agente a
botones o lista, con fallback a texto numerado.

El agente decide QUÉ ofrecer (agents/core/options_tools.py); acá sólo se dibuja.
Los límites se repiten a propósito: el agente es otro deploy y no se puede
importar, y un menú que la Cloud API rechaza deja al productor sin respuesta.
Ver docs/superpowers/specs/2026-10-09-menu-opciones-whatsapp-design.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .external_services.whatsapp_client import (
    create_button_message,
    create_list_message,
    create_text_message,
)

MAX_OPTIONS = 10
MAX_BUTTONS = 3
MAX_BUTTON_TITLE = 20
MAX_ROW_TITLE = 24
MAX_DESCRIPTION = 72
MAX_BUTTON_LABEL = 20
MAX_BODY = 1024
DEFAULT_BUTTON_LABEL = "Ver opciones"
DEFAULT_BODY = "¿Qué quieres hacer ahora?"


@dataclass(frozen=True)
class Option:
    title: str
    description: str = ""


@dataclass
class AgentReply:
    """La respuesta del agente lista para WhatsApp: texto y, si las ofreció, opciones."""

    text: str
    options: Optional[list[Option]] = None
    button: str = DEFAULT_BUTTON_LABEL


def parse_options(args: Any) -> Optional[tuple[list[Option], str]]:
    """Valida los `args` de una llamada a `ofrecer_opciones`. None si no sirven.

    Mismos límites que agents/core/options_tools.py. Se re-validan porque el
    webhook ve la llamada aunque la tool la haya rechazado con `ok: False`.
    """
    if not isinstance(args, dict):
        return None
    raw = args.get("opciones")
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_OPTIONS:
        return None
    options: list[Option] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            return None
        title = str(item.get("titulo") or "").strip()
        description = str(item.get("descripcion") or "").strip()
        if not title or len(title) > MAX_ROW_TITLE or len(description) > MAX_DESCRIPTION:
            return None
        if title.casefold() in seen:
            return None
        seen.add(title.casefold())
        options.append(Option(title, description))
    button = str(args.get("boton") or "").strip() or DEFAULT_BUTTON_LABEL
    if len(button) > MAX_BUTTON_LABEL:
        return None
    return options, button


def build_reply_messages(reply: AgentReply) -> list[dict]:
    """Los mensajes a enviar, en orden.

    Sin opciones: el texto. Con opciones: botones si son ≤3 y caben en 20
    caracteres, lista si no. Un texto que no cabe en el cuerpo de un
    interactivo (1024) sale antes como texto y el interactivo lleva un cuerpo
    corto; lo mismo si el agente no escribió nada.
    """
    text = reply.text.strip()
    if not reply.options:
        return [create_text_message(text)]
    messages: list[dict] = []
    body = text
    if len(text) > MAX_BODY:
        messages.append(create_text_message(text))
        body = DEFAULT_BODY
    elif not text:
        body = DEFAULT_BODY
    if len(reply.options) <= MAX_BUTTONS and all(
        len(o.title) <= MAX_BUTTON_TITLE for o in reply.options
    ):
        messages.append(create_button_message(body, [o.title for o in reply.options]))
    else:
        messages.append(create_list_message(
            body, reply.button, [(o.title, o.description) for o in reply.options]
        ))
    return messages


def numbered_fallback(reply: AgentReply, include_text: bool) -> dict:
    """Las opciones como texto numerado, para cuando el interactivo no salió.

    `include_text=False` cuando el texto ya se mandó aparte (no se repite).
    """
    parts: list[str] = []
    if include_text and reply.text.strip():
        parts.append(reply.text.strip())
    parts.append("\n".join(f"{i}. {o.title}" for i, o in enumerate(reply.options or [], 1)))
    parts.append("Responde con el número o escríbeme lo que necesitas.")
    return create_text_message("\n\n".join(parts))
