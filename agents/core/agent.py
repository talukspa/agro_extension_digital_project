"""Single factory for both agents. build_app(...) returns a deploy-ready AdkApp.

The agent `name` prefix (e.g. "aa_agent") derives the sub-agent names so traces
stay readable. The main datastore env var name differs per agent; guides/faq/
chileprunes datastores are shared across both.
"""
import os

from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool, agent_tool
from vertexai.agent_engines import AdkApp

from core import bq_tools, prompts
from core.llm_global import GlobalGemini
from core.retry_plugin import OkContractRetryPlugin

# Consecutive tool failures before the plugin stops feeding back reflection
# guidance. Env-overridable per engine, same pattern as BQ_MAX_BYTES.
TOOL_MAX_RETRIES = int(os.environ.get("TOOL_MAX_RETRIES", "3"))


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

    bq = LlmAgent(
        name=f"{name}_bq",
        model=GlobalGemini(model="gemini-3.5-flash"),
        instruction=prompts.bq_instruction(key),
        description=prompts.bq_description(key),
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
        tools=[
            agent_tool.AgentTool(agent=rag),
            agent_tool.AgentTool(agent=bq),
        ],
    )
    # The plugin only sees our BigQuery failures because OkContractRetryPlugin
    # teaches it the {ok, error} contract — see core/retry_plugin.py.
    return AdkApp(
        agent=root,
        plugins=[OkContractRetryPlugin(max_retries=TOOL_MAX_RETRIES)],
    )
