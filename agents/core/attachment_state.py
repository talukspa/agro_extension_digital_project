"""El archivo que mandó el productor, guardado en el estado de la sesión.

POR QUÉ NO BASTA CON LA LÍNEA EN EL MENSAJE

El webhook agrega al mensaje del productor una línea
`[adjunto de WhatsApp · id_de_adjunto=… · nombre_archivo=…]` (ver
`agent_client._media_label` en webhook-application). Esa línea la ve el RAÍZ.
Pero quien adjunta es el sub-agente del expediente, y corre como `AgentTool`:
ADK le abre una sesión NUEVA y le pasa sólo el texto del `request` que escribe
el raíz (google/adk/tools/agent_tool.py, `run_async`). No ve el archivo, ni la
línea, ni la conversación. Si el raíz no copia el id en el pedido —y nada se lo
garantiza— `adjuntar_evidencia` no tiene con qué llamar a /api/agent/evidence.

Lo que `AgentTool` SÍ copia a la sesión del sub-agente es el estado
(`tool_context.state`, menos las llaves `_adk*`), y devuelve al padre los
cambios que el sub-agente hace en él. Por eso el id viaja por el estado:

- `before_agent` (callback del raíz) lee la línea del mensaje que llega y
  guarda `{"id_de_adjunto", "nombre_archivo"}` en `STATE_KEY`.
- `bloque` agrega "ADJUNTO RECIBIDO" a la instrucción del expediente.
- `adjuntar_evidencia` lo toma de ahí si el modelo no le pasa el id, y lo
  borra cuando el adjunto quedó guardado.

El estado sobrevive entre turnos: si el productor confirma la acción en el
mensaje siguiente, el id sigue ahí.
"""
from __future__ import annotations

import re
from typing import Any, Optional

STATE_KEY = "adjunto_pendiente"

# El formato exacto de `_media_label`: campos separados por " · ".
_LINEA = re.compile(
    r"\[adjunto de WhatsApp · id_de_adjunto=([^\s·\]]+)"
    r"(?: · nombre_archivo=([^\]]+))?\]"
)


def parse(texto: str) -> Optional[dict[str, str]]:
    """La línea del webhook como dict, o None si el texto no la trae."""
    m = _LINEA.search(texto or "")
    if not m:
        return None
    return {"id_de_adjunto": m.group(1), "nombre_archivo": (m.group(2) or "").strip()}


async def before_agent(callback_context: Any) -> None:
    """Callback del raíz: si el mensaje trae un archivo, lo deja en el estado.

    Sólo escribe cuando hay línea: un mensaje de texto posterior ("sí, va en la
    calibración") no borra el archivo que todavía falta guardar. Devuelve None
    para que el turno siga normal.
    """
    content = getattr(callback_context, "user_content", None)
    for part in getattr(content, "parts", None) or []:
        adjunto = parse(getattr(part, "text", None) or "")
        if adjunto:
            callback_context.state[STATE_KEY] = adjunto
    return None


def pendiente(state: Any) -> Optional[dict[str, str]]:
    """El archivo por guardar, o None. Tolera estado ausente o borrado."""
    if state is None:
        return None
    valor = state.get(STATE_KEY)
    if isinstance(valor, dict) and valor.get("id_de_adjunto"):
        return valor
    return None


def bloque(state: Any) -> str:
    """La línea que se agrega a la instrucción del expediente, o ""."""
    adjunto = pendiente(state)
    if not adjunto:
        return ""
    linea = f"\n\nADJUNTO RECIBIDO: id_de_adjunto={adjunto['id_de_adjunto']}"
    if adjunto.get("nombre_archivo"):
        linea += f", nombre_archivo={adjunto['nombre_archivo']}"
    return linea
