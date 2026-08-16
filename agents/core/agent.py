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


def _prefix(name: str) -> str:
    # "aa_agent" -> "agent_aa" prompt key. Names are aa_agent / pp_agent.
    return "agent_" + name.split("_", 1)[0]


def _datastore(short_id: str) -> str:
    # VertexAiSearchTool needs the FULL datastore resource name, NOT the bare id.
    # Passing the bare id makes every RAG query fail server-side with
    # "Invalid Vertex AI datastore resource name" (root-caused via Cloud Logging
    # in the #43 npe live test; all datastores live in the `global` location).
    # GOOGLE_CLOUD_PROJECT is injected by Agent Engine at runtime.
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    return (
        f"projects/{project}/locations/global/collections/"
        f"default_collection/dataStores/{short_id}"
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
    return AdkApp(agent=root)
