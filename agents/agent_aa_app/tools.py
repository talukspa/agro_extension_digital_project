import os
from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

llm = ChatVertexAI(model_name="gemini-3.5-flash")

BIGQUERY_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")

db = SQLDatabase.from_uri(f"bigquery://{BIGQUERY_PROJECT}/{BIGQUERY_DATASET}")

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

text2sql_tools = toolkit.get_tools()
