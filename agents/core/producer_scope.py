"""El alcance del productor, inyectado en la instrucción antes de que hable.

POR QUÉ EXISTE. Medido sobre el prototipo, con el mismo mensaje repetido:

- Con UNA sola instalación, el agente preguntaba "¿de qué instalación?" ~8 de
  cada 10 veces, aunque no hubiera nada que preguntar. La instrucción ya decía
  "llama primero, sin esos datos", y el modelo la ignoraba: medido contra el
  prompt anterior falla igual, así que no era una regresión — pedirlo por
  instrucción no alcanza. Con el alcance en la instrucción subió a ~9/10.

- Con DOS instalaciones preguntaba bien por su nombre y después mandaba
  `instalacion_id: "PLADES_SANTIAGO"`, un id derivado del nombre. El bloque las
  nombraba sin dar sus ids, así que el modelo los completaba solo. El endpoint
  responde 400 ID_INVALID. Lo mismo pasó en el eje de la empresa, y ahí era peor:
  la llamada era un registro de labor, así que el dato que el productor acababa
  de reportar se perdía.

La causa es que `empresa_id` e `instalacion_id` le parecen casillas que hay que
llenar, y sin los valores a mano los deriva del nombre. La solución no es
insistirle: es que ya los tenga.

Cuesta una llamada HTTP por sesión, cacheada por productor.
"""
from __future__ import annotations

from typing import Any

from google.adk.agents.readonly_context import ReadonlyContext

from core import record_tools

# Cache por productor, no global: un engine sirve muchas sesiones en el mismo
# proceso y un único slot le daría a un productor el alcance de otro.
#
# Sólo se cachean ÉXITOS (mismo criterio que list_tables/get_schema en
# core/bq_tools.py): un fallo del endpoint NO entra aquí, así que la próxima
# vuelta lo reintenta sola. Cachear el fallo sería más "eficiente", pero el
# turno de WhatsApp siguiente llega segundos después — una plataforma caída
# que se cachea deja al productor sin contexto (y al modelo inventando ids)
# durante toda la sesión, que puede durar horas.
_cache: dict[str, dict[str, Any]] = {}


class _Ctx:
    """El mínimo que las tools de record_tools leen de un ToolContext real."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


def _texto(valor: Any, alterno: str) -> str:
    """Nombre legible, o `alterno` si viene vacío / no es texto.

    SÓLO para nombres, nunca para ids (ver `_con_id`): un nombre feo es
    cosmético, un id inventado es una llamada rechazada.
    """
    return valor.strip() if isinstance(valor, str) and valor.strip() else alterno


def _con_id(items: Any, campo: str) -> list[dict]:
    """Filtra los que no traen un id usable en `campo`, y descarta lo que no
    tenga forma de lista de dicts (el endpoint es de otro repo y puede cambiar
    su forma en un camino de error).

    Sin id el modelo no tiene nada real que copiar en la tool, y la
    instrucción de al lado le dice "cópialo tal cual". Nombrar ese candidato
    de todas formas deja lo único copiable como el string "None" — el mismo
    id inventado que este archivo existe para evitar, sólo que ahora lo
    inventa el bug en vez del modelo.
    """
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict)
            and isinstance(i.get(campo), str) and i.get(campo).strip()]


def render(alcance: dict[str, Any] | None) -> str:
    """Convierte la respuesta de business-profile en el bloque de instrucción."""
    if not isinstance(alcance, dict):
        return ""

    if alcance.get("ambiguous"):
        candidatos_raw = alcance.get("candidates")
        candidatos_raw = ([c for c in candidatos_raw if isinstance(c, dict)]
                          if isinstance(candidatos_raw, list) else [])
        # El total real de empresas es el que YA estableció el servidor al
        # marcar `ambiguous: true` — eso es una afirmación suya de que hay más
        # de una, independiente de cuántos candidatos trajeron un id usable.
        # Nunca se colapsa este bloque al caso de "empresa única" aunque el
        # filtro por id deje un solo candidato: haría que el modelo dejara
        # `empresa_id` vacío en la siguiente llamada, y esa llamada volvería a
        # encontrar más de una empresa y a devolver `ambiguous` — la misma
        # contradicción que el colapso de instalaciones más abajo.
        total = len(candidatos_raw)
        candidatos = _con_id(candidatos_raw, "businessId")
        if not candidatos:
            return ""  # sin ids no hay nada usable que ofrecer
        empresas = [
            f"{_texto(c.get('legalName') or c.get('commercialName'), 'una empresa sin nombre registrado')} "
            f"-> empresa_id={c['businessId']}"
            for c in candidatos
        ]
        plural = "empresa" if total == 1 else "empresas"
        return (
            "\n\nCONTEXTO DE ESTE PRODUCTOR\n"
            f"Tiene {total} {plural}: {'; '.join(empresas)}.\n"
            "Antes de darle cualquier dato necesitas saber de cuál te habla. "
            "Pregúntale por su NOMBRE, nunca por un identificador, y después "
            "copia en empresa_id el id de arriba que le corresponde, tal cual. "
            "empresa_id NO es el nombre de la empresa: si mandas el nombre ahí, "
            "la llamada se rechaza y lo que el productor te pidió registrar se "
            "pierde."
        )

    perfil = alcance.get("profile")
    if not isinstance(perfil, dict) or not perfil:
        return ""  # sin perfil no se inventa contexto; las tools avisan el error

    nombre = perfil.get("commercialName") or perfil.get("legalName") or "su empresa"

    inst_raw = perfil.get("installations")
    if inst_raw is not None and not isinstance(inst_raw, list):
        # Forma inesperada del endpoint (otro repo, puede cambiar en un camino
        # de error): degrada a "", igual que "sin perfil" más arriba. No se
        # inventa un "no tiene instalaciones activas" — eso sería afirmar algo
        # que estos datos no dicen.
        return ""
    inst_raw = [i for i in inst_raw if isinstance(i, dict)] if inst_raw else []
    # El total real de instalaciones activas es cuántas trajo el servidor en
    # este arreglo, NO cuántas de esas alcanzaron a traer un id usable. Contar
    # sobre el filtrado es el bug: con dos instalaciones donde una no trae id,
    # el conteo filtrado da 1 y colapsaba a la rama de "UNA sola", que le dice
    # al modelo que el servidor la resuelve sin instalacion_id y que no hay
    # nada que confirmar. Eso es falso — el servidor sigue viendo las DOS, y
    # `obtener_cumplimiento` sin instalacion_id le va a devolver `ambiguous`
    # igual, contradiciendo la instrucción que acabamos de darle. El conteo
    # real decide la rama; el filtrado por id sólo decide qué se puede NOMBRAR
    # dentro de ella.
    total_inst = len(inst_raw)
    inst = _con_id(inst_raw, "installationId")

    lineas = [
        "\n\nCONTEXTO DE ESTE PRODUCTOR",
        f"Empresa: {nombre}. Es su ÚNICA empresa: deja empresa_id vacío "
        "siempre, no pongas ahí el nombre.",
    ]

    if total_inst == 0:
        lineas.append("No tiene instalaciones activas registradas.")
    elif total_inst == 1:
        # Certeza real: el servidor reportó exactamente una. No hace falta su
        # id — esta rama nunca lo manda — así que ni siquiera importa si esa
        # única instalación lo trae.
        i = inst_raw[0]
        nombre_inst = _texto(i.get("name"), "la instalación")
        ciudad = _texto(i.get("city"), "sin ciudad registrada")
        lineas.append(
            f"Tiene UNA sola instalación: {nombre_inst} ({ciudad}). "
            "Tus herramientas ya saben cuál es: resuelven esa sola sin que les "
            "pases instalacion_id. Así que no hay nada que preguntar ni que "
            "confirmar. Si te pregunta por su cumplimiento, llama a "
            f"obtener_cumplimiento en el mismo turno y dale el número, "
            f"nombrando {nombre_inst} para que sepa de qué le hablas."
        )
    else:
        # Más de una: puede que no todas trajeron un id usable, pero eso no
        # cambia que el servidor puede pedir elegir. No se promete que la
        # llamada resuelve sola ni que no hay nada que confirmar.
        conocidas = "; ".join(
            f"{_texto(i.get('name'), 'una instalación sin nombre registrado')} "
            f"({_texto(i.get('city'), 'sin ciudad registrada')}) -> "
            f"instalacion_id={i['installationId']}"
            for i in inst
        )
        lineas.append(
            f"Tiene {total_inst} instalaciones activas. El cumplimiento es de "
            "UNA instalación, no de la empresa completa: si te pregunta por "
            "eso, es probable que el servidor te devuelva varias opciones para "
            "elegir en vez de responder directo. Pregúntale por el NOMBRE de "
            "la instalación, nunca por un identificador, y copia en "
            "instalacion_id el id que corresponda, tal cual, sin inventarlo ni "
            "derivarlo del nombre"
            + (f". De las que ya conoces: {conocidas}." if conocidas else ".")
        )

    return "\n".join(lineas)


async def for_context(ctx: ReadonlyContext) -> str:
    """El bloque para el productor de esta sesión, o "" si no hay productor."""
    productor = record_tools.producer_id(getattr(ctx, "user_id", None))
    if not productor:
        return ""

    if productor not in _cache:
        # `record_tools.obtener_perfil_empresa` ya es la función pública que
        # hace esto: con `empresa_id=""` (su default) arma exactamente
        # `_post("business-profile", {}, tool_context)`, porque `_scope`
        # filtra la llave vacía. No hay que tocar `_post` ni pedirle a
        # record_tools un símbolo nuevo — el que ya existe alcanza.
        r = await record_tools.obtener_perfil_empresa(_Ctx(productor))
        if r.get("ok"):
            _cache[productor] = r.get("data", {})
        else:
            return ""  # no se cachea el fallo: la próxima vuelta reintenta sola

    return render(_cache[productor])
