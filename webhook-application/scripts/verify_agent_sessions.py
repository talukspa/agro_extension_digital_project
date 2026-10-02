#!/usr/bin/env python
"""Verifica contra un Agent Engine REAL que las sesiones del webhook funcionan.

Las pruebas unitarias mockean el engine, así que no pueden demostrar lo que
rompió en producción (issue #70): que el nombre de la sesión quede legible
después de crearla, que el `ttl` llegue hasta la API, y que dos identidades del
mismo teléfono no compartan nombre. Esto corre el código de producción
—`session_id_for` y `create_agent_session`— contra un engine de verdad y
después relee el resultado por REST, con un cliente aparte, para que la
comprobación no dependa del mismo SDK que hizo la escritura.

Manual, no corre en CI: necesita credenciales y escribe sesiones (las borra al
terminar). Apuntar siempre a npe, nunca a prod.

    GOOGLE_CLOUD_PROJECT=agro-extension-digital-npe \
    AGENT_ENGINE_ID=2408706170282835968 \
      uv run python scripts/verify_agent_sessions.py

Sale 0 si todo pasa, 1 con la aserción que falló.
"""
import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from unittest.mock import AsyncMock, patch

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
ENGINE = os.environ.get("AGENT_ENGINE_ID", "2408706170282835968")

if PROJECT.endswith("-prd"):
    sys.exit("Negado: este script escribe sesiones. Apuntar a npe, no a prod.")

# Teléfono inventado, no es de un productor.
WA_ID = os.environ.get("VERIFY_WA_ID", "56900000070")
UUID = "245e654f-617b-4ba6-9122-6c035ffa1fe3"

# El engine arranca en frío y el default de 15s no alcanza. Se setea antes de
# importar el módulo, que lee la variable al importar.
os.environ.setdefault("AGENT_SESSION_TIMEOUT", "240")
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
# app_config valida al importar; nada de esto se usa en el camino que se prueba.
for _k, _v in [
    ("VERIFY_TOKEN", "x"),
    ("WSP_TOKEN_AA", "x"),
    ("WSP_TOKEN_PP", "x"),
    ("WHATSAPP_BASE_URL", "https://graph.facebook.com/v22.0"),
    ("ESTANDAR_AA_FACEBOOK_APP", "x"),
    ("ESTANDAR_AA_APP_NAME", "agent_aa"),
    ("ESTANDAR_PP_FACEBOOK_APP", "x"),
    ("ESTANDAR_PP_APP_NAME", "agent_pp"),
]:
    os.environ.setdefault(_k, _v)

import vertexai  # noqa: E402
from vertexai import agent_engines  # noqa: E402

from whatsapp_webhook.external_services import agent_client  # noqa: E402

BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT}"
    f"/locations/{LOCATION}/reasoningEngines/{ENGINE}"
)


def _token() -> str:
    return subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def api(path: str, method: str = "GET") -> tuple[int, dict]:
    """Lee/borra por REST — a propósito NO usa el SDK que hizo la escritura."""
    req = urllib.request.Request(
        f"{BASE}{path}", method=method, headers={"Authorization": f"Bearer {_token()}"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def _hours_between(desde: str, hasta: str) -> float:
    a = datetime.fromisoformat(desde.replace("Z", "+00:00")).timestamp()
    b = datetime.fromisoformat(hasta.replace("Z", "+00:00")).timestamp()
    return (b - a) / 3600


def check(titulo: str, condicion: bool, detalle: str = "") -> None:
    print(f"   {'OK  ' if condicion else 'FALLA'} {titulo}{f' — {detalle}' if detalle else ''}")
    if not condicion:
        raise SystemExit(1)


async def main() -> None:
    vertexai.init(project=PROJECT, location=LOCATION)
    engine = agent_engines.get(
        f"projects/{PROJECT}/locations/{LOCATION}/reasoningEngines/{ENGINE}"
    )
    creadas: list[str] = []

    # get_engine es lo único que se parchea: resuelve el resource_name por Secret
    # Manager. Todo lo demás es el código de producción, sin tocar.
    with patch.object(agent_client, "get_engine", AsyncMock(return_value=engine)):
        print("\n1. la sesión queda legible, con el dueño correcto y con ttl")
        sid = agent_client.session_id_for(WA_ID, UUID)
        await agent_client.create_agent_session(UUID, "agent_pp", sid)
        creadas.append(sid)
        code, body = api(f"/sessions/{sid}")
        check("GET por el nombre generado", code == 200, f"{sid} -> HTTP {code}")
        check("el dueño es el uuid", body.get("userId") == UUID, body.get("userId"))
        vida = _hours_between(body["createTime"], body["expireTime"])
        check("el ttl llegó a la API", 23.9 < vida < 24.1, f"{vida:.1f}h (sin ttl: 8760h)")

        print("\n2. get-or-create sobre un nombre sano (lo que #70 rompía)")
        out = await agent_client.create_agent_session(UUID, "agent_pp", sid)
        check("el segundo create no levanta", out is not None, "'already exists' -> get OK")

        print("\n3. dos dueños del mismo teléfono no comparten nombre")
        sid_tel = agent_client.session_id_for(WA_ID, WA_ID)  # cae al teléfono
        check("el nombre cambia con el dueño", sid != sid_tel, f"{sid} != {sid_tel}")
        await agent_client.create_agent_session(WA_ID, "agent_pp", sid_tel)
        creadas.append(sid_tel)
        c1, b1 = api(f"/sessions/{sid}")
        c2, b2 = api(f"/sessions/{sid_tel}")
        check(
            "ambas existen con dueños distintos",
            c1 == c2 == 200 and b1["userId"] != b2["userId"],
            f"{b1.get('userId')} / {b2.get('userId')}",
        )

        print("\n4. rotación: cruzar la ventana da un nombre nuevo y usable")
        futuro = time.time() + agent_client.SESSION_WINDOW_SECONDS
        with patch.object(agent_client.time, "time", return_value=futuro):
            sid_next = agent_client.session_id_for(WA_ID, UUID)
        check("el nombre rota", sid_next != sid, f"{sid} -> {sid_next}")
        await agent_client.create_agent_session(UUID, "agent_pp", sid_next)
        creadas.append(sid_next)
        c3, _ = api(f"/sessions/{sid_next}")
        check("la ventana siguiente es usable", c3 == 200, f"HTTP {c3}")

    print("\n5. limpieza")
    for s in creadas:
        code, _ = api(f"/sessions/{s}", method="DELETE")
        print(f"   DELETE {s}: HTTP {code}")

    print("\nTODO OK")


if __name__ == "__main__":
    asyncio.run(main())
