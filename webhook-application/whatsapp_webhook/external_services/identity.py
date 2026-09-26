"""wa_id -> producer_user_id, contra /api/agent/resolve-identity.

POR QUÉ NO SE RESUELVE ACÁ CONTRA SUPABASE: resolver la identidad necesita
`service_role`, y la invariante de esa capa es que la llave no sale de la app de
Next. El webhook sólo carga `AGENT_SERVICE_TOKEN`, que no puede leer usuarios.

El uuid resuelto se le pasa al agente como `user_id` de la sesión de ADK, y de
ahí lo leen las tools del expediente (`agents/core/record_tools.py`). No va en el
estado de la sesión: el estado se fija en `create_session`, y
`agent_client.create_agent_session` cachea el `AlreadyExists` para caer en
`async_get_session`, así que de la segunda vuelta en adelante no se volvería a
fijar — un productor que verifica su teléfono a mitad de conversación se quedaría
con el estado viejo. `user_id` viaja fresco en cada llamada.

Cuando no hay vínculo verificado devuelve None y el webhook manda el teléfono
como `user_id`. Las tools del expediente validan la forma de uuid y se niegan; el
agente le pide completar su registro. RAG y el catálogo siguen funcionando: son
datos públicos del estándar.

NUNCA LEVANTA. Corre en el camino del mensaje del productor, así que una
excepción acá se lleva el turno completo. Ante cualquier fallo devuelve None y la
conversación sigue sin expediente, que es degradar, no caerse.
"""
import logging
import os
from typing import Optional

import httpx

_logger = logging.getLogger(__name__)
_TIMEOUT_SECONDS = 10.0


def _api_base() -> str:
    """Base de la app. Leída por llamada, nunca ligada al import.

    El servicio de Cloud Run se reconfigura sin redesplegar la imagen, y una
    lectura en el import se queda con el valor del arranque.
    """
    return os.getenv("CIRUELA_API_BASE", "http://localhost:3100").rstrip("/")


def _token() -> str:
    return os.getenv("AGENT_SERVICE_TOKEN", "")


def _uuid_de(datos: object) -> Optional[str]:
    """Saca el `producerUserId` del sobre, o None si no viene como se espera.

    El sobre de la app es `{success, data, status}`. Se acepta también el objeto
    plano por si la respuesta llega sin envolver, pero nada se asume: cada nivel
    se verifica antes de indexarlo, porque un proxy delante de la app puede
    devolver un cuerpo JSON que no es un objeto.
    """
    if not isinstance(datos, dict):
        return None
    cuerpo = datos.get("data")
    if not isinstance(cuerpo, dict):
        cuerpo = datos
    valor = cuerpo.get("producerUserId")
    if not isinstance(valor, str):
        return None
    limpio = valor.strip()
    return limpio or None


async def resolve_producer(wa_id: str) -> Optional[str]:
    """El uuid del productor para este wa_id, o None si no hay vínculo."""
    if not _token():
        # Fail loud en el log, silencioso hacia el productor: sin token no hay
        # nada que intentar, y un Bearer vacío vuelve como 401 que se confunde
        # con un número sin vincular. Se nombra la variable, nunca su valor.
        _logger.error("resolve_identity.sin_token", extra={"faltante": "AGENT_SERVICE_TOKEN"})
        return None

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            r = await client.post(
                f"{_api_base()}/api/agent/resolve-identity",
                headers={
                    "Authorization": f"Bearer {_token()}",
                    "Content-Type": "application/json",
                },
                json={"waId": wa_id},
            )
    except Exception as exc:  # noqa: BLE001
        # Ancho a propósito, y no `httpx.HTTPError`: `httpx.InvalidURL` NO
        # desciende de HTTPError (ver el test de la jerarquía), así que un
        # CIRUELA_API_BASE con un typo se escaparía de un except específico y se
        # llevaría el turno del productor. Se loguea la CLASE, no el mensaje ni
        # la URL, para no arrastrar credenciales que vinieran en la query.
        _logger.warning("resolve_identity.inalcanzable", extra={"error": type(exc).__name__})
        return None

    if r.status_code == 404:
        # Número desconocido, sin OTP verificado, onboarding incompleto o cuenta
        # no activa. No es un fallo del webhook: es un productor que todavía no
        # completó su registro, y el agente sabe qué decirle.
        _logger.info("resolve_identity.sin_vinculo")
        return None

    if r.status_code >= 400:
        _logger.warning("resolve_identity.http_error", extra={"status": r.status_code})
        return None

    try:
        datos = r.json()
    except ValueError:
        _logger.warning("resolve_identity.cuerpo_no_json", extra={"status": r.status_code})
        return None

    productor = _uuid_de(datos)
    if productor is None:
        _logger.warning("resolve_identity.sin_producer_user_id")
    return productor
