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

    Misma razón que los topes de core/catalog_tools.py: una lectura en el import es
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


class ProducerContext:
    """El mínimo que las tools de este módulo leen de un ToolContext real:
    sólo `user_id`.

    Público por el mismo motivo que `producer_id`: `core/producer_scope.py` y
    `core/consent_guard.py` necesitan pasarle a estas tools un objeto con
    `.user_id` sin tener un `ToolContext` real a mano (uno arma el bloque de
    instrucción antes de que exista un turno de ADK; el otro intercepta el
    turno antes de que llegue al modelo). Antes cada uno tenía su propia copia
    de esta clase — la misma desincronización que el docstring de `producer_id`
    ya advierte para ese chequeo, aplicada a la clase que lo envuelve.
    """

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


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
    core/catalog_tools.py. Los tests reemplazan este helper (no `httpx.AsyncClient`
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
        # Mismo trade-off que core/catalog_tools.py con las excepciones de Postgres:
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


async def obtener_avance_del_plan(tool_context: ToolContext, estandar: str = "",
                                  empresa_id: str = "") -> dict:
    """Devuelve el avance del plan de implementación activo del productor.

    Incluye el total de acciones, cuántas ya tienen evidencia cargada y el
    porcentaje de avance. Úsala cuando pregunten "cómo voy" o por su progreso.

    Si tiene dos planes activos devuelve `ambiguous`: "cómo voy" no tiene una
    sola respuesta. Pregúntale de cuál, por el NOMBRE del estándar.

    Args:
        estandar: "PRODUCCION_PRIMARIA" o "ADECUACION_AGROINDUSTRIAL".
        empresa_id: el `businessId` de un candidato, tras una ambigüedad ya
            resuelta. Vacío en la primera llamada.
    """
    return await _post("plan-status",
                       _scope(standardCode=estandar, businessId=empresa_id),
                       tool_context)


async def listar_acciones_pendientes(
    tool_context: ToolContext, limite: int = 5, estandar: str = "",
    empresa_id: str = "", incluir_las_que_ya_tienen_respaldo: bool = False,
) -> dict:
    """Lista las acciones del plan que todavía no tienen evidencia cargada.

    Vienen ordenadas por fecha objetivo, la más próxima primero, y cada una dice
    de qué estándar es. Úsala cuando pregunten qué les falta o qué vence pronto.

    Esta NO pregunta: si el productor está en los dos estándares trae acciones de
    ambos. Al enumerarlas agrúpalas por estándar en vez de mezclarlas.

    Args:
        limite: cuántas traer como máximo (el servidor acota a 50).
        estandar: opcional, para traer sólo las de un estándar.
        empresa_id: el `businessId` de un candidato, tras una ambigüedad resuelta.
        incluir_las_que_ya_tienen_respaldo: ponlo en True cuando estés UBICANDO
            un documento que mandó el productor. Por defecto la lista sólo trae
            las acciones sin ningún respaldo, y clasificar contra esa lista
            recortada hace que termines forzando el calce contra la única que
            quedó visible.
    """
    payload: dict[str, Any] = {"limit": limite}
    if incluir_las_que_ya_tienen_respaldo:
        payload["includeWithEvidence"] = True
    payload.update(_scope(standardCode=estandar, businessId=empresa_id))
    return await _post("pending-actions", payload, tool_context)


async def obtener_detalle_de_accion(tool_context: ToolContext,
                                    codigo_accion: str,
                                    estandar: str = "") -> dict:
    """Devuelve el detalle completo de una acción del plan por su código.

    Incluye descripción, medio de verificación, recursos necesarios y material
    de apoyo. Úsala cuando pregunten por una acción específica o cómo cumplir
    con algo puntual.

    Si el código existe en los dos estándares devuelve `ambiguous` con el título
    de cada una: pregúntale al productor por el TÍTULO, no por el estándar.

    Args:
        codigo_accion: el código de la acción, por ejemplo "A001".
        estandar: déjalo vacío salvo tras una ambigüedad ya resuelta.
    """
    payload: dict[str, Any] = {"questionCode": codigo_accion}
    payload.update(_scope(standardCode=estandar))
    return await _post("action", payload, tool_context)


async def obtener_cumplimiento(tool_context: ToolContext, empresa_id: str = "",
                               instalacion_id: str = "") -> dict:
    """Devuelve el cumplimiento de UNA instalación del productor.

    El cumplimiento es por instalación, no de la empresa completa. Si el
    productor tiene varias activas devuelve `ambiguous` con sus nombres:
    pregúntale de cuál, por su NOMBRE.

    Args:
        empresa_id: el `businessId` de un candidato, tras una ambigüedad resuelta.
        instalacion_id: el `installationId` de un candidato. Cópialo tal cual del
            contexto o de la respuesta anterior; no lo derives del nombre.
    """
    return await _post("compliance",
                       _scope(businessId=empresa_id, installationId=instalacion_id),
                       tool_context)


async def obtener_nivel_de_certificacion(tool_context: ToolContext,
                                         estandar: str = "",
                                         empresa_id: str = "") -> dict:
    """Devuelve el nivel de certificación del plan activo.

    El nivel OFICIAL es el congelado al autodiagnóstico (`officialYear`). Si hay
    un recálculo distinto (`recalculatedYear`), no lo presentes como si fuera el
    resultado.

    Args:
        estandar: "PRODUCCION_PRIMARIA" o "ADECUACION_AGROINDUSTRIAL".
        empresa_id: el `businessId` de un candidato, tras una ambigüedad resuelta.
    """
    return await _post("certification-level",
                       _scope(standardCode=estandar, businessId=empresa_id),
                       tool_context)


async def leer_conversacion_de_accion(tool_context: ToolContext,
                                      codigo_accion: str,
                                      estandar: str = "") -> dict:
    """Devuelve la conversación de una acción: lo que escribió el productor y lo
    que respondió el auditor.

    Úsala cuando pregunte si le respondieron, o antes de escribirle de nuevo
    sobre la misma acción — así no le repites una consulta que ya hizo.

    Cada mensaje dice de quién es en `from`: "productor", "auditor" o
    "administrador".

    Args:
        codigo_accion: el código de la acción, por ejemplo "A001".
        estandar: déjalo vacío salvo tras una ambigüedad ya resuelta.
    """
    payload: dict[str, Any] = {"questionCode": codigo_accion}
    payload.update(_scope(standardCode=estandar))
    return await _post("action-messages", payload, tool_context)


async def registrar_labor(tool_context: ToolContext, estandar: str,
                          datos: dict, codigo_accion: str = "",
                          empresa_id: str = "") -> dict:
    """Registra una labor de terreno que el productor reporta.

    Úsala cuando cuente que hizo algo medible en su campo o planta (consumos,
    aplicaciones, mantenciones). Los datos quedan pendientes de revisión.

    Si tiene más de una empresa devuelve `ambiguous` y NO registra nada.
    Pregúntale de cuál es y vuelve a llamar con `empresa_id`: si no, el registro
    se pierde.

    Args:
        estandar: "PRODUCCION_PRIMARIA" o "ADECUACION_AGROINDUSTRIAL". Lo
            deduces tú del contenido: campo, riego, agua, suelo y plagas es
            Producción Primaria; planta, líneas, equipos, bodega y proceso es
            Adecuación Agroindustrial. No se lo preguntes al productor.
        datos: los valores reportados, por ejemplo
            {"supply_source": "pozo", "monthly_consumption_m3": 120}.
        codigo_accion: el código de la acción relacionada, si aplica.
        empresa_id: el `businessId` de un candidato, tras una ambigüedad
            resuelta. NUNCA el nombre de la empresa: se rechaza y el dato que el
            productor te pidió registrar se pierde.
    """
    payload: dict[str, Any] = {"standardCode": estandar, "payload": datos}
    # Por _scope(), no por un `if codigo_accion`: un framework de
    # function-calling puede mandar un espacio en vez de omitir un parámetro
    # opcional, y un "questionCode" así no calza con ningún código real — la
    # labor quedaría sin vincular a ninguna acción y `ok: True` no lo delata.
    payload.update(_scope(questionCode=codigo_accion, businessId=empresa_id))
    return await _post("labor-log", payload, tool_context)


async def adjuntar_evidencia(tool_context: ToolContext, codigo_accion: str,
                             id_de_adjunto: str, nombre_archivo: str = "",
                             estandar: str = "") -> dict:
    """Adjunta a una acción del plan la foto o documento que mandó el productor.

    Es el caso central del canal. Llámala cuando haya enviado un adjunto y sepa
    a qué acción va: porque te lo dijo, o porque te confirmó la que le
    propusiste. Si el archivo sirve o no lo decide el productor y lo revisa el
    auditor: no lo filtres tú.

    Adjuntar el respaldo NO significa que la acción quede cumplida. No se lo
    digas así.

    Args:
        codigo_accion: el código de la acción, por ejemplo "A001".
        id_de_adjunto: el `id_de_adjunto` de la línea
            "[adjunto de WhatsApp · id_de_adjunto=… · nombre_archivo=…]" que
            llega junto al archivo, copiado tal cual. Nunca lo inventes.
        nombre_archivo: el `nombre_archivo` de esa misma línea, si viene. Si no
            viene, déjalo vacío.
        estandar: DÉJALO VACÍO en el primer intento, siempre, aunque creas saber
            cuál es. Si el código existe en los dos estándares el servidor
            responde `ambiguous` y ahí le preguntas. Rellenarlo por tu cuenta es
            cómo se archiva un respaldo en el plan equivocado, donde nadie lo ve.
    """
    payload: dict[str, Any] = {"questionCode": codigo_accion,
                               "mediaId": id_de_adjunto}
    # Por _scope(), no por un `if nombre_archivo`: un espacio en vez de un
    # parámetro omitido dejaría "fileName": " " — el adjunto quedaría con
    # nombre visible en blanco en el expediente, en vez de sin nombre.
    payload.update(_scope(fileName=nombre_archivo, standardCode=estandar))
    return await _post("evidence", payload, tool_context)


async def enviar_mensaje_al_auditor(tool_context: ToolContext,
                                    codigo_accion: str, texto: str,
                                    estandar: str = "") -> dict:
    """Publica un mensaje del productor en la conversación de una acción.

    El auditor SÍ responde, en el mismo hilo: para leer lo que contestó usa
    leer_conversacion_de_accion.

    Si el código existe en los dos estándares devuelve `ambiguous` y NO publica
    nada.

    Args:
        codigo_accion: el código de la acción, por ejemplo "A001".
        texto: el mensaje del productor, en sus palabras.
        estandar: déjalo vacío salvo tras una ambigüedad ya resuelta.
    """
    payload: dict[str, Any] = {"questionCode": codigo_accion, "text": texto}
    payload.update(_scope(standardCode=estandar))
    return await _post("auditor-message", payload, tool_context)


async def registrar_preferencia_de_contacto(tool_context: ToolContext,
                                            accion: str) -> dict:
    """Registra que el productor acepta ("granted") o rechaza ("revoked")
    recibir mensajes por WhatsApp.

    Es un requisito legal: si pide la baja, regístrala de inmediato y
    confírmasela. Llama a la herramienta PRIMERO y cuéntaselo DESPUÉS.

    Args:
        accion: "granted" para dar de alta, "revoked" para dar de baja.
    """
    return await _post("consent", {"action": accion}, tool_context)


TOOLS: list = [
    obtener_perfil_empresa,
    obtener_avance_del_plan,
    listar_acciones_pendientes,
    obtener_detalle_de_accion,
    obtener_cumplimiento,
    obtener_nivel_de_certificacion,
    leer_conversacion_de_accion,
    registrar_labor,
    adjuntar_evidencia,
    enviar_mensaje_al_auditor,
    registrar_preferencia_de_contacto,
]
