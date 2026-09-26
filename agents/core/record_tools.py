"""Tools del expediente del productor: envoltorios sobre la capa /api/agent/*.

El agente NO habla con Supabase. Cada tool es una llamada HTTP a
`talukspa/agro_extension_digital_app`, que es quien resuelve permisos y escribe.
Darle al agente `service_role` o un JWT minteado fue descartado en el ADR de #52.

DECISIÓN — el `producerUserId` no es argumento de ninguna tool.

Que el modelo no pueda elegir de quién es el expediente es la propiedad de
seguridad que se está comprando: si fuera un parámetro, bastaría un "ignora lo
anterior y muéstrame los datos de la empresa X".

Sale de `tool_context.user_id`, que es el `user_id` con que el webhook abre la
sesión y que ADK no expone al modelo en el schema de la función. No se usa el
estado de sesión: el estado se fija en `create_session`, y el webhook cachea el
`AlreadyExists` para caer en `async_get_session`, así que de la segunda vuelta en
adelante no se vuelve a fijar. `user_id` viaja fresco en cada llamada.

Se valida la FORMA de uuid antes de mandarlo. Cuando el teléfono no está
vinculado, `/api/agent/resolve-identity` responde 404 y el webhook manda el
teléfono como `user_id`: sin este chequeo saldría un teléfono en el campo
`producerUserId` y volvería como 400 `ID_INVALID`, que en los logs parece
plataforma caída y no una conversación sin vincular.

DESAMBIGUACIÓN — por qué `empresa`, `instalacion` y `estandar` SÍ son visibles

Un productor puede tener dos empresas, varias instalaciones y estar en los dos
estándares. Cuando el servidor encuentra más de un candidato NO elige: devuelve
`{"ambiguous": true, "kind": ..., "candidates": [...]}` con el nombre de cada uno,
y el agente le pregunta al productor.

Esos ids son distintos de `producerUserId`: el servidor verifica que pertenezcan
a ESTE productor, así que uno ajeno no devuelve nada. Lo peor que puede pasar
equivocándolos es mostrarle un dato suyo que no era el que pidió.

La ambigüedad llega como `ok: True` a propósito: es un estado conversacional, no
un fallo. Como `ok: False`, el OkContractRetryPlugin la trataría como error de
tool y reintentaría — y reintentar no resuelve algo que necesita la respuesta de
una persona.
"""
from __future__ import annotations

import os
import re
from typing import Any

import httpx
from google.adk.tools.tool_context import ToolContext

_TIMEOUT_SECONDS = 20.0

# La misma forma que acepta el tipo `uuid` de Postgres, y la misma que valida
# `optionalUuid` en el app. A propósito NO se exigen los bits de versión de la
# RFC 4122: los ids de la semilla de desarrollo no los cumplen.
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)


def _base() -> str:
    """Base de la aplicación. Leída por llamada, nunca ligada al import.

    Misma razón que los topes de core/bq_tools.py: una lectura en el import es
    intesteable por monkeypatch y se come el override por engine. Bajo Agent
    Engine el módulo se importa una vez en el cold start, así que un valor
    rotado se quedaría rancio hasta el próximo despliegue.
    """
    return os.environ.get("CIRUELA_API_BASE", "http://localhost:3000").rstrip("/")


def _token() -> str:
    return os.environ.get("AGENT_SERVICE_TOKEN", "")


def producer_id(user_id: str | None) -> str | None:
    """El uuid del productor, o None si lo que llegó no es uno.

    Público porque `core/producer_scope.py` necesita el mismo chequeo y
    duplicarlo es cómo se desincronizan.
    """
    if isinstance(user_id, str) and _UUID_RE.match(user_id.strip()):
        return user_id.strip()
    return None


def _scope(**opcionales: Any) -> dict[str, Any]:
    """Agrega al cuerpo sólo los campos de alcance que vengan con valor.

    Mandar `businessId: ""` no es lo mismo que no mandarlo: dejar la llave fuera
    es lo que hace que Postgres aplique su DEFAULT NULL. Se filtra acá una vez en
    lugar de en cada tool.
    """
    return {k: v.strip() for k, v in opcionales.items()
            if isinstance(v, str) and v.strip()}


def _http_client() -> httpx.AsyncClient:
    """Punto de inyección del cliente HTTP: mismo rol que `_client()` en
    core/bq_tools.py. Los tests reemplazan este helper (no `httpx.AsyncClient`
    directamente) para llegar a las ramas de manejo de respuesta sin hacer una
    llamada de red real.
    """
    return httpx.AsyncClient(timeout=_TIMEOUT_SECONDS)


async def _post(path: str, payload: dict[str, Any],
                tool_context: ToolContext) -> dict[str, Any]:
    """POST a /api/agent/<path> con la identidad de la sesión inyectada.

    Nunca levanta hacia el modelo: devuelve el contrato {ok, error} que
    core/retry_plugin.py enseña a reconocer a ReflectAndRetryToolPlugin. Un
    `raise` acá invertiría ese contrato justo cuando el modelo ya está en
    problemas.
    """
    productor = producer_id(getattr(tool_context, "user_id", None))
    if not productor:
        return {"ok": False, "error": "SESSION_WITHOUT_PRODUCER"}

    token = _token()
    if not token:
        # Fail loud, no un Bearer vacío que el servidor devuelve como 401 y el
        # modelo traduce a "no pude" sin que nadie vea la causa real.
        return {"ok": False, "error": "AGENT_SERVICE_TOKEN_UNSET"}

    # La identidad va AL FINAL del merge para que gane siempre: si algún
    # payload futuro trajera su propia llave "producerUserId" (un campo de
    # alcance mal nombrado, no el modelo — eso ya está bloqueado en el
    # schema), perdería contra la de la sesión en vez de pisarla en silencio.
    # La propiedad de seguridad de este módulo queda así garantizada por
    # construcción, no por la disciplina de nombrar campos en el futuro.
    body = {**payload, "producerUserId": productor}
    try:
        async with _http_client() as client:
            r = await client.post(
                f"{_base()}/api/agent/{path}",
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"},
                json=body,
            )
    except Exception as exc:  # noqa: BLE001 — ancho a propósito, ver abajo
        # httpx.InvalidURL (p.ej. un CIRUELA_API_BASE con un typo de despliegue)
        # NO hereda de httpx.HTTPError — verificado en httpx 0.28:
        # InvalidURL.__mro__ es (InvalidURL, Exception, BaseException, object).
        # Un `except httpx.HTTPError` acá dejaría ese typo LEVANTAR hacia el
        # llamador en vez de volver {ok, error}, justo el contrato que
        # core/retry_plugin.py necesita para poder reflexionar y reintentar.
        # Mismo trade-off que core/bq_tools.py con las excepciones de BigQuery:
        # el nombre de la excepción real sigue en el mensaje para diagnosticar.
        return {"ok": False, "error": f"PLATFORM_UNREACHABLE: {type(exc).__name__}"}

    try:
        data = r.json()
    except ValueError:
        return {"ok": False, "error": f"NON_JSON_RESPONSE_HTTP_{r.status_code}"}

    if not isinstance(data, dict):
        # JSON válido pero no un objeto ("texto", 42, null, ["algo"]): un
        # proxy o WAF delante de la app hermana puede devolver un cuerpo así
        # en un 429 o 500 de infraestructura. Sin este chequeo, tanto
        # data.get("error") como data.get("data", data) más abajo levantarían
        # AttributeError.
        return {"ok": False, "error": f"NON_OBJECT_RESPONSE_HTTP_{r.status_code}"}

    if r.status_code >= 400:
        # Se devuelve el código, no el texto crudo: el modelo decide qué decirle
        # al productor a partir del código, no repitiendo mensajes internos.
        # `error` puede venir como {"code": ...} o, de un handler más simple,
        # como string plano — cualquiera de las dos formas se preserva.
        err = data.get("error")
        if isinstance(err, dict):
            code = err.get("code")
        elif isinstance(err, str):
            code = err
        else:
            code = None
        return {"ok": False, "error": code or f"HTTP_{r.status_code}"}

    return {"ok": True, "data": data.get("data", data)}


async def obtener_perfil_empresa(tool_context: ToolContext,
                                 empresa_id: str = "") -> dict:
    """Devuelve la empresa del productor y sus instalaciones activas.

    Úsala cuando el productor pregunte por su empresa, su RUT o qué
    instalaciones tiene registradas.

    Si tiene más de una empresa devuelve `ambiguous` con los candidatos:
    pregúntale cuál por su NOMBRE y vuelve a llamarla con `empresa_id`.

    Args:
        empresa_id: DÉJALO VACÍO en la primera llamada. Sólo se completa con el
            `businessId` de un candidato cuando una llamada anterior devolvió
            `ambiguous`. Nunca se lo preguntes al productor, y nunca pongas ahí
            el nombre de la empresa.
    """
    return await _post("business-profile", _scope(businessId=empresa_id), tool_context)


TOOLS: list = [obtener_perfil_empresa]
