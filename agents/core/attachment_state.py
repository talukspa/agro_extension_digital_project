"""Los archivos que mandó el productor, guardados en el estado de la sesión.

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
cambios que el sub-agente hace en él. Por eso los ids viajan por el estado:

- `before_agent` (callback del raíz) lee la línea del mensaje que llega y la
  agrega a la lista `STATE_KEY`.
- `bloque` agrega "ADJUNTOS RECIBIDOS" a la instrucción del expediente.
- `adjuntar_evidencia` toma el id de ahí y saca de la lista el que guardó.

Es una LISTA porque el productor puede mandar varias fotos (cada una llega en
su propio mensaje) antes de decir a qué acción va cada una. Cada archivo vence
a las `VIGENCIA_SEGUNDOS`: una foto mandada para otra cosa (una duda sobre una
plaga) no debe quedar esperando días para colgarse de la acción equivocada.
"""
from __future__ import annotations

import re
import time
from typing import Any, Optional

STATE_KEY = "adjuntos_pendientes"
VIGENCIA_SEGUNDOS = 24 * 60 * 60
MAX_PENDIENTES = 10

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


def _ahora() -> float:
    """Punto de inyección del reloj para los tests."""
    return time.time()


def pendientes(state: Any) -> list[dict[str, Any]]:
    """Los archivos por guardar que siguen vigentes, del más viejo al más nuevo."""
    if state is None:
        return []
    valor = state.get(STATE_KEY)
    if not isinstance(valor, list):
        return []
    limite = _ahora() - VIGENCIA_SEGUNDOS
    return [
        a for a in valor
        if isinstance(a, dict) and a.get("id_de_adjunto")
        and float(a.get("recibido", 0)) >= limite
    ]


async def before_agent(callback_context: Any) -> None:
    """Callback del raíz: si el mensaje trae un archivo, lo suma a la lista.

    Sólo mira la ÚLTIMA parte de texto, que es donde el webhook pone la línea:
    un productor que escriba una línea parecida en el caption no inventa un
    archivo. Un mensaje sin archivo no toca la lista, porque el productor puede
    confirmar la acción en el turno siguiente. Devuelve None para que el turno
    siga normal.
    """
    content = getattr(callback_context, "user_content", None)
    textos = [getattr(p, "text", None) for p in (getattr(content, "parts", None) or [])]
    textos = [t for t in textos if t]
    adjunto = parse(textos[-1]) if textos else None
    if not adjunto:
        return None
    lista = [a for a in pendientes(callback_context.state)
             if a["id_de_adjunto"] != adjunto["id_de_adjunto"]]
    lista.append({**adjunto, "recibido": _ahora()})
    callback_context.state[STATE_KEY] = lista[-MAX_PENDIENTES:]
    return None


def quitar(state: Any, id_de_adjunto: str) -> None:
    """Saca de la lista el archivo que ya quedó guardado (y los vencidos)."""
    if state is None:
        return
    state[STATE_KEY] = [a for a in pendientes(state)
                        if a["id_de_adjunto"] != id_de_adjunto]


def bloque(state: Any) -> str:
    """Lo que se agrega a la instrucción del expediente, o ""."""
    lista = pendientes(state)
    if not lista:
        return ""
    lineas = ["", "", "ADJUNTOS RECIBIDOS (del más viejo al más nuevo):"]
    for a in lista:
        linea = f"- id_de_adjunto={a['id_de_adjunto']}"
        if a.get("nombre_archivo"):
            linea += f", nombre_archivo={a['nombre_archivo']}"
        lineas.append(linea)
    return "\n".join(lineas)
