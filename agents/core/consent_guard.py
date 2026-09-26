"""La baja de WhatsApp, registrada antes de que el modelo pueda contestar sin
registrarla.

POR QUÉ NO ALCANZA LA INSTRUCCIÓN: medido sobre 5 corridas del mismo mensaje
("no me escriban más por favor"), 2 veces el agente respondió "Registré tu
preferencia para no recibir más mensajes" sin haber llamado a ninguna
herramienta. Reforzar la instrucción lo bajó de 5/5 a 2/5, no a 0.

El productor se queda creyendo que se dio de baja y sigue dado de alta. Eso es
un incumplimiento legal, no una respuesta imperfecta, así que no pasa por el
modelo: se reconoce la frase, se registra, y se devuelve la confirmación sin
consultarlo.

El modelo sigue atendiendo el resto — incluidas las formas de pedir la baja que
esta expresión no cubre, que para eso la instrucción lo sigue diciendo. Esto es
una red, no un reemplazo.
"""
from __future__ import annotations

import re

from google.adk.models import LlmResponse
from google.genai import types

from core import record_tools

# Frases con las que un productor chileno pide la baja sin ambigüedad posible.
# Deliberadamente cortas y literales: esto no interpreta, sólo reconoce.
#
# "no me escrib\\w*" y "no me mand\\w* m[áa]s" exigen el "no me" pegado al
# verbo: así no muerden "no me escribió nadie?" (no hay verbo en 1ra persona
# del que pide) ni "por qué no me mandan más las guías?" (sujeto "las guías",
# no "mensajes/wsp/whatsapp" — ver el grupo de "no quiero más").
_PIDE_BAJA = re.compile(
    r"\bno me (escriban?|escribas|mandes?|manden)\b.{0,20}\bm[áa]s\b"
    r"|\bno quiero m[áa]s (mensajes|wsp|whatsapp)\b"
    r"|\bd[ée]jame de escribir\b"
    r"|\bdame de baja\b|\bd[ae]r(me)? de baja\b|\bb[áa]jame de la lista\b"
    r"|\bme doy de baja\b"
    r"|\bpara de (escribirme|mandarme)\b"
    r"|\bunsubscribe\b",
    re.I,
)
_PIDE_ALTA = re.compile(
    r"\bvuelvan? a escribirme\b|\bs[íi] quiero recibir\b"
    r"|\breactiv\w* los mensajes\b|\bdame de alta\b",
    re.I,
)


class _Ctx:
    """El mínimo que las tools de record_tools leen. Duplica `_Ctx` de
    producer_scope.py a propósito: ambas son tres líneas y viven en módulos
    sin relación entre sí (uno arma contexto de instrucción, este intercepta
    antes del modelo). Importar una desde la otra sería acoplar dos archivos
    por una clase que ninguno de los dos exporta como API — más caro que
    repetirla.
    """

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


def _ultimo_mensaje_del_usuario(llm_request) -> str:
    """El texto del último turno del usuario, o "" si no hay uno legible.

    `contents` es el historial completo de la conversación: leer cualquier
    mensaje que no sea el último daría de baja a alguien por algo que dijo
    hace veinte turnos.
    """
    for contenido in reversed(getattr(llm_request, "contents", None) or []):
        if getattr(contenido, "role", None) != "user":
            continue
        return " ".join(
            (getattr(p, "text", None) or "")
            for p in (getattr(contenido, "parts", None) or [])
        )
    return ""


def _respuesta(texto: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text=texto)])
    )


async def before_model(callback_context, llm_request):
    """`before_model_callback` del root. Devuelve None para que siga el modelo."""
    productor = record_tools.producer_id(getattr(callback_context, "user_id", None))
    if not productor:
        return None

    ultimo = _ultimo_mensaje_del_usuario(llm_request)
    ctx = _Ctx(productor)

    if _PIDE_BAJA.search(ultimo):
        r = await record_tools.registrar_preferencia_de_contacto(ctx, "revoked")
        return _respuesta(
            "Listo, te di de baja: no te vamos a escribir más por WhatsApp. "
            "Si después quieres volver a recibirlos, escríbeme y te doy de alta."
            if r.get("ok")
            else "Quisiste darte de baja, pero no pude confirmarla ahora mismo: "
                 "la plataforma no respondió. Todavía estás dado de alta. "
                 "Vuelve a escribirme en un rato para intentarlo de nuevo."
        )

    if _PIDE_ALTA.search(ultimo):
        r = await record_tools.registrar_preferencia_de_contacto(ctx, "granted")
        return _respuesta(
            "Listo, quedaste de alta: te vuelvo a escribir por acá."
            if r.get("ok")
            else "Quisiste quedar de alta, pero no pude confirmarlo ahora mismo: "
                 "la plataforma no respondió. Vuelve a escribirme en un rato."
        )

    return None
