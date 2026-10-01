"""Camino completo contra el stack REAL: agente real, app real, Postgres real.

No hay imitación en ninguna capa. Se registra cada cuerpo HTTP que sale del
agente, el código que vuelve, y se consulta la base antes y después para ver qué
quedó escrito de verdad — no lo que el agente dice que escribió, que es
precisamente la diferencia que midiendo el prototipo resultó importar.

    cd agents
    set -a && . ./.env
    . <el .env.local de la app, por AGENT_SERVICE_TOKEN>
    export CIRUELA_API_BASE=http://localhost:3100
    set +a
    .venv/bin/python scripts/e2e_real_stack.py

Requiere la app corriendo y la Supabase local con acciones de plan cargadas. Si
`implementation_plan_actions` está vacía, los caminos de evidencia y de mensaje
al auditor no se pueden ejercitar y el guion lo dice en lugar de fingir.
"""
import asyncio
import json
import logging
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PRODUCTOR = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"
DB = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

GUION = [
    "Hola, cómo va mi cumplimiento?",
    "el de la planta de deshidratado",
    "qué me falta pendiente?",
    "registra que en el pozo consumí 137 metros cúbicos este mes",
    "dile al auditor que el medidor del pozo ya quedó instalado",
    "me respondió algo el auditor?",
    "no me escriban más por favor",
]

LLAMADAS: list[tuple[str, dict, dict]] = []


def sql(q: str) -> str:
    r = subprocess.run([
        "psql", DB, "-At", "-c", q,
    ], capture_output=True, text=True)
    return r.stdout.strip()


def _estado_base() -> dict[str, str]:
    return {
        "labores del agente": sql(
            "select count(*) from labor_logs where source='whatsapp_agent';"),
        "mensajes de acción": sql("select count(*) from question_messages;"),
        "evidencias": sql("select count(*) from survey_evidence;"),
        "eventos de consentimiento": sql(
            f"select count(*) from whatsapp_consent_events where user_id='{PRODUCTOR}';"),
    }


async def main() -> None:
    logging.getLogger("google_genai").setLevel(logging.CRITICAL)
    logging.getLogger("google.adk").setLevel(logging.CRITICAL)

    from google.adk.runners import InMemoryRunner
    from google.genai import types

    from agent_pp_app.agent_engine_app import app
    from core import record_tools

    acciones = sql("select count(*) from implementation_plan_actions;")
    print(f"acciones de plan en la base: {acciones}")
    if acciones == "0":
        print("  OJO: sin acciones de plan, evidencia y mensaje al auditor no se "
              "pueden ejercitar. No lo reportes como defecto del agente.")

    # Espiar el cliente HTTP, no las tools: así se ve el cuerpo EXACTO que viaja,
    # que es donde aparecieron los ids inventados al medir el prototipo.
    original = record_tools._post

    async def espiado(path, payload, tool_context):
        salida = await original(path, payload, tool_context)
        LLAMADAS.append((path, payload, salida))
        return salida

    record_tools._post = espiado

    antes = _estado_base()
    print(f"base ANTES:  {antes}")

    root = app._tmpl_attrs["agent"]
    runner = InMemoryRunner(agent=root, app_name="e2e_real")
    await runner.session_service.create_session(
        app_name="e2e_real", user_id=PRODUCTOR, session_id="56912345678")

    for mensaje in GUION:
        i = len(LLAMADAS)
        print(f"\n{'=' * 78}\nPRODUCTOR: {mensaje}\n{'-' * 78}")
        texto: list[str] = []
        for intento in range(4):
            try:
                async for ev in runner.run_async(
                    user_id=PRODUCTOR, session_id="56912345678",
                    new_message=types.Content(
                        role="user", parts=[types.Part(text=mensaje)]),
                ):
                    for p in (ev.content.parts if ev.content else []) or []:
                        if getattr(p, "text", None):
                            texto.append(p.text)
                break
            except Exception as exc:  # noqa: BLE001
                if "RESOURCE_EXHAUSTED" not in str(exc) and "429" not in str(exc):
                    print(f"  !! {type(exc).__name__}: {str(exc)[:160]}")
                    break
                espera = 20 * (intento + 1)
                print(f"  (429, esperando {espera}s)", flush=True)
                await asyncio.sleep(espera)

        for path, cuerpo, salida in LLAMADAS[i:]:
            sin_id = {k: v for k, v in cuerpo.items()}
            datos = salida.get("data") if isinstance(salida, dict) else None
            if isinstance(datos, dict) and datos.get("ambiguous"):
                marca = f"AMBIGUO/{datos.get('kind')}"
            elif isinstance(salida, dict) and not salida.get("ok"):
                marca = f"ERROR {salida.get('error')}"
            else:
                marca = "ok"
            print(f"  POST /{path} {json.dumps(sin_id, ensure_ascii=False)[:150]}  [{marca}]")
        print(f"  AGENTE: {''.join(texto).strip()[:400]}")

    despues = _estado_base()
    print(f"\n{'=' * 78}\nbase DESPUÉS: {despues}")
    for k in antes:
        if antes[k] != despues[k]:
            print(f"  cambió {k}: {antes[k]} -> {despues[k]}")

    errores = [c for c in LLAMADAS if isinstance(c[2], dict) and not c[2].get("ok")]
    print(f"\nllamadas HTTP: {len(LLAMADAS)}   con error: {len(errores)}")
    for path, cuerpo, salida in errores:
        print(f"  ERROR /{path}: {salida.get('error')}  cuerpo={json.dumps(cuerpo, ensure_ascii=False)[:120]}")

    print("\nlo último escrito:")
    print("  labor:    ", sql("select payload::text from labor_logs "
                              "where source='whatsapp_agent' order by created_at desc limit 1;") or "(nada)")
    print("  mensaje:  ", sql("select left(message,80) from question_messages "
                              "order by created_at desc limit 1;") or "(nada)")
    print("  consent:  ", sql(f"select action from whatsapp_consent_events "
                              f"where user_id='{PRODUCTOR}' order by seq desc limit 1;") or "(nada)")


if __name__ == "__main__":
    asyncio.run(main())
