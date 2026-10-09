# Menú de opciones en WhatsApp — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** El agente raíz (AA y PP) ofrece opciones tocables —botones o lista de WhatsApp— al saludar y después de cada respuesta, y el toque del productor vuelve al agente como texto.

**Architecture:** Una tool nueva `ofrecer_opciones` en el agente raíz sólo valida y devuelve `ok`; el webhook lee los `args` de esa llamada en el stream de Agent Runtime, los re-valida y los dibuja como mensaje interactivo (botones si son ≤3 cortas, lista si no), con fallback a texto numerado. Los toques (`interactive.button_reply` / `list_reply`) entran por el mismo camino que un texto.

**Tech Stack:** Python 3.12 · uv · Google ADK (`LlmAgent`, `AgentTool`) · Vertex AI Agent Runtime · FastAPI webhook · httpx · pydantic v2 · pytest / pytest-asyncio · WhatsApp Cloud API.

**Spec:** `docs/superpowers/specs/2026-10-09-menu-opciones-whatsapp-design.md`

## Global Constraints

- Límites WhatsApp: botones 1–3 con título ≤ 20; lista 1–10 filas con título ≤ 24 y descripción ≤ 72; etiqueta del botón de lista ≤ 20; cuerpo ≤ 1024.
- La tool vive en el agente **raíz**, nunca en un sub-agente (los eventos de un `AgentTool` no llegan al stream del webhook).
- La tool devuelve el contrato `{"ok": bool, "error": str}` que `core/retry_plugin.py` reconoce; nunca trunca ni levanta.
- Ids de botón/fila: `opt_1 … opt_n`.
- Menú principal (título / descripción), idéntico en AA y PP:
  Subir un verificador / Foto o documento para una acción de tu plan ·
  Mi avance y puntaje / Cómo vas en tu plan y tu nivel ·
  Qué me falta / Acciones pendientes y próximas fechas ·
  Conocer el estándar / Qué pide, dimensiones y puntajes ·
  Sustentabilidad / Buenas prácticas para producir mejor ·
  Registrar una labor / Algo que hiciste en campo o planta ·
  Hablar con el auditor / Dejar o leer mensajes
- Un toque llega al agente como `"<título> — <descripción>"` (o sólo el título si no hay descripción).
- Sin dependencias nuevas. Comentarios y docstrings nuevos en español, como el código vecino.
- Commits: mensaje imperativo en español, terminado en `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Comandos de test: agentes `cd agents && uv run pytest -q`; webhook `cd webhook-application && uv run --extra dev pytest -q`.

## Review Focus

1. **El modelo llama a `ofrecer_opciones` pero no escribe texto** → el interactivo sale con cuerpo "¿Qué quieres hacer ahora?" en vez de un error. (Tests en Task 4 y Task 5.)
2. **Reintento tras `ok: False`** → el webhook usa la ÚLTIMA llamada; si esa última es inválida, el productor recibe texto sin opciones (nunca un menú roto). (Task 5.)
3. **Texto > 1024 con opciones y el interactivo falla** → el fallback numerado no repite el texto que ya salió. (Task 6.)
4. **Un `interactive` que no es un toque de botón/lista** (p. ej. `nfm_reply` de un Flow) → sigue en el acuse actual, no llega vacío al agente. (Task 7.)
5. **Tras un fallback numerado el productor contesta "2"** → el texto del fallback le dice que responda con el número o lo escriba, y el agente tiene en su historial los `args` de la llamada para mapearlo. (Task 4.)

---

### Task 1: Tool `ofrecer_opciones` en el agente

**Files:**
- Create: `agents/core/options_tools.py`
- Test: `agents/tests/test_options_tools.py`

**Interfaces:**
- Produces: `core.options_tools.ofrecer_opciones(opciones: list[Opcion], boton: str = "Ver opciones") -> dict`; `core.options_tools.Opcion` (pydantic, `titulo: str`, `descripcion: str = ""`); `core.options_tools.TOOLS: list`.

- [ ] **Step 1: Write the failing test**

`agents/tests/test_options_tools.py`:

```python
"""La tool del menú sólo valida los límites de WhatsApp: el webhook la dibuja.

Cada límite que no se valide acá termina en un menú descartado en el webhook
(el productor recibe texto pelado) en vez de un reintento del modelo.
"""
import pytest

from core.options_tools import Opcion, ofrecer_opciones

MENU = [
    {"titulo": "Subir un verificador", "descripcion": "Foto o documento para una acción de tu plan"},
    {"titulo": "Mi avance y puntaje", "descripcion": "Cómo vas en tu plan y tu nivel"},
    {"titulo": "Qué me falta", "descripcion": "Acciones pendientes y próximas fechas"},
    {"titulo": "Conocer el estándar", "descripcion": "Qué pide, dimensiones y puntajes"},
    {"titulo": "Sustentabilidad", "descripcion": "Buenas prácticas para producir mejor"},
    {"titulo": "Registrar una labor", "descripcion": "Algo que hiciste en campo o planta"},
    {"titulo": "Hablar con el auditor", "descripcion": "Dejar o leer mensajes"},
]


def test_el_menu_principal_es_valido():
    r = ofrecer_opciones(MENU)
    assert r == {"ok": True, "data": {"opciones_ofrecidas": 7}}


def test_acepta_instancias_de_opcion():
    """ADK puede entregar los items ya convertidos al modelo pydantic."""
    r = ofrecer_opciones([Opcion(titulo="Sí"), Opcion(titulo="No")])
    assert r["ok"] is True


@pytest.mark.parametrize("opciones", [[], [{"titulo": f"Op {i}"} for i in range(11)]])
def test_rechaza_cero_o_mas_de_diez(opciones):
    r = ofrecer_opciones(opciones)
    assert r["ok"] is False and "entre 1 y 10" in r["error"]


def test_rechaza_titulo_vacio():
    r = ofrecer_opciones([{"titulo": "  "}])
    assert r["ok"] is False and "no tiene título" in r["error"]


def test_rechaza_titulo_de_25():
    r = ofrecer_opciones([{"titulo": "x" * 25}])
    assert r["ok"] is False and "24" in r["error"]


def test_acepta_titulo_de_24():
    assert ofrecer_opciones([{"titulo": "x" * 24}])["ok"] is True


def test_rechaza_descripcion_de_73():
    r = ofrecer_opciones([{"titulo": "A", "descripcion": "x" * 73}])
    assert r["ok"] is False and "72" in r["error"]


def test_rechaza_titulos_repetidos_sin_importar_mayusculas():
    r = ofrecer_opciones([{"titulo": "Qué me falta"}, {"titulo": " qué me falta "}])
    assert r["ok"] is False and "repetido" in r["error"]


def test_rechaza_boton_de_21():
    r = ofrecer_opciones([{"titulo": "A"}], boton="x" * 21)
    assert r["ok"] is False and "20" in r["error"]


def test_boton_vacio_usa_el_de_siempre():
    """Un framework de function-calling puede mandar "" por un opcional."""
    assert ofrecer_opciones([{"titulo": "A"}], boton="")["ok"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd agents && uv run pytest tests/test_options_tools.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'core.options_tools'`

- [ ] **Step 3: Write minimal implementation**

`agents/core/options_tools.py`:

```python
"""El menú de opciones tocables: el agente raíz decide qué ofrecer, el webhook
lo dibuja como botones o lista de WhatsApp.

Esta tool NO envía nada. El webhook lee los `args` de la llamada en el stream de
Agent Runtime (`webhook-application/.../agent_client.send_to_agent`). Por eso
vive en el RAÍZ: los sub-agentes corren como `AgentTool` y sus eventos internos
no llegan a ese stream.

Lo único que hace es validar los límites de la Cloud API para que el modelo
corrija con el contrato {ok, error} de core/retry_plugin.py ANTES de que el
webhook tenga que descartar el menú. Nunca trunca: un título cortado a la mitad
es peor que un reintento. El webhook re-valida con los mismos números (otro
deploy, no puede importar este módulo).

Ver docs/superpowers/specs/2026-10-09-menu-opciones-whatsapp-design.md.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

MAX_OPCIONES = 10
MAX_TITULO = 24
MAX_DESCRIPCION = 72
MAX_BOTON = 20


class Opcion(BaseModel):
    titulo: str
    descripcion: str = ""


def _como_dict(opcion: Any) -> dict:
    """ADK puede entregar cada item como `Opcion` o como dict crudo."""
    if isinstance(opcion, BaseModel):
        return opcion.model_dump()
    return opcion if isinstance(opcion, dict) else {}


def _error(motivo: str) -> dict:
    return {"ok": False, "error": motivo}


def ofrecer_opciones(opciones: list[Opcion], boton: str = "Ver opciones") -> dict:
    """Muestra al productor opciones tocables (botones o lista de WhatsApp)
    junto a tu respuesta.

    Úsala al saludar (con el menú principal), al terminar una respuesta (2 a 4
    siguientes pasos), cuando el productor no sabe qué pedir, o para que elija
    entre varias cosas. Tu texto NO repite las opciones: van sólo acá. Cuando
    toque una, te llega como su mensaje el título de la opción.

    Args:
        opciones: de 1 a 10. `titulo` de hasta 24 caracteres, sin repetir;
            `descripcion` opcional, de hasta 72.
        boton: el texto del botón que abre la lista, hasta 20 caracteres.
    """
    items = [_como_dict(o) for o in (opciones or [])]
    if not 1 <= len(items) <= MAX_OPCIONES:
        return _error(
            f"Ofrece entre 1 y {MAX_OPCIONES} opciones; mandaste {len(items)}."
        )
    vistos: set[str] = set()
    for i, opcion in enumerate(items, 1):
        titulo = str(opcion.get("titulo") or "").strip()
        descripcion = str(opcion.get("descripcion") or "").strip()
        if not titulo:
            return _error(f"La opción {i} no tiene título.")
        if len(titulo) > MAX_TITULO:
            return _error(
                f'El título "{titulo}" tiene {len(titulo)} caracteres; el máximo '
                f"es {MAX_TITULO}. Acórtalo."
            )
        if len(descripcion) > MAX_DESCRIPCION:
            return _error(
                f'La descripción de "{titulo}" tiene {len(descripcion)} caracteres; '
                f"el máximo es {MAX_DESCRIPCION}. Acórtala."
            )
        if titulo.casefold() in vistos:
            return _error(f'El título "{titulo}" está repetido.')
        vistos.add(titulo.casefold())
    # Vacío = el de siempre: el webhook pone "Ver opciones".
    if len((boton or "").strip()) > MAX_BOTON:
        return _error(f"El texto del botón debe tener hasta {MAX_BOTON} caracteres.")
    return {"ok": True, "data": {"opciones_ofrecidas": len(items)}}


TOOLS: list = [ofrecer_opciones]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd agents && uv run pytest tests/test_options_tools.py -q`
Expected: PASS (12 passed)

- [ ] **Step 5: Commit**

```bash
git add agents/core/options_tools.py agents/tests/test_options_tools.py
git commit -m "feat(agents): tool ofrecer_opciones que valida el menú de WhatsApp

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Registrar la tool en el raíz (AA y PP)

**Files:**
- Modify: `agents/core/agent.py` (import y `tools=[...]` del `root`)
- Modify: `agents/tests/test_core_agent.py`, `agents/tests/test_planner_and_citations.py` (los tests que recorren `root.tools` asumiendo que todo es `AgentTool`)

**Interfaces:**
- Consumes: `core.options_tools.TOOLS` (Task 1).
- Produces: `build_app(...)` cuyo raíz tiene `[AgentTool(rag), AgentTool(catalog), AgentTool(record), ofrecer_opciones]`.

- [ ] **Step 1: Write the failing test**

Agregar al final de `agents/tests/test_core_agent.py`:

```python
def test_el_root_tiene_la_tool_del_menu_y_los_subagentes_no():
    """Sólo el raíz: los eventos de un AgentTool no llegan al stream que lee
    el webhook, así que en un sub-agente la tool no dibujaría nada."""
    from core.agent import build_app
    from core import options_tools

    for name, env in (("pp_agent", "DATASTORE_PP_ID"), ("aa_agent", "DATASTORE_AA_ID")):
        root = build_app(name=name, display_name=name, main_datastore_env=env)._tmpl_attrs["agent"]
        assert options_tools.ofrecer_opciones in root.tools
        for t in root.tools:
            if hasattr(t, "agent"):
                assert options_tools.ofrecer_opciones not in t.agent.tools
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd agents && uv run pytest tests/test_core_agent.py::test_el_root_tiene_la_tool_del_menu_y_los_subagentes_no -q`
Expected: FAIL — `assert <function ofrecer_opciones ...> in [...]`

- [ ] **Step 3: Write minimal implementation**

En `agents/core/agent.py`, cambiar el import:

```python
from core import catalog_tools, consent_guard, options_tools, producer_scope, prompts, record_tools
```

y la lista de tools del `root`:

```python
        tools=[
            agent_tool.AgentTool(agent=rag),
            agent_tool.AgentTool(agent=catalog),
            agent_tool.AgentTool(agent=record),
            # En el raíz y sólo acá: el webhook lee esta llamada del stream
            # para dibujar el menú — ver core/options_tools.py.
            *options_tools.TOOLS,
        ],
```

- [ ] **Step 4: Arreglar los tests que asumen que todo `root.tools` es un `AgentTool`**

Con la función nueva en `root.tools`, `t.agent` levanta `AttributeError` en esos tests. Correr este script desde `agents/` (reemplaza los accesos por un helper que filtra los `AgentTool`):

```bash
cd agents && uv run python - <<'EOF'
HELPER = '''

def _subagentes(root):
    """Los AgentTool del raíz. `root.tools` también trae ofrecer_opciones, que
    es una función y no tiene `.agent`."""
    return [t for t in root.tools if hasattr(t, "agent")]
'''
for path in ("tests/test_core_agent.py", "tests/test_planner_and_citations.py"):
    s = open(path).read()
    s = s.replace('app._tmpl_attrs["agent"].tools', '_subagentes(app._tmpl_attrs["agent"])')
    s = s.replace("_root(app).tools", "_subagentes(_root(app))")
    s = s.replace("root.tools", "_subagentes(root)")
    # El test nuevo de Step 1 sí quiere la lista completa del raíz.
    s = s.replace(
        "assert options_tools.ofrecer_opciones in _subagentes(root)",
        "assert options_tools.ofrecer_opciones in root.tools",
    )
    s = s.replace("        for t in _subagentes(root):\n            if hasattr(t, \"agent\"):",
                  "        for t in root.tools:\n            if hasattr(t, \"agent\"):")
    # El helper va después de los imports de cabecera.
    head, sep, rest = s.partition("\n\n\n")
    s = head + HELPER + sep + rest
    open(path, "w").write(s)
EOF
grep -n "root.tools\|_subagentes" tests/test_core_agent.py tests/test_planner_and_citations.py
```

Expected: `root.tools` sólo queda en `test_el_root_tiene_la_tool_del_menu_y_los_subagentes_no` y dentro de `_subagentes`; el resto usa `_subagentes(...)`.

- [ ] **Step 5: Run the agent suite**

Run: `cd agents && uv run pytest -q`
Expected: PASS (todo verde; antes de Task 1 eran 254 passed, 7 skipped).

- [ ] **Step 6: Commit**

```bash
git add agents/core/agent.py agents/tests/test_core_agent.py agents/tests/test_planner_and_citations.py
git commit -m "feat(agents): ofrecer_opciones colgada del raíz de AA y PP

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Prompt raíz — saludo con menú y cierre con opciones

**Files:**
- Modify: `agents/core/prompts/agent_aa/root.md` (§2 y §4)
- Modify: `agents/core/prompts/agent_pp/root.md` (§2 y §4)
- Test: `agents/tests/test_prompts_root_menu.py`

**Interfaces:**
- Consumes: el nombre de la tool `ofrecer_opciones` (Task 1).
- Produces: `prompts.root_instruction(agente)` con las reglas del menú.

- [ ] **Step 1: Write the failing test**

`agents/tests/test_prompts_root_menu.py`:

```python
"""Las reglas del menú en el prompt raíz.

Mismo estilo que tests/test_prompts_record.py: cada regla afirma que la frase
correcta está y que un marcador antónimo natural NO está.
"""
import pytest

from core import prompts

AGENTES = ["agent_pp", "agent_aa"]
MENU = [
    ("Subir un verificador", "Foto o documento para una acción de tu plan"),
    ("Mi avance y puntaje", "Cómo vas en tu plan y tu nivel"),
    ("Qué me falta", "Acciones pendientes y próximas fechas"),
    ("Conocer el estándar", "Qué pide, dimensiones y puntajes"),
    ("Sustentabilidad", "Buenas prácticas para producir mejor"),
    ("Registrar una labor", "Algo que hiciste en campo o planta"),
    ("Hablar con el auditor", "Dejar o leer mensajes"),
]


def _plano(texto: str) -> str:
    return " ".join(texto.split())


@pytest.mark.parametrize("agente", AGENTES)
def test_el_saludo_obliga_el_menu_principal(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "llama SIEMPRE a `ofrecer_opciones` con este menú principal" in texto
    assert "sin menú" not in texto.lower()


@pytest.mark.parametrize("agente", AGENTES)
@pytest.mark.parametrize("titulo,descripcion", MENU)
def test_el_menu_principal_tiene_las_siete_opciones(agente, titulo, descripcion):
    texto = _plano(prompts.root_instruction(agente))
    assert f'titulo "{titulo}", descripcion "{descripcion}"' in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_los_titulos_del_menu_caben_en_whatsapp(agente):
    for titulo, descripcion in MENU:
        assert len(titulo) <= 24 and len(descripcion) <= 72


@pytest.mark.parametrize("agente", AGENTES)
def test_cierra_con_siguientes_pasos_no_con_la_frase_fija(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "llama a `ofrecer_opciones` con 2 a 4 siguientes pasos" in texto
    assert "¿Hay algo más en lo que pueda ayudarte" not in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_el_texto_no_repite_las_opciones(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "Tu texto NUNCA repite ni numera las opciones" in texto
    assert "numéralas" not in texto.lower()


@pytest.mark.parametrize("agente", AGENTES)
def test_no_ofrece_opciones_cuando_el_productor_tiene_que_escribir(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "NO la uses cuando el productor esté en medio de algo que tiene que escribir él" in texto


@pytest.mark.parametrize("agente", AGENTES)
def test_el_toque_llega_como_su_mensaje(agente):
    texto = _plano(prompts.root_instruction(agente))
    assert "trátalo como si lo hubiera escrito" in texto
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd agents && uv run pytest tests/test_prompts_root_menu.py -q`
Expected: FAIL — las frases nuevas no están y `¿Hay algo más en lo que pueda ayudarte` sí.

- [ ] **Step 3: Write minimal implementation**

Correr desde `agents/` (reemplaza §2 y §4 en los dos `root.md`; el nombre de la fase es lo único que cambia entre AA y PP):

```bash
cd agents && uv run python - <<'EOF'
import re

MENU = """\
- titulo "Subir un verificador", descripcion "Foto o documento para una acción de tu plan"
- titulo "Mi avance y puntaje", descripcion "Cómo vas en tu plan y tu nivel"
- titulo "Qué me falta", descripcion "Acciones pendientes y próximas fechas"
- titulo "Conocer el estándar", descripcion "Qué pide, dimensiones y puntajes"
- titulo "Sustentabilidad", descripcion "Buenas prácticas para producir mejor"
- titulo "Registrar una labor", descripcion "Algo que hiciste en campo o planta"
- titulo "Hablar con el auditor", descripcion "Dejar o leer mensajes"
"""

INICIO = """### 2. 🤝 Inicio de Conversación (Menú Principal)

Muchos productores no saben cómo pedir lo que necesitan. Guíalos con opciones
tocables en vez de esperar a que inventen la pregunta.

Cuando el productor saluda, escribe algo vago ("hola", "ayuda", "no sé") o te
pide el "Menú principal", saluda en UNA frase y llama SIEMPRE a
`ofrecer_opciones` con este menú principal, tal cual:

{menu}
**Ejemplo Obligatorio de texto (las opciones van en la tool, no acá):**

> ¡Hola! 👋 Soy el asistente del Estándar de Sustentabilidad de la Ciruela Deshidratada, fase de {fase}. ¿Qué quieres hacer hoy? 👇

Si el primer mensaje ya trae una pregunta concreta, respóndela directo y ofrece
las opciones al final, como en cualquier respuesta.

"""

CIERRE = """### 4. 🔁 Finalización de Cada Respuesta: Siguientes Pasos

Después de responder, llama a `ofrecer_opciones` con 2 a 4 siguientes pasos
probables para lo que acabas de responder. Por ejemplo, después de mostrarle su
avance: "Qué me falta", "Subir un verificador", "Menú principal". Si no hay un
siguiente paso claro, ofrece el menú principal. Incluye "Menú principal" entre
las opciones de cierre para que siempre pueda volver al inicio.

Úsala también para que elija entre varias cosas: por ejemplo, los títulos de
sus acciones pendientes que te trajo el EXPEDIENTE.

NO la uses cuando el productor esté en medio de algo que tiene que escribir él:
el texto de un mensaje al auditor, los datos de una labor, o cuando le acabas de
pedir un archivo.

Tu texto NUNCA repite ni numera las opciones: van sólo en `ofrecer_opciones`.
Cuando el productor toca una opción, te llega como su mensaje el título (y la
descripción) de esa opción: trátalo como si lo hubiera escrito.

"""

for agente, fase in (("agent_aa", "Adecuación Agroindustrial"),
                     ("agent_pp", "Producción Primaria")):
    path = f"core/prompts/{agente}/root.md"
    s = open(path).read()
    s, n2 = re.subn(r"### 2\. 🤝 Inicio de Conversación.*?(?=---)",
                    INICIO.format(menu=MENU, fase=fase), s, flags=re.S)
    s, n4 = re.subn(r"### 4\. 🔁 Finalización de Cada Respuesta.*?(?=---)",
                    CIERRE, s, flags=re.S)
    assert (n2, n4) == (1, 1), (path, n2, n4)
    open(path, "w").write(s)
EOF
git diff --stat
```

Expected: `root.md` de AA y PP modificados (sólo §2 y §4).

- [ ] **Step 4: Run tests**

Run: `cd agents && uv run pytest -q`
Expected: PASS (todo verde, incluidos los tests de prompts existentes).

- [ ] **Step 5: Commit**

```bash
git add agents/core/prompts/agent_aa/root.md agents/core/prompts/agent_pp/root.md agents/tests/test_prompts_root_menu.py
git commit -m "feat(agents): el raíz saluda con menú principal y cierra con siguientes pasos

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Webhook — modelo de opciones y armado de mensajes interactivos

**Files:**
- Modify: `webhook-application/whatsapp_webhook/external_services/whatsapp_client.py` (builders nuevos)
- Create: `webhook-application/whatsapp_webhook/interactive.py`
- Test: `webhook-application/tests/external_services/test_whatsapp_client.py` (agregar), `webhook-application/tests/test_interactive.py` (nuevo)

**Interfaces:**
- Produces:
  - `whatsapp_client.create_button_message(body: str, titles: list[str]) -> dict`
  - `whatsapp_client.create_list_message(body: str, button: str, rows: list[tuple[str, str]]) -> dict`
  - `interactive.Option(title: str, description: str = "")` (dataclass frozen)
  - `interactive.AgentReply(text: str, options: list[Option] | None = None, button: str = "Ver opciones")` (dataclass)
  - `interactive.parse_options(args: Any) -> tuple[list[Option], str] | None`
  - `interactive.build_reply_messages(reply: AgentReply) -> list[dict]`
  - `interactive.numbered_fallback(reply: AgentReply, include_text: bool) -> dict`
  - constantes `DEFAULT_BUTTON_LABEL = "Ver opciones"`, `DEFAULT_BODY = "¿Qué quieres hacer ahora?"`

- [ ] **Step 1: Write the failing tests**

Agregar al final de `webhook-application/tests/external_services/test_whatsapp_client.py`:

```python
def test_create_button_message_shape():
    msg = wc.create_button_message("¿Seguimos?", ["Sí", "No"])
    assert msg == {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "¿Seguimos?"},
            "action": {"buttons": [
                {"type": "reply", "reply": {"id": "opt_1", "title": "Sí"}},
                {"type": "reply", "reply": {"id": "opt_2", "title": "No"}},
            ]},
        },
    }


def test_create_list_message_shape_omits_empty_description():
    msg = wc.create_list_message("Elige", "Ver opciones",
                                 [("Qué me falta", "Pendientes"), ("Menú principal", "")])
    assert msg == {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "Elige"},
            "action": {
                "button": "Ver opciones",
                "sections": [{"title": "Opciones", "rows": [
                    {"id": "opt_1", "title": "Qué me falta", "description": "Pendientes"},
                    {"id": "opt_2", "title": "Menú principal"},
                ]}],
            },
        },
    }
```

`webhook-application/tests/test_interactive.py`:

```python
"""Del `ofrecer_opciones` del agente al mensaje de WhatsApp (puro, sin red)."""
import pytest

from whatsapp_webhook.interactive import (
    DEFAULT_BODY,
    AgentReply,
    Option,
    build_reply_messages,
    numbered_fallback,
    parse_options,
)

SIETE = [Option(f"Opción {i}", f"Descripción {i}") for i in range(1, 8)]


# ----------------------------------------------------------------- parse_options
def test_parse_options_ok():
    args = {"opciones": [{"titulo": "Qué me falta", "descripcion": "Pendientes"},
                         {"titulo": "Menú principal"}], "boton": "Ver"}
    assert parse_options(args) == (
        [Option("Qué me falta", "Pendientes"), Option("Menú principal", "")], "Ver"
    )


def test_parse_options_boton_vacio_usa_el_de_siempre():
    assert parse_options({"opciones": [{"titulo": "A"}], "boton": ""})[1] == "Ver opciones"


@pytest.mark.parametrize("args", [
    None,
    "texto",
    {},
    {"opciones": []},
    {"opciones": [{"titulo": f"O{i}"} for i in range(11)]},
    {"opciones": [{"titulo": ""}]},
    {"opciones": [{"titulo": "x" * 25}]},
    {"opciones": [{"titulo": "A", "descripcion": "x" * 73}]},
    {"opciones": [{"titulo": "A"}, {"titulo": " a "}]},
    {"opciones": ["A"]},
    {"opciones": [{"titulo": "A"}], "boton": "x" * 21},
])
def test_parse_options_rechaza_lo_que_whatsapp_no_acepta(args):
    assert parse_options(args) is None


# ---------------------------------------------------------- build_reply_messages
def test_sin_opciones_es_texto():
    assert build_reply_messages(AgentReply("Hola")) == [
        {"type": "text", "text": {"body": "Hola", "preview_url": False}}
    ]


def test_tres_cortas_son_botones():
    msgs = build_reply_messages(AgentReply("¿Seguimos?", [Option("Sí"), Option("No"), Option("Menú principal")]))
    assert len(msgs) == 1
    assert msgs[0]["interactive"]["type"] == "button"
    assert msgs[0]["interactive"]["body"]["text"] == "¿Seguimos?"


def test_tres_con_un_titulo_de_21_es_lista():
    msgs = build_reply_messages(AgentReply("Elige", [Option("A"), Option("B"), Option("x" * 21)]))
    assert msgs[0]["interactive"]["type"] == "list"


def test_siete_es_lista_con_descripciones_y_boton():
    msgs = build_reply_messages(AgentReply("Hola", SIETE, "Ver opciones"))
    inter = msgs[0]["interactive"]
    assert inter["type"] == "list"
    assert inter["action"]["button"] == "Ver opciones"
    assert inter["action"]["sections"][0]["rows"][0] == {
        "id": "opt_1", "title": "Opción 1", "description": "Descripción 1"
    }


def test_texto_largo_va_aparte_y_el_interactivo_con_cuerpo_corto():
    largo = "x" * 1100
    msgs = build_reply_messages(AgentReply(largo, SIETE))
    assert msgs[0] == {"type": "text", "text": {"body": largo, "preview_url": False}}
    assert msgs[1]["interactive"]["body"]["text"] == DEFAULT_BODY


def test_sin_texto_con_opciones_usa_el_cuerpo_por_defecto():
    """Review Focus 1: el modelo llamó la tool pero no escribió nada."""
    msgs = build_reply_messages(AgentReply("", SIETE))
    assert len(msgs) == 1
    assert msgs[0]["interactive"]["body"]["text"] == DEFAULT_BODY


# --------------------------------------------------------------- numbered_fallback
def test_fallback_numerado_con_texto():
    body = numbered_fallback(AgentReply("Hola", [Option("Sí"), Option("No")]), include_text=True)["text"]["body"]
    assert body.startswith("Hola")
    assert "1. Sí" in body and "2. No" in body
    # Review Focus 5: le dice cómo contestar.
    assert "Responde con el número" in body


def test_fallback_numerado_sin_texto_no_lo_repite():
    body = numbered_fallback(AgentReply("Hola", [Option("Sí")]), include_text=False)["text"]["body"]
    assert "Hola" not in body
    assert "1. Sí" in body
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd webhook-application && uv run --extra dev pytest tests/test_interactive.py tests/external_services/test_whatsapp_client.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'whatsapp_webhook.interactive'` y `AttributeError: ... has no attribute 'create_button_message'`.

- [ ] **Step 3: Write minimal implementation**

En `webhook-application/whatsapp_webhook/external_services/whatsapp_client.py`, después de `create_document_message`:

```python
def create_button_message(body: str, titles: list[str]) -> Dict[str, Any]:
    """Mensaje con 1-3 botones de respuesta (título ≤ 20, cuerpo ≤ 1024)."""
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": [
                {"type": "reply", "reply": {"id": f"opt_{i}", "title": title}}
                for i, title in enumerate(titles, 1)
            ]},
        },
    }


def create_list_message(body: str, button: str, rows: list[tuple[str, str]]) -> Dict[str, Any]:
    """Mensaje de lista: un botón que abre 1-10 filas (título ≤ 24, descripción ≤ 72).

    La descripción vacía se omite: la Cloud API rechaza `"description": ""`.
    """
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "action": {
                "button": button,
                "sections": [{"title": "Opciones", "rows": [
                    {"id": f"opt_{i}", "title": title, **({"description": desc} if desc else {})}
                    for i, (title, desc) in enumerate(rows, 1)
                ]}],
            },
        },
    }
```

`webhook-application/whatsapp_webhook/interactive.py`:

```python
"""Opciones tocables de WhatsApp: de la llamada `ofrecer_opciones` del agente a
botones o lista, con fallback a texto numerado.

El agente decide QUÉ ofrecer (agents/core/options_tools.py); acá sólo se dibuja.
Los límites se repiten a propósito: el agente es otro deploy y no se puede
importar, y un menú que la Cloud API rechaza deja al productor sin respuesta.
Ver docs/superpowers/specs/2026-10-09-menu-opciones-whatsapp-design.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .external_services.whatsapp_client import (
    create_button_message,
    create_list_message,
    create_text_message,
)

MAX_OPTIONS = 10
MAX_BUTTONS = 3
MAX_BUTTON_TITLE = 20
MAX_ROW_TITLE = 24
MAX_DESCRIPTION = 72
MAX_BUTTON_LABEL = 20
MAX_BODY = 1024
DEFAULT_BUTTON_LABEL = "Ver opciones"
DEFAULT_BODY = "¿Qué quieres hacer ahora?"


@dataclass(frozen=True)
class Option:
    title: str
    description: str = ""


@dataclass
class AgentReply:
    """La respuesta del agente lista para WhatsApp: texto y, si las ofreció, opciones."""

    text: str
    options: Optional[list[Option]] = None
    button: str = DEFAULT_BUTTON_LABEL


def parse_options(args: Any) -> Optional[tuple[list[Option], str]]:
    """Valida los `args` de una llamada a `ofrecer_opciones`. None si no sirven.

    Mismos límites que agents/core/options_tools.py. Se re-validan porque el
    webhook ve la llamada aunque la tool la haya rechazado con `ok: False`.
    """
    if not isinstance(args, dict):
        return None
    raw = args.get("opciones")
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_OPTIONS:
        return None
    options: list[Option] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            return None
        title = str(item.get("titulo") or "").strip()
        description = str(item.get("descripcion") or "").strip()
        if not title or len(title) > MAX_ROW_TITLE or len(description) > MAX_DESCRIPTION:
            return None
        if title.casefold() in seen:
            return None
        seen.add(title.casefold())
        options.append(Option(title, description))
    button = str(args.get("boton") or "").strip() or DEFAULT_BUTTON_LABEL
    if len(button) > MAX_BUTTON_LABEL:
        return None
    return options, button


def build_reply_messages(reply: AgentReply) -> list[dict]:
    """Los mensajes a enviar, en orden.

    Sin opciones: el texto. Con opciones: botones si son ≤3 y caben en 20
    caracteres, lista si no. Un texto que no cabe en el cuerpo de un
    interactivo (1024) sale antes como texto y el interactivo lleva un cuerpo
    corto; lo mismo si el agente no escribió nada.
    """
    text = reply.text.strip()
    if not reply.options:
        return [create_text_message(text)]
    messages: list[dict] = []
    body = text
    if len(text) > MAX_BODY:
        messages.append(create_text_message(text))
        body = DEFAULT_BODY
    elif not text:
        body = DEFAULT_BODY
    if len(reply.options) <= MAX_BUTTONS and all(
        len(o.title) <= MAX_BUTTON_TITLE for o in reply.options
    ):
        messages.append(create_button_message(body, [o.title for o in reply.options]))
    else:
        messages.append(create_list_message(
            body, reply.button, [(o.title, o.description) for o in reply.options]
        ))
    return messages


def numbered_fallback(reply: AgentReply, include_text: bool) -> dict:
    """Las opciones como texto numerado, para cuando el interactivo no salió.

    `include_text=False` cuando el texto ya se mandó aparte (no se repite).
    """
    parts: list[str] = []
    if include_text and reply.text.strip():
        parts.append(reply.text.strip())
    parts.append("\n".join(f"{i}. {o.title}" for i, o in enumerate(reply.options or [], 1)))
    parts.append("Responde con el número o escríbeme lo que necesitas.")
    return create_text_message("\n\n".join(parts))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd webhook-application && uv run --extra dev pytest tests/test_interactive.py tests/external_services/test_whatsapp_client.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add webhook-application/whatsapp_webhook/interactive.py webhook-application/whatsapp_webhook/external_services/whatsapp_client.py webhook-application/tests/test_interactive.py webhook-application/tests/external_services/test_whatsapp_client.py
git commit -m "feat(webhook): armado de botones y listas de WhatsApp desde ofrecer_opciones

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Webhook — leer `ofrecer_opciones` del stream del agente

**Files:**
- Modify: `webhook-application/whatsapp_webhook/external_services/agent_client.py` (`send_to_agent`)
- Test: `webhook-application/tests/external_services/test_agent_client.py`

**Interfaces:**
- Consumes: `interactive.parse_options`, `interactive.Option` (Task 4).
- Produces: `send_to_agent(...)` devuelve además `"options": list[Option] | None` y `"button": str | None`. Con opciones y sin texto, `"response"` es `""` (no el error de respuesta vacía).

- [ ] **Step 1: Write the failing tests**

Agregar en `webhook-application/tests/external_services/test_agent_client.py` (antes de `test_send_to_agent_returns_error_payload_when_no_text`):

```python
def _engine_que_emite(*events):
    async def fake_stream(*, user_id, session_id, message):
        for e in events:
            yield e
    engine = MagicMock()
    engine.async_stream_query = lambda **kw: fake_stream(**kw)
    return engine


def _llamada(args):
    return {"content": {"parts": [{"function_call": {"name": "ofrecer_opciones", "args": args}}]}}


async def _consultar(engine):
    from whatsapp_webhook.external_services import agent_client
    with patch.object(agent_client, "get_engine", return_value=engine):
        return await agent_client.send_to_agent(
            app_name="agent_aa", user_id="+56999", session_id="+56999", message="hola",
        )


@pytest.mark.asyncio
async def test_send_to_agent_toma_la_ultima_llamada_valida_a_ofrecer_opciones():
    """Review Focus 2: el modelo reintentó tras ok:False; vale la última."""
    from whatsapp_webhook.interactive import Option
    engine = _engine_que_emite(
        _llamada({"opciones": [{"titulo": "x" * 30}]}),
        {"content": {"parts": [{"function_response": {"name": "ofrecer_opciones",
                                                      "response": {"ok": False}}}]}},
        _llamada({"opciones": [{"titulo": "Qué me falta", "descripcion": "Pendientes"}],
                  "boton": "Ver"}),
        {"content": {"parts": [{"text": "Hola"}]}},
    )
    result = await _consultar(engine)
    assert result["response"] == "Hola"
    assert result["options"] == [Option("Qué me falta", "Pendientes")]
    assert result["button"] == "Ver"


@pytest.mark.asyncio
async def test_send_to_agent_si_la_ultima_llamada_es_invalida_no_hay_opciones():
    engine = _engine_que_emite(
        _llamada({"opciones": [{"titulo": "Sí"}]}),
        _llamada({"opciones": [{"titulo": "x" * 30}]}),
        {"content": {"parts": [{"text": "Hola"}]}},
    )
    result = await _consultar(engine)
    assert result["response"] == "Hola"
    assert result["options"] is None


@pytest.mark.asyncio
async def test_send_to_agent_ignora_otras_tools():
    engine = _engine_que_emite(
        {"content": {"parts": [{"function_call": {"name": "aa_agent_record", "args": {"request": "x"}}}]}},
        {"content": {"parts": [{"text": "Hola"}]}},
    )
    result = await _consultar(engine)
    assert result["options"] is None


@pytest.mark.asyncio
async def test_send_to_agent_opciones_sin_texto_no_es_error():
    """Review Focus 1: llamó la tool y no escribió: no es 'respuesta vacía'."""
    engine = _engine_que_emite(_llamada({"opciones": [{"titulo": "Menú principal"}]}))
    result = await _consultar(engine)
    assert result["response"] == ""
    assert result["options"] is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd webhook-application && uv run --extra dev pytest tests/external_services/test_agent_client.py -q -k "ofrecer_opciones or opciones or otras_tools"`
Expected: FAIL — `KeyError: 'options'` (y el caso sin texto devuelve el error de respuesta vacía).

- [ ] **Step 3: Write minimal implementation**

En `agent_client.py`, import (junto a los otros relativos):

```python
from ..interactive import parse_options
```

En `send_to_agent`, junto a `out`/`raw_events`:

```python
    out: list[str] = []
    raw_events: list[dict] = []
    # La ÚLTIMA llamada a ofrecer_opciones del turno: si el modelo reintentó
    # tras un ok:False, la que vale es la final (ver interactive.parse_options).
    options_args: dict | None = None
```

En el `for attempt ...`, después de `raw_events.clear()`:

```python
        options_args = None
```

Reemplazar el bloque que recorre las partes:

```python
                    content = event.get("content") or {}
                    for part in content.get("parts") or []:
                        text = part.get("text")
                        if text:
                            out.append(text)
```

por:

```python
                    content = event.get("content") or {}
                    for part in content.get("parts") or []:
                        text = part.get("text")
                        if text:
                            out.append(text)
                        call = part.get("function_call") or {}
                        if call.get("name") == "ofrecer_opciones":
                            options_args = call.get("args")
```

Reemplazar desde `response_text = normalize_whatsapp_markdown("".join(out))` hasta el `return` final por:

```python
    response_text = normalize_whatsapp_markdown("".join(out))
    parsed = parse_options(options_args) if options_args is not None else None
    options, button = parsed if parsed else (None, None)
    if not response_text and not options:
        _logger.warning(
            "agent_query.empty_response",
            extra={
                "app_name": app_name,
                "user_id": user_id,
                "events_received": len(raw_events),
            },
        )
        return {
            "response": "Error: Could not extract text from agent response.",
            "raw_response": raw_events,
        }
    _logger.info(
        "agent_query.complete",
        extra={
            "app_name": app_name,
            "user_id": user_id,
            "events_received": len(raw_events),
            "response_chars": len(response_text),
            "options": len(options) if options else 0,
        },
    )
    return {
        "response": response_text,
        "options": options,
        "button": button,
        "raw_response": raw_events,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd webhook-application && uv run --extra dev pytest tests/external_services/test_agent_client.py -q`
Expected: PASS (incluidos los tests existentes de `send_to_agent`).

- [ ] **Step 5: Commit**

```bash
git add webhook-application/whatsapp_webhook/external_services/agent_client.py webhook-application/tests/external_services/test_agent_client.py
git commit -m "feat(webhook): send_to_agent recoge las opciones de ofrecer_opciones

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Webhook — enviar la respuesta con opciones (texto, audio y media)

**Files:**
- Modify: `webhook-application/whatsapp_webhook/messages.py`
- Test: `webhook-application/tests/test_messages.py`

**Interfaces:**
- Consumes: `AgentReply`, `Option`, `DEFAULT_BUTTON_LABEL`, `build_reply_messages`, `numbered_fallback` (Task 4); `send_to_agent` con `options`/`button` (Task 5).
- Produces:
  - `send_message_to_agent(...) -> AgentReply` (antes `str`)
  - `send_agent_reply(phone: str, reply: AgentReply | str, api_url: str, token: str) -> None`
  - `_whatsapp_endpoint(app_name: str) -> tuple[str, str] | None` → `(f"{facebook_app_url}/messages", token)`

- [ ] **Step 1: Write the failing tests**

Agregar import arriba de `tests/test_messages.py`:

```python
from whatsapp_webhook.interactive import AgentReply, Option
```

Ajustar los tres tests que comparan el `str` que devolvía `send_message_to_agent`:

```python
    assert "no configurado" in out.text
```

```python
    assert "comunicación" in out.text.lower()
```

```python
    assert out.text == "listo"
```

(en `test_send_message_to_agent_value_error_returns_config_message`, `test_send_message_to_agent_generic_error_returns_comm_message` y `test_send_message_to_agent_pasa_el_user_id_ya_resuelto_sin_resolver_de_nuevo` respectivamente).

Agregar al final:

```python
# --------------------------------------------------------------------------- #
# Respuestas con opciones (menú interactivo)
# --------------------------------------------------------------------------- #
SIETE = [Option(f"Opción {i}", f"Descripción {i}") for i in range(1, 8)]


@pytest.mark.asyncio
async def test_send_message_to_agent_pasa_las_opciones():
    with patch.object(messages, "send_to_agent", AsyncMock(return_value={
        "response": "Hola", "options": SIETE, "button": "Ver"})):
        out = await messages.send_message_to_agent(WA_ID, AA, WA_ID, "hola")
    assert out == AgentReply("Hola", SIETE, "Ver")


@pytest.mark.asyncio
async def test_send_agent_reply_con_un_str_manda_texto():
    with patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.send_agent_reply(WA_ID, "Hola", "u", "t")
    assert send.await_args.args[1]["text"]["body"] == "Hola"


@pytest.mark.asyncio
async def test_send_agent_reply_con_opciones_cortas_manda_botones():
    with patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.send_agent_reply(WA_ID, AgentReply("¿Seguimos?", [Option("Sí"), Option("No")]), "u", "t")
    send.assert_awaited_once()
    assert send.await_args.args[1]["interactive"]["type"] == "button"


@pytest.mark.asyncio
async def test_si_falla_el_interactivo_cae_a_texto_numerado():
    send = AsyncMock(side_effect=[RuntimeError("400 Bad Request"), {}])
    with patch.object(messages, "send_whatsapp_message", send):
        await messages.send_agent_reply(WA_ID, AgentReply("Hola", [Option("Sí"), Option("No")]), "u", "t")
    assert send.await_count == 2
    body = send.await_args_list[1].args[1]["text"]["body"]
    assert body.startswith("Hola") and "1. Sí" in body and "2. No" in body


@pytest.mark.asyncio
async def test_texto_largo_no_se_repite_en_el_fallback():
    """Review Focus 3."""
    largo = "x" * 1100
    send = AsyncMock(side_effect=[{}, RuntimeError("400"), {}])
    with patch.object(messages, "send_whatsapp_message", send):
        await messages.send_agent_reply(WA_ID, AgentReply(largo, SIETE), "u", "t")
    assert send.await_count == 3
    fallback = send.await_args_list[2].args[1]["text"]["body"]
    assert largo not in fallback and "1. Opción 1" in fallback


@pytest.mark.asyncio
async def test_si_falla_el_texto_se_propaga():
    """El texto no tiene fallback: el manejador ya captura y avisa el error."""
    with patch.object(messages, "send_whatsapp_message", AsyncMock(side_effect=RuntimeError("x"))):
        with pytest.raises(RuntimeError):
            await messages.send_agent_reply(WA_ID, "Hola", "u", "t")


@pytest.mark.asyncio
async def test_texto_entrante_con_opciones_responde_con_lista():
    with patch.object(messages, "create_agent_session", AsyncMock()), \
         patch.object(messages, "send_to_agent", AsyncMock(return_value={
             "response": "¡Hola! ¿Qué quieres hacer hoy?", "options": SIETE,
             "button": "Ver opciones"})), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.process_message(WA_ID, _text_msg(), AA)
    payload = send.await_args.args[1]
    assert payload["interactive"]["type"] == "list"
    assert payload["interactive"]["body"]["text"] == "¡Hola! ¿Qué quieres hacer hoy?"


@pytest.mark.asyncio
async def test_media_con_opciones_responde_con_botones():
    async def fake_send(uid, app, sess, msg):
        return AgentReply("Lo guardé en Calibración", [Option("Subir otro"), Option("Menú principal")])

    with patch.object(messages, "download_whatsapp_media", AsyncMock(return_value=b"\xff\xd8img")), \
         patch.object(messages, "upload_media", AsyncMock(return_value="gs://b/x.jpg")), \
         patch.object(messages, "send_message_to_agent", fake_send), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.handle_media_message(WA_ID, WA_ID, "mid", "image/jpeg", "", "", AA)
    assert send.await_args.args[1]["interactive"]["type"] == "button"


def test_whatsapp_endpoint_por_app(monkeypatch):
    monkeypatch.setattr(config, "aa_facebook_app_url", "https://graph.example/aa")
    assert messages._whatsapp_endpoint(AA) == (
        "https://graph.example/aa/messages", "test-wsp-token-aa"
    )
    assert messages._whatsapp_endpoint("agent_unknown") is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd webhook-application && uv run --extra dev pytest tests/test_messages.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'send_agent_reply'` / `'_whatsapp_endpoint'`, y `out.text` sobre un `str`.

- [ ] **Step 3: Write minimal implementation**

En `whatsapp_webhook/messages.py`:

1. Imports: agregar

```python
from .interactive import (
    DEFAULT_BUTTON_LABEL,
    AgentReply,
    build_reply_messages,
    numbered_fallback,
)
```

2. `send_message_to_agent`: cambiar la firma a `-> AgentReply` y el cuerpo del `try`/`except` a:

```python
    try:
        response_data = await send_to_agent(app_name, agent_user_id, session_id, message)
        return AgentReply(
            text=response_data.get(
                "response", "Error: No se pudo extraer el texto de la respuesta."
            ),
            options=response_data.get("options"),
            button=response_data.get("button") or DEFAULT_BUTTON_LABEL,
        )
    except ValueError as e:
        logger.error(f"Configuration error: {e}", exc_info=True)
        return AgentReply("Error: Servicio de agente no configurado.")
    except Exception as e:
        logger.error(f"Error communicating with agent: {e}", exc_info=True)
        return AgentReply("Error: Fallo la comunicación con el servicio del agente.")
```

3. Agregar, antes de `_send_whatsapp_acknowledgment`:

```python
def _whatsapp_endpoint(app_name: str) -> Optional[tuple[str, str]]:
    """(url de /messages, token) de ESTA app, o None si falta configuración.

    AA y PP mandan desde números distintos con tokens distintos (ver
    config.token_for).
    """
    if app_name == config.aa_app_name:
        facebook_app_url = config.aa_facebook_app_url
    elif app_name == config.pp_app_name:
        facebook_app_url = config.pp_facebook_app_url
    else:
        logging.error(f"Unknown app name: {app_name}")
        return None
    wsp_token = config.token_for(app_name)
    if not facebook_app_url or not wsp_token:
        logging.error(f"WhatsApp API URL or token is not configured for {app_name}.")
        return None
    return f"{facebook_app_url}/messages", wsp_token


async def send_agent_reply(
    phone: str, reply: "AgentReply | str", api_url: str, token: str
) -> None:
    """Manda la respuesta del agente: texto y, si las ofreció, sus opciones.

    Si el interactivo falla (la Cloud API lo rechaza) se reenvía como texto con
    las opciones numeradas: el productor nunca se queda sin respuesta. Un fallo
    del TEXTO se propaga; los manejadores ya lo capturan y avisan.
    """
    if isinstance(reply, str):
        reply = AgentReply(text=reply)
    outgoing = build_reply_messages(reply)
    for i, message in enumerate(outgoing):
        if message.get("type") != "interactive":
            await send_whatsapp_message(phone, message, api_url, token)
            continue
        try:
            await send_whatsapp_message(phone, message, api_url, token)
        except Exception as e:  # noqa: BLE001 — cualquier rechazo cae al texto
            logging.warning(f"Interactive send failed, falling back to text: {e}")
            await send_whatsapp_message(
                phone, numbered_fallback(reply, include_text=(i == 0)), api_url, token
            )
```

4. `_send_whatsapp_acknowledgment`: reemplazar la resolución de url/token por el helper:

```python
    logger = get_logger("whatsapp_ack", {"app_name": app_name})
    endpoint = _whatsapp_endpoint(app_name)
    if endpoint is None:
        return False

    try:
        message = create_text_message(message_text)
        await send_whatsapp_message(user_wa_id, message, *endpoint)
        logger.info(f"Acknowledgment sent successfully to {mask_pii(user_wa_id)}")
        return True
    except Exception as e:
        logger.error(f"Failed to send acknowledgment: {e}", exc_info=True)
        return False
```

5. `_process_single_text_message`: reemplazar el cuerpo por:

```python
    message_text = message.get_message_content() or ""
    reply = await send_message_to_agent(
        agent_user_id, app_name, session_id_for(sender_wa_id, agent_user_id), message_text
    )
    if not reply.text.strip() and not reply.options:
        reply = AgentReply("No pude procesar tu mensaje. Intenta de nuevo.")
    endpoint = _whatsapp_endpoint(app_name)
    if endpoint is None:
        return
    try:
        await send_agent_reply(sender_wa_id, reply, *endpoint)
    except Exception as e:  # noqa: BLE001 — mismo contrato que el acuse: loguea y sigue
        logging.error(f"Failed to send agent reply: {e}", exc_info=True)
```

6. `handle_audio_message` y `handle_media_message`: el envío de la respuesta del agente

```python
        await send_whatsapp_message(
            phone, create_text_message(response), f"{facebook_app_url}/messages", wsp_token
        )
```

pasa a (las dos apariciones; los acuses de error con `create_text_message("...")` literal NO se tocan):

```python
        await send_agent_reply(phone, response, f"{facebook_app_url}/messages", wsp_token)
```

- [ ] **Step 4: Run the webhook suite**

Run: `cd webhook-application && uv run --extra dev pytest -q`
Expected: PASS (todo verde, incluidos los tests de audio/media existentes: sus mocks devuelven `str`, que `send_agent_reply` manda como texto).

- [ ] **Step 5: Commit**

```bash
git add webhook-application/whatsapp_webhook/messages.py webhook-application/tests/test_messages.py
git commit -m "feat(webhook): responde con botones o lista cuando el agente ofrece opciones

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Webhook — el toque de una opción vuelve al agente como texto

**Files:**
- Modify: `webhook-application/whatsapp_webhook/models/messages.py` (`WhatsAppInteractiveContent`, `WhatsAppMessage`)
- Modify: `webhook-application/whatsapp_webhook/messages.py` (despacho en `process_message`)
- Test: `webhook-application/tests/test_models.py`, `webhook-application/tests/test_messages.py`

**Interfaces:**
- Produces: `WhatsAppMessage.interactive_reply_text() -> str | None`; `get_message_content()` devuelve ese texto para `interactive`.

- [ ] **Step 1: Write the failing tests**

Agregar al final de `webhook-application/tests/test_models.py`:

```python
def _tap(kind, **reply):
    from whatsapp_webhook.models.messages import WhatsAppMessage
    return WhatsAppMessage.model_validate({
        "id": "wamid.tap", "type": "interactive", "timestamp": "0", "from": "56912345678",
        "interactive": {"type": kind, kind: reply},
    })


def test_list_reply_se_lee_como_titulo_y_descripcion():
    m = _tap("list_reply", id="opt_3", title="Qué me falta",
             description="Acciones pendientes y próximas fechas")
    assert m.interactive_reply_text() == "Qué me falta — Acciones pendientes y próximas fechas"
    assert m.get_message_content() == m.interactive_reply_text()


def test_button_reply_se_lee_como_titulo():
    m = _tap("button_reply", id="opt_1", title="Sí")
    assert m.interactive_reply_text() == "Sí"


def test_interactive_que_no_es_un_toque_no_tiene_texto():
    """Review Focus 4: p. ej. la respuesta de un Flow."""
    m = _tap("nfm_reply", response_json="{}", body="Sent")
    assert m.interactive_reply_text() is None
    assert m.get_message_content() == "[Interactive message]"
```

Agregar al final de `webhook-application/tests/test_messages.py`:

```python
def _tap_msg(kind="list_reply", **reply):
    return WhatsAppMessage.model_validate(
        {"id": "wamid.tap", "type": "interactive", "timestamp": "0", "from": WA_ID,
         "interactive": {"type": kind, kind: reply}}
    )


@pytest.mark.asyncio
async def test_toque_de_una_opcion_va_al_agente_como_texto():
    visto = {}

    async def fake_send_to_agent(app_name, user_id, session_id, message):
        visto["message"] = message
        return {"response": "Te faltan 3 acciones"}

    with patch.object(messages, "create_agent_session", AsyncMock()), \
         patch.object(messages, "send_to_agent", fake_send_to_agent), \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.process_message(
            WA_ID, _tap_msg(id="opt_3", title="Qué me falta", description="Acciones pendientes"), AA
        )
    assert visto["message"] == "Qué me falta — Acciones pendientes"
    assert send.await_args.args[1]["text"]["body"] == "Te faltan 3 acciones"


@pytest.mark.asyncio
async def test_interactive_sin_toque_sigue_en_el_acuse():
    with patch.object(messages, "create_agent_session", AsyncMock()), \
         patch.object(messages, "send_to_agent", AsyncMock()) as agent, \
         patch.object(messages, "send_whatsapp_message", AsyncMock()) as send:
        await messages.process_message(WA_ID, _tap_msg("nfm_reply", response_json="{}"), AA)
    agent.assert_not_awaited()
    assert "imágenes y PDF" in send.await_args.args[1]["text"]["body"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd webhook-application && uv run --extra dev pytest tests/test_models.py tests/test_messages.py -q -k "reply or toque or interactive"`
Expected: FAIL — `AttributeError: 'WhatsAppMessage' object has no attribute 'interactive_reply_text'`.

- [ ] **Step 3: Write minimal implementation**

En `whatsapp_webhook/models/messages.py`, reemplazar `WhatsAppInteractiveContent` por:

```python
class WhatsAppInteractiveReply(BaseModel):
    """El botón o la fila que tocó el usuario."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = Field(None, description="Id del botón o fila (opt_N)")
    title: Optional[str] = Field(None, description="Título tocado")
    description: Optional[str] = Field(None, description="Descripción de la fila, si tenía")


class WhatsAppInteractiveContent(BaseModel):
    """Interactive content (buttons, lists, etc.)."""

    model_config = ConfigDict(extra="allow")

    type: Optional[str] = Field(None, description="Interactive type")
    button_reply: Optional[WhatsAppInteractiveReply] = Field(None, description="Botón tocado")
    list_reply: Optional[WhatsAppInteractiveReply] = Field(None, description="Fila tocada")
```

En `WhatsAppMessage`, agregar antes de `get_message_content`:

```python
    def interactive_reply_text(self) -> Optional[str]:
        """El toque de un botón o fila como texto: "título — descripción".

        La descripción va porque el título solo ("Qué me falta") pierde el
        contexto del menú. None si no es un toque reconocible (p. ej. un Flow).
        """
        if self.type != "interactive" or not self.interactive:
            return None
        reply = self.interactive.button_reply or self.interactive.list_reply
        title = (reply.title or "").strip() if reply else ""
        if not title:
            return None
        description = (reply.description or "").strip()
        return f"{title} — {description}" if description else title
```

y en `get_message_content`, cambiar la rama `interactive`:

```python
        elif self.type == "interactive":
            return self.interactive_reply_text() or "[Interactive message]"
```

En `whatsapp_webhook/messages.py` (`process_message`), cambiar la primera rama del despacho:

```python
    if message.type == "text" or message.interactive_reply_text():
        # Un toque de botón/lista es texto para el agente: mismo camino.
        await _process_single_text_message(sender_wa_id, agent_user_id, message, app_name)
```

- [ ] **Step 4: Run the webhook suite**

Run: `cd webhook-application && uv run --extra dev pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add webhook-application/whatsapp_webhook/models/messages.py webhook-application/whatsapp_webhook/messages.py webhook-application/tests/test_models.py webhook-application/tests/test_messages.py
git commit -m "feat(webhook): el toque de un botón o fila vuelve al agente como texto

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Verificación final

**Files:** ninguno nuevo.

- [ ] **Step 1: Correr las dos suites completas**

Run: `cd agents && uv run pytest -q` → Expected: PASS, 0 failed.
Run: `cd webhook-application && uv run --extra dev pytest -q` → Expected: PASS, 0 failed.

- [ ] **Step 2: Revisar el diff contra el spec**

Run: `git diff main --stat` y confirmar que sólo cambian: `agents/core/{options_tools.py,agent.py,prompts/agent_{aa,pp}/root.md}`, `webhook-application/whatsapp_webhook/{interactive.py,messages.py,models/messages.py,external_services/{agent_client.py,whatsapp_client.py}}`, sus tests, y los docs del spec/plan.

- [ ] **Step 3: Anotar el orden de deploy en la descripción del PR**

Webhook primero (sin la tool no hay opciones: responde texto como hoy), después los agentes AA y PP. La rama `fix/evidence-attach-media-id` también toca `agent_client.py` y los `root.md`/`record.md`: resolver el conflicto al mergear la segunda.
