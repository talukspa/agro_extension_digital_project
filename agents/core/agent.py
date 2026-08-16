"""Single factory for both agents. build_app(...) returns a deploy-ready AdkApp.

The agent `name` prefix (e.g. "aa_agent") derives the sub-agent names so traces
stay readable. The main datastore env var name differs per agent; guides/faq/
chileprunes datastores are shared across both.
"""
import os

from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool, agent_tool
from vertexai.agent_engines import AdkApp

from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig

from core import bq_tools, prompts
from core.llm_global import GlobalGemini
from core.retry_plugin import OkContractRetryPlugin

def _tool_max_retries() -> int:
    """Consecutive tool failures before the plugin stops reflecting.

    Read per call, never bound at import — same reason as the caps in
    core/bq_tools.py: an import-time binding is untestable via monkeypatch and
    silently ignores the per-engine override.
    """
    return int(os.environ.get("TOOL_MAX_RETRIES", "3"))


def _planner():
    """BuiltInPlanner for the root + BQ agents, or None.

    DEFAULT IS OFF. #44 estimated "+10-15% tokens", but thinking tokens bill at
    OUTPUT rate and a WhatsApp reply is only 100-500 tokens — a 2048-token
    budget can cost more than the answer. Ship dark, flip AGENT_PLANNER=builtin
    on ONE engine, and compare against real npe traffic before defaulting it on.

    PlanReActPlanner is deliberately not offered: it adds a full extra LLM
    round-trip per planning step, which WhatsApp latency cannot absorb.

    Env is read per call, never bound at import — see the B4 note in bq_tools.
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
        model=GlobalGemini(model="gemini-3.1-flash-lite"),
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
    # so thinking budget buys nothing. The BQ agent's 4-tool workflow IS a plan,
    # and the root's job is routing — both can benefit.
    bq = LlmAgent(
        name=f"{name}_bq",
        model=GlobalGemini(model="gemini-3.5-flash"),
        instruction=prompts.bq_instruction(key),
        description=prompts.bq_description(key),
        planner=_planner(),
        tools=[
            bq_tools.list_tables,
            bq_tools.get_schema,
            bq_tools.check_query,
            bq_tools.run_query,
        ],
    )

    root = LlmAgent(
        name=name,
        model=GlobalGemini(model="gemini-3.5-flash"),
        instruction=prompts.root_instruction(key),
        planner=_planner(),
        tools=[
            agent_tool.AgentTool(agent=rag),
            agent_tool.AgentTool(agent=bq),
        ],
    )
    # The plugin only sees our BigQuery failures because OkContractRetryPlugin
    # teaches it the {ok, error} contract — see core/retry_plugin.py.
    #
    # throw_exception_if_retry_exceeded=False is REQUIRED, not cosmetic: it
    # defaults to True, so once max_retries consecutive failures are reached the
    # plugin RAISES out of the tool path. core/bq_tools.py is built on "never
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
