from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools import VertexAiSearchTool

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import InMemorySaver

import os
from agent_pp_app.tools import get_text2sql_tools
from agent_pp_app.utils.langgraph_agent import LangGraphAgent
from agent_pp_app.llm_global import GlobalGemini, GEMINI_LOCATION
from agent_pp_app.prompts import (
    agent_pp_instruction,
    agent_pp_bq_instruction,
    agent_pp_bq_description,
    agent_pp_rag_instruction,
    agent_pp_rag_description,
    text2sql_instruction,
)

def _datastore(short_id: str) -> str:
    """Build the full Vertex AI Search datastore resource name.

    ADK's VertexAiSearchTool requires the full resource name, not the bare id;
    passing just the id makes the engine's GenerateContent call fail with
    "Invalid Vertex AI datastore resource name". The datastores live in the
    `global` location under the default collection; GOOGLE_CLOUD_PROJECT is
    injected by Agent Engine at runtime.
    """
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    return (
        f"projects/{project}/locations/global/collections/"
        f"default_collection/dataStores/{short_id}"
    )


vertex_search_tool_pp = VertexAiSearchTool(
    data_store_id=_datastore(os.environ["DATASTORE_PP_ID"])
)
vertex_search_tool_guides = VertexAiSearchTool(
    data_store_id=_datastore(os.environ["DATASTORE_GUIDES_ID"])
)
vertex_search_tool_faq = VertexAiSearchTool(
    data_store_id=_datastore(os.environ["DATASTORE_FAQ_ID"])
)
vertex_search_tool_chileprunes_cl = VertexAiSearchTool(
    data_store_id=_datastore(os.environ["DATASTORE_CHILEPRUNES_CL_ID"])
)

pp_agent_rag = LlmAgent(
    name="pp_agent_rag",
    model=GlobalGemini(model="gemini-3.1-flash-lite"),
    instruction=agent_pp_rag_instruction(),
    description=agent_pp_rag_description(),
    tools=[
        vertex_search_tool_pp,
        vertex_search_tool_guides,
        vertex_search_tool_faq,
        vertex_search_tool_chileprunes_cl,
    ],
)

def _build_bq_graph():
    """Lazy LangGraph constructor — see agent_aa_app/agent.py for rationale."""
    return create_react_agent(
        model=ChatVertexAI(model_name="gemini-3.5-flash", location=GEMINI_LOCATION),
        tools=get_text2sql_tools(),
        prompt=text2sql_instruction().format(dialect="bigquery", top_k=16),
        checkpointer=InMemorySaver(),
    )


pp_agent_bq = LangGraphAgent(
    name="pp_agent_bq",
    graph_factory=_build_bq_graph,
    instruction=agent_pp_bq_instruction(),
    description=agent_pp_bq_description(),
)

root_agent = LlmAgent(
    name="pp_agent",
    model=GlobalGemini(model="gemini-3.5-flash"),
    instruction=agent_pp_instruction(),
    tools=[
        agent_tool.AgentTool(agent=pp_agent_rag),
        agent_tool.AgentTool(agent=pp_agent_bq),
    ],
)
