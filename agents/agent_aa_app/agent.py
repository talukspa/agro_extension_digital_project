from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools import VertexAiSearchTool

from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import InMemorySaver

import os
from agent_aa_app.tools import text2sql_tools
from agent_aa_app.utils.langgraph_agent import LangGraphAgent
from agent_aa_app.llm_global import GlobalGemini, GEMINI_LOCATION
from agent_aa_app.prompts import (
    agent_aa_instruction,
    agent_aa_bq_instruction,
    agent_aa_bq_description,
    agent_aa_rag_instruction,
    agent_aa_rag_description,
    text2sql_instruction,
)

vertex_search_tool_aa = VertexAiSearchTool(data_store_id=os.getenv("DATASTORE_AA_ID"))
vertex_search_tool_guides = VertexAiSearchTool(
    data_store_id=os.getenv("DATASTORE_GUIDES_ID")
)
vertex_search_tool_faq = VertexAiSearchTool(data_store_id=os.getenv("DATASTORE_FAQ_ID"))
vertex_search_tool_chileprunes_cl = VertexAiSearchTool(
    data_store_id=os.getenv("DATASTORE_CHILEPRUNES_CL_ID")
)

aa_agent_rag = LlmAgent(
    name="aa_agent_rag",
    model=GlobalGemini(model="gemini-3.1-flash-lite"),
    instruction=agent_aa_rag_instruction(),
    description=agent_aa_rag_description(),
    tools=[
        vertex_search_tool_aa,
        vertex_search_tool_guides,
        vertex_search_tool_faq,
        vertex_search_tool_chileprunes_cl,
    ],
)

llm = ChatVertexAI(model_name="gemini-3.5-flash", location=GEMINI_LOCATION)


def _build_bq_graph():
    """Build the LangGraph BigQuery react agent lazily.

    Holds non-picklable state (CompiledStateGraph + SQLDatabase Engine), so
    must be deferred past the deepcopy that vertexai.agent_engines.create()
    runs on the AdkApp. Runs once, server-side, on first invocation.
    """
    return create_react_agent(
        model=ChatVertexAI(model_name="gemini-3.5-flash", location=GEMINI_LOCATION),
        tools=text2sql_tools,
        prompt=text2sql_instruction().format(dialect="bigquery", top_k=16),
        checkpointer=InMemorySaver(),
    )


aa_agent_bq = LangGraphAgent(
    name="aa_agent_bq",
    graph_factory=_build_bq_graph,
    instruction=agent_aa_bq_instruction(),
    description=agent_aa_bq_description(),
)

root_agent = LlmAgent(
    name="aa_agent",
    model=GlobalGemini(model="gemini-3.5-flash"),
    instruction=agent_aa_instruction(),
    tools=[
        agent_tool.AgentTool(agent=aa_agent_rag),
        agent_tool.AgentTool(agent=aa_agent_bq),
    ],
)
