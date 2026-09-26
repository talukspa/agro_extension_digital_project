"""Mide a qué sub-agente enruta el root, con el agente real.

POR QUÉ EXISTE: hasta ahora el root elegía entre dos sub-agentes —RAG para
conceptos, BQ para el catálogo— con una regla de una línea cada uno. Con el
EXPEDIENTE son tres, y las fronteras que se pueden confundir son concretas:

  "¿qué pide la acción P001?"              -> catálogo, es el estándar en abstracto
  "¿qué pide la acción P001 de mi plan?"   -> expediente, su fecha y sus respaldos
  "¿cómo instalo un medidor de agua?"      -> normativa, es una guía
  "¿cuándo vence lo del medidor?"          -> expediente, la fecha es de su plan

No es un test de pytest: necesita cuota de Vertex y tarda minutos. Se corre a
mano cuando se cambia el prompt del root, una descripción de sub-agente, o se
agrega un sub-agente nuevo.

    cd agents
    set -a && . ./.env
    . <el .env.local de la app, por CIRUELA_API_BASE y AGENT_SERVICE_TOKEN>
    set +a
    .venv/bin/python scripts/measure_routing.py [repeticiones]

No hay umbral que "pase" de antemano. Lo que se busca es saber DÓNDE está el
enrutamiento hoy, para poder afirmar que un cambio lo mejoró o lo empeoró. Sin un
número anterior, "el enrutamiento empeoró" no se puede sostener.
"""
import asyncio
import logging
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Un productor del seed con dos instalaciones y un plan con acciones: así el
# bloque de contexto sale de datos reales y no de un caso degenerado.
PRODUCTOR = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"

CASOS = [
    # (mensaje del productor, sub-agente esperado, por qué)
    ("cómo va mi cumplimiento?", "record", "posesivo: su porcentaje"),
    ("qué me falta pendiente?", "record", "posesivo: sus acciones"),
    ("te mando la foto del medidor de agua", "record", "escribe: adjunta un respaldo"),
    ("registra que en el pozo consumí 120 metros cúbicos", "record", "escribe: labor"),
    ("me respondió el auditor?", "record", "su conversación"),
    ("cuándo vence lo del medidor?", "record", "la fecha es de SU plan"),
    ("en qué año de certificación estoy?", "record", "su nivel"),
    ("cuántos puntos vale la dimensión Ética?", "bq", "agregado del catálogo"),
    ("lístame las acciones de Ambiente, tema Agua", "bq", "filtro del catálogo"),
    ("qué pide la acción P001?", "bq", "el estándar en abstracto"),
    ("qué es la huella hídrica?", "rag", "concepto"),
    ("cómo instalo un medidor de agua?", "rag", "guía de implementación"),
]


def _elegidos(llamadas: list[str]) -> set[str]:
    """Qué sub-agentes pidió el root en este turno. Puede ser MÁS DE UNO.

    Los sub-agentes viajan como AgentTool, así que el root los invoca por su
    nombre (`pp_agent_record`, etc.). Se busca el sufijo para no atarse al
    prefijo del agente.

    OJO, esto se midió mal la primera vez: la versión anterior devolvía un solo
    sufijo, el primero de una tupla ordenada, así que un turno que llamaba a RAG
    **y** a BQ se contaba como BQ. Y llamar a los dos es justamente lo que el
    prompt de BQ pide —cuando RAG explica un concepto, BQ trae el `link` del
    recurso—, así que el medidor reportaba 0/3 en dos casos donde el agente
    estaba haciendo lo correcto. Un medidor que castiga el comportamiento
    deseado es peor que no medir.
    """
    encontrados = {s for s in ("record", "bq", "rag")
                   if any(n.endswith(s) for n in llamadas)}
    if not encontrados and any("transfer" in n for n in llamadas):
        return {"transfer"}  # ADK despachó por transferencia, no por AgentTool
    return encontrados


async def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    from google.adk.runners import InMemoryRunner
    from google.genai import types

    from agent_pp_app.agent_engine_app import app

    root = app._tmpl_attrs["agent"]
    aciertos: Counter[str] = Counter()
    desvios: list[tuple[str, str, str, list[str]]] = []
    sin_llamar = 0

    # ADK imprime el traceback completo de un 429 antes de levantarlo, y con una
    # docena de casos eso sepulta el resultado. El reintento vive acá, no en el
    # bucle: un 429 tiene que repetir ESA repetición, no perderla — si no, el
    # caso queda medido sobre menos muestras que el resto y los números no se
    # pueden comparar entre sí.
    logging.getLogger("google_genai").setLevel(logging.CRITICAL)
    logging.getLogger("google.adk").setLevel(logging.CRITICAL)

    async def _un_turno(mensaje: str, etiqueta: str) -> list[str]:
        for intento in range(6):
            runner = InMemoryRunner(agent=root, app_name=etiqueta)
            await runner.session_service.create_session(
                app_name=etiqueta, user_id=PRODUCTOR, session_id="s"
            )
            llamadas: list[str] = []
            try:
                async for ev in runner.run_async(
                    user_id=PRODUCTOR,
                    session_id="s",
                    new_message=types.Content(
                        role="user", parts=[types.Part(text=mensaje)]
                    ),
                ):
                    for p in (ev.content.parts if ev.content else []) or []:
                        fc = getattr(p, "function_call", None)
                        if fc:
                            llamadas.append(fc.name)
                return llamadas
            except Exception as exc:  # noqa: BLE001
                if "RESOURCE_EXHAUSTED" not in str(exc) and "429" not in str(exc):
                    raise
                espera = 20 * (intento + 1)
                print(f"      (429, esperando {espera}s)", flush=True)
                await asyncio.sleep(espera)
        print(f"      (agotados los reintentos de {mensaje!r})", flush=True)
        return []

    for mensaje, esperado, _por_que in CASOS:
        print(f"  {mensaje}", flush=True)
        for i in range(n):
            llamadas = await _un_turno(
                mensaje, f"routing_{abs(hash(mensaje)) % 9999}_{i}"
            )
            elegidos = _elegidos(llamadas)
            if not elegidos:
                sin_llamar += 1
            # Acierta si el esperado está ENTRE los que llamó. Traer además otro
            # no es un desvío: el prompt de BQ pide acompañar a RAG con el link
            # del recurso, y el expediente puede necesitar el catálogo para
            # explicar una acción. Lo que sería un desvío es no llamar al que
            # corresponde.
            if esperado in elegidos:
                aciertos[mensaje] += 1
            else:
                desvios.append((mensaje, esperado, ",".join(sorted(elegidos)) or "ninguno", llamadas))

    print(f"\n{'=' * 78}\nENRUTAMIENTO — n={n} por caso\n{'=' * 78}")
    for mensaje, esperado, por_que in CASOS:
        marca = "  " if aciertos[mensaje] == n else "<-"
        print(f" {marca} {aciertos[mensaje]}/{n}  [{esperado:6}]  {mensaje}")
        if aciertos[mensaje] != n:
            print(f"          ({por_que})")

    total = sum(aciertos.values())
    print(f"\ncorrecto: {total}/{len(CASOS) * n}")
    print(f"turnos que no llamaron a ningún sub-agente: {sin_llamar}")

    if desvios:
        print(f"\n{len(desvios)} desvíos, los primeros 12:")
        for mensaje, esperado, elegido, llamadas in desvios[:12]:
            print(f"  {mensaje!r}")
            print(f"    esperado={esperado}  elegido={elegido}  llamó={llamadas}")


if __name__ == "__main__":
    asyncio.run(main())
