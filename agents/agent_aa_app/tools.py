import os

from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from agent_aa_app.llm_global import GEMINI_LOCATION

# Cached SQLDatabase handle. Built lazily by _get_db() rather than at import
# time: SQLDatabase.from_uri() opens a live BigQuery connection, which we must
# not do while the module is merely imported (e.g. during the engine-create
# deepcopy or at test collection).
_db = None


def _get_db() -> SQLDatabase:
    global _db
    if _db is None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        dataset = os.getenv("BIGQUERY_DATASET")
        _db = SQLDatabase.from_uri(f"bigquery://{project}/{dataset}")
    return _db


def get_text2sql_tools():
    """Build the BigQuery SQL toolkit tools lazily.

    Deferred out of import so the live BigQuery connection only happens when
    the LangGraph BQ agent is actually constructed (server-side, on first
    invocation), not at import/deepcopy time.
    """
    llm = ChatVertexAI(model_name="gemini-3.5-flash", location=GEMINI_LOCATION)
    toolkit = SQLDatabaseToolkit(db=_get_db(), llm=llm)
    return toolkit.get_tools()
