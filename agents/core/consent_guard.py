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

DEUDA CONOCIDA — qué pasa si el endpoint falla. Si `registrar_preferencia_de_
contacto` devuelve `ok: False`, la baja NO queda registrada en ningún lado, y
nada la reintenta salvo que el productor vuelva a escribir: este callback sólo
corre cuando llega un turno nuevo, no hay ningún reloj corriendo entre medio.
Si el productor no vuelve a escribir, la obligación legal queda incumplida y
no queda rastro de que se intentó. Este archivo no puede arreglarlo: un
callback de un turno no es el lugar para una cola durable. El arreglo real es
un reintento con estado propio — una cola durable o un job del webhook en
`talukspa/agro_extension_digital_app` — que viva fuera de este turno.
"""
from __future__ import annotations

import re

from google.adk.models import LlmResponse
from google.genai import types

from core import record_tools

# Frases con las que un productor chileno pide la baja sin ambigüedad posible.
# Deliberadamente cortas y literales: esto no interpreta, sólo reconoce.
#
# "no me (escriban?|escribas|mandes?|manden)" exige el "no me" pegado a la
# forma exacta de quien pide la baja: así no muerde "no me escribió nadie?"
# (pasado, no es un pedido) ni "por qué no me mandan más las guías?"
# ("mandan" indicativo de terceros, no "mandes?" ni "manden").
#
# El lookahead que sigue es la parte que distingue "no me escribas" (baja: el
# imperativo negado no tiene objeto) de "no me mandes la foto" (instrucción
# sobre un mensaje concreto: el imperativo negado SÍ tiene objeto, y ese
# objeto es lo que decide, no la presencia de "más"). No hay una regla de
# regex para "objeto ausente" en español libre, así que esto ENUMERA los
# rellenos que pueden seguir al verbo sin que dejen de ser una baja — "más",
# "mensajes/wsp/whatsapp" o "por favor", en cualquier combinación, y nada
# más hasta el final del mensaje. Es una lista, no una regla: una forma de
# pedir la baja que meta un objeto distinto ahí ("no me escribas al celular")
# no la reconoce esta expresión, y por eso el modelo sigue cubriendo el resto.
_RELLENO_BAJA = r"(?:\s+(?:m[áa]s|mensajes|wsp|whatsapp|por favor))*[\s,.!?]*$"
_PIDE_BAJA = re.compile(
    r"\bno me (escriban?|escribas|mandes?|manden)\b(?=" + _RELLENO_BAJA + r")"
    r"|\bno quiero (m[áa]s (mensajes|wsp|whatsapp)|recibir (los )?mensajes)\b"
    r"|\bd[ée]jame de escribir\b"
    r"|\bdame de baja\b|\bd[ae]r(me)? de baja\b|\bb[áa]jame de la lista\b"
    r"|\bme doy de baja\b"
    r"|\bpara de (escribirme|mandarme)\b"
    r"|\bunsubscribe\b",
    re.I,
)

# Frases afirmativas de alta. Por sí solas NO alcanzan: "vuelvan a
# escribirme" es una alta, pero "no vuelvan a escribirme" es una BAJA que usa
# las mismas palabras con un "no" adelante. _PIDE_ALTA reconoce la frase;
# _sin_negacion_antes (más abajo) es quien decide si de verdad es una alta.
_PIDE_ALTA = re.compile(
    r"\bvuelvan? a escribirme\b|\bs[íi] quiero recibir\b"
    r"|\breactiv\w* los mensajes\b|\bdame de alta\b",
    re.I,
)

_NEGACION = re.compile(r"\bno\b", re.I)


def _sin_negacion_antes(texto: str, posicion: int) -> bool:
    """True si nada en `texto[:posicion]` niega lo que _PIDE_ALTA reconoció.

    Un lookbehind de regex exige ancho fijo y la distancia entre el "no" y la
    frase que niega varía ("no vuelvan a escribirme" vs. "no quiero que
    vuelvan a escribirme"), así que se busca la negación en todo el texto
    anterior al match en lugar de en una ventana fija.

    DELIBERADAMENTE CONSERVADOR, y a propósito asimétrico con _PIDE_BAJA: un
    "no" en cualquier parte del mensaje ANTES de la frase de alta la anula,
    aunque ese "no" pertenezca a otra idea. "no me llegó nada, dame de alta"
    cae al modelo en vez de registrar "granted" — un falso negativo, pero uno
    inofensivo: el alta es una conveniencia que la instrucción del prompt ya
    cubre. La baja es la obligación legal, así que ahí sí se enumeran los
    rellenos permitidos (ver _RELLENO_BAJA) en vez de exigir ausencia total
    de "no" en el mensaje. Si algún día "arreglas" este falso negativo para
    que el alta sea menos conservadora, revisa primero que no reabra el caso
    de "no vuelvan a escribirme" registrándose como alta.
    """
    return not _NEGACION.search(texto[:posicion])


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
    ctx = record_tools.ProducerContext(productor)

    if _PIDE_BAJA.search(ultimo):
        r = await record_tools.registrar_preferencia_de_contacto(ctx, "revoked")
        return _respuesta(
            "Listo, te di de baja: no te vamos a escribir más por WhatsApp. "
            "Si después quieres volver a recibirlos, escríbeme y te doy de alta."
            if r.get("ok")
            else "Quisiste darte de baja, pero no pude confirmarla: sigues "
                 "dado de alta. Escríbeme de nuevo en un rato para intentarlo "
                 "otra vez."
        )

    m = _PIDE_ALTA.search(ultimo)
    if m and _sin_negacion_antes(ultimo, m.start()):
        r = await record_tools.registrar_preferencia_de_contacto(ctx, "granted")
        return _respuesta(
            "Listo, quedaste de alta: te vuelvo a escribir por acá."
            if r.get("ok")
            else "Quisiste quedar de alta, pero no pude confirmarlo. "
                 "Escríbeme de nuevo en un rato para intentarlo otra vez."
        )

    return None
