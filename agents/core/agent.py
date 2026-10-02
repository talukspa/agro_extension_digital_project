"""Single factory for both agents. build_app(...) returns a deploy-ready AdkApp.

The agent `name` prefix (e.g. "aa_agent") derives the sub-agent names so traces
stay readable. The main datastore env var name differs per agent; guides/faq/
chileprunes datastores are shared across both.
"""
import functools
import os

from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool, agent_tool
from vertexai.agent_engines import AdkApp

from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig

from core import catalog_tools, consent_guard, producer_scope, prompts, record_tools
from core.llm_global import GlobalGemini
from core.retry_plugin import OkContractRetryPlugin

# Model choices are per-role, and the cheap one is NOT the obvious one.
#
# Modelos GA (2.5) en vez de los 3.x preview. Los 3.x (gemini-3.7-flash /
# 3.1-flash-lite) sólo se sirven desde la location `global`, que comparte una
# pool de quota de preview chica: en prod devolvía 429 RESOURCE_EXHAUSTED en
# casi cada turno (texto e imágenes por igual). Los 2.5 son GA, multimodales
# (imágenes/PDF), y con `GEMINI_LOCATION=us-central1` usan la quota regional
# dedicada del proyecto. Volver a un 3.x cuando su quota esté resuelta es sólo
# cambiar estas constantes de vuelta (y GEMINI_LOCATION a `global`).
ROOT_MODEL = "gemini-2.5-flash"
CATALOG_MODEL = "gemini-2.5-flash"
RAG_MODEL = "gemini-2.5-flash-lite"

# El expediente es lectura y ESCRITURA sobre el productor: adjunta respaldos,
# registra labores, publica mensajes al auditor. Se le da el mismo modelo que al
# root en lugar del flash-lite de RAG porque equivocarse acá deja un registro
# mal puesto en el expediente de una persona, no una respuesta imprecisa.
RECORD_MODEL = "gemini-2.5-flash"


def _tool_max_retries() -> int:
    """Consecutive tool failures before the plugin stops reflecting.

    Read per call, never bound at import — same reason as the caps in
    core/catalog_tools.py: an import-time binding is untestable via monkeypatch and
    silently ignores the per-engine override.
    """
    return int(os.environ.get("TOOL_MAX_RETRIES", "3"))


def _planner():
    """BuiltInPlanner for the root + catalog agents, or None.

    DEFAULT IS OFF. #44 estimated "+10-15% tokens", but thinking tokens bill at
    OUTPUT rate and a WhatsApp reply is only 100-500 tokens — a 2048-token
    budget can cost more than the answer. Ship dark, flip AGENT_PLANNER=builtin
    on ONE engine, and compare against real npe traffic before defaulting it on.

    PlanReActPlanner is deliberately not offered: it adds a full extra LLM
    round-trip per planning step, which WhatsApp latency cannot absorb.

    Env is read per call, never bound at import — see the note in catalog_tools.
    """
    if os.environ.get("AGENT_PLANNER", "off") != "builtin":
        return None
    return BuiltInPlanner(
        thinking_config=ThinkingConfig(
            include_thoughts=True,
            thinking_budget=int(os.environ.get("AGENT_THINK_BUDGET", "2048")),
        )
    )


def _prefix(name: str) -> str:
    # "aa_agent" -> "agent_aa" prompt key. Names are aa_agent / pp_agent.
    return "agent_" + name.split("_", 1)[0]


async def _record_instruction(key: str, ctx) -> str:
    """La instrucción es una función, no una cadena: el alcance del productor
    cambia por sesión y ADK la llama al armar cada request. Ver el docstring
    de core/producer_scope.py, con la medición de por qué hace falta.

    Módulo, no una función anidada en build_app: el resto de build_app no
    define funciones internas (_prefix, _datastore, _planner ya viven acá
    arriba), así que una `def` nueva ahí adentro sería el único caso que
    rompe ese patrón. `functools.partial(_record_instruction, key)` en
    build_app fija `key` sin crear una función por llamada.
    """
    return prompts.record_instruction(key) + await producer_scope.for_context(ctx)


def _datastore(value: str) -> str:
    """Return a FULL Vertex AI Search datastore resource name, idempotently.

    VertexAiSearchTool rejects a bare id with "Invalid Vertex AI datastore
    resource name" (root-caused via Cloud Logging in the #43 npe live test; all
    datastores live in the `global` location).

    It rejects a DOUBLE-prefixed name with the exact same message, and both
    formats are in use: cicd/stacks/*/env.yaml holds bare ids (what CI ships to
    the engine) while agents/.env holds already-qualified names (what a local
    run sees). Wrapping unconditionally turned every local run into
    .../dataStores/projects/.../dataStores/<id> and broke all RAG.

    Accept either. GOOGLE_CLOUD_PROJECT is injected by Agent Engine at runtime.
    """
    if value.startswith("projects/"):
        return value
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    return (
        f"projects/{project}/locations/global/collections/"
        f"default_collection/dataStores/{value}"
    )


def build_app(name: str, display_name: str, main_datastore_env: str) -> AdkApp:
    key = _prefix(name)

    rag = LlmAgent(
        name=f"{name}_rag",
        model=GlobalGemini(model=RAG_MODEL),
        instruction=prompts.rag_instruction(key),
        description=prompts.rag_description(key),
        tools=[
            VertexAiSearchTool(data_store_id=_datastore(os.environ[main_datastore_env])),
            VertexAiSearchTool(data_store_id=_datastore(os.environ["DATASTORE_GUIDES_ID"])),
            VertexAiSearchTool(data_store_id=_datastore(os.environ["DATASTORE_FAQ_ID"])),
            VertexAiSearchTool(data_store_id=_datastore(os.environ["DATASTORE_CHILEPRUNES_CL_ID"])),
        ],
    )

    # No planner on the RAG agent: it is a single-step retrieve-and-answer task,
    # so thinking budget buys nothing. The catalog agent's 4-tool workflow IS a plan,
    # and the root's job is routing — both can benefit.
    catalog = LlmAgent(
        name=f"{name}_catalog",
        model=GlobalGemini(model=CATALOG_MODEL),
        instruction=prompts.catalog_instruction(key),
        description=prompts.catalog_description(key),
        planner=_planner(),
        tools=list(catalog_tools.TOOLS),
    )

    record = LlmAgent(
        name=f"{name}_record",
        model=GlobalGemini(model=RECORD_MODEL),
        instruction=functools.partial(_record_instruction, key),
        description=prompts.record_description(key),
        planner=_planner(),
        tools=list(record_tools.TOOLS),
    )

    root = LlmAgent(
        name=name,
        model=GlobalGemini(model=ROOT_MODEL),
        instruction=prompts.root_instruction(key),
        planner=_planner(),
        # La baja de WhatsApp se registra antes de que el modelo pueda
        # contestar sin registrarla — ver core/consent_guard.py.
        before_model_callback=consent_guard.before_model,
        tools=[
            agent_tool.AgentTool(agent=rag),
            agent_tool.AgentTool(agent=catalog),
            agent_tool.AgentTool(agent=record),
        ],
    )
    # The plugin only sees our tool failures because OkContractRetryPlugin
    # teaches it the {ok, error} contract — see core/retry_plugin.py.
    #
    # throw_exception_if_retry_exceeded=False is REQUIRED, not cosmetic: it
    # defaults to True, so once max_retries consecutive failures are reached the
    # plugin RAISES out of the tool path. core/catalog_tools.py is built on "never
    # raise into the model"; letting the last attempt raise inverts that
    # contract exactly when the model is already struggling, turning a
    # recoverable "I couldn't find that" into an engine-level exception.
    return AdkApp(
        agent=root,
        plugins=[
            OkContractRetryPlugin(
                max_retries=_tool_max_retries(),
                throw_exception_if_retry_exceeded=False,
            )
        ],
    )
