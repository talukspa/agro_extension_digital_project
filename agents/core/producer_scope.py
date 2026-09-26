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
    """El mínimo que `record_tools._post` lee, para reusarlo desde acá."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


def render(alcance: dict[str, Any] | None) -> str:
    """Convierte la respuesta de business-profile en el bloque de instrucción."""
    if not isinstance(alcance, dict):
        return ""

    if alcance.get("ambiguous"):
        empresas = [
            f"{c.get('legalName') or c.get('commercialName')} -> "
            f"empresa_id={c.get('businessId')}"
            for c in alcance.get("candidates", [])
        ]
        return (
            "\n\nCONTEXTO DE ESTE PRODUCTOR\n"
            f"Tiene {len(empresas)} empresas: {'; '.join(empresas)}.\n"
            "Antes de darle cualquier dato necesitas saber de cuál te habla. "
            "Pregúntale por su NOMBRE, nunca por un identificador, y después "
            "copia en empresa_id el id de arriba que le corresponde, tal cual. "
            "empresa_id NO es el nombre de la empresa: si mandas el nombre ahí, "
            "la llamada se rechaza y lo que el productor te pidió registrar se "
            "pierde."
        )

    perfil = alcance.get("profile") or {}
    if not perfil:
        return ""  # sin perfil no se inventa contexto; las tools avisan el error

    nombre = perfil.get("commercialName") or perfil.get("legalName") or "su empresa"
    inst = perfil.get("installations") or []

    lineas = [
        "\n\nCONTEXTO DE ESTE PRODUCTOR",
        f"Empresa: {nombre}. Es su ÚNICA empresa: deja empresa_id vacío "
        "siempre, no pongas ahí el nombre.",
    ]

    if len(inst) == 1:
        i = inst[0]
        lineas.append(
            f"Tiene UNA sola instalación: {i.get('name')} ({i.get('city')}). "
            "Tus herramientas ya saben cuál es: resuelven esa sola sin que les "
            "pases instalacion_id. Así que no hay nada que preguntar ni que "
            "confirmar. Si te pregunta por su cumplimiento, llama a "
            f"obtener_cumplimiento en el mismo turno y dale el número, "
            f"nombrando {i.get('name')} para que sepa de qué le hablas."
        )
    elif len(inst) > 1:
        detalle = "; ".join(
            f"{i.get('name')} ({i.get('city')}) -> "
            f"instalacion_id={i.get('installationId')}"
            for i in inst
        )
        lineas.append(
            f"Tiene {len(inst)} instalaciones: {detalle}. "
            "El cumplimiento es de UNA instalación, no de la empresa completa, "
            "así que cuando te pregunte por eso necesitas saber de cuál. "
            "Pregúntale por el NOMBRE de la instalación, nunca por un "
            "identificador, y después copia en instalacion_id el id de arriba "
            "que le corresponde, tal cual, sin inventarlo ni derivarlo del "
            "nombre."
        )
    else:
        lineas.append("No tiene instalaciones activas registradas.")

    return "\n".join(lineas)


async def for_context(ctx: ReadonlyContext) -> str:
    """El bloque para el productor de esta sesión, o "" si no hay productor."""
    productor = record_tools.producer_id(getattr(ctx, "user_id", None))
    if not productor:
        return ""

    if productor not in _cache:
        # Se llama a `record_tools._post`, que es privado al módulo, en vez de
        # pedirle a record_tools una función pública nueva: `_post` ya hace
        # exactamente lo que se necesita (inyecta producerUserId, devuelve el
        # contrato {ok, data}) y envolverlo en un segundo nombre público sólo
        # para que este módulo no toque un "_" sería una capa sin comportamiento
        # propio. Los dos viven en el mismo paquete `core` y el mismo commit los
        # revisa juntos, así que no hay un límite de paquete que proteger.
        r = await record_tools._post("business-profile", {}, _Ctx(productor))
        if r.get("ok"):
            _cache[productor] = r.get("data", {})
        else:
            return ""  # no se cachea el fallo: la próxima vuelta reintenta sola

    return render(_cache[productor])
