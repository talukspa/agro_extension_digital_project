"""Tests for the lazy BigQuery text2sql tooling.

``_get_db`` must memoize the SQLDatabase handle so the live BigQuery
connection happens at most once per process, and ``get_text2sql_tools``
must return the toolkit's tools.
"""
from unittest.mock import MagicMock, patch

import agent_aa_app.tools as tools


def test_get_db_memoizes_single_connection(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proj-x")
    monkeypatch.setenv("BIGQUERY_DATASET", "ds-y")
    tools._db = None  # reset the module-level cache
    fake_db = MagicMock(name="SQLDatabase")
    with patch.object(tools.SQLDatabase, "from_uri", return_value=fake_db) as from_uri:
        first = tools._get_db()
        second = tools._get_db()

    assert first is second is fake_db
    from_uri.assert_called_once_with("bigquery://proj-x/ds-y")


def test_get_text2sql_tools_returns_toolkit_tools(monkeypatch):
    tools._db = MagicMock(name="db-already-cached")  # skip real connection
    sentinel_tools = [MagicMock(name="tool1"), MagicMock(name="tool2")]
    toolkit = MagicMock()
    toolkit.get_tools.return_value = sentinel_tools

    with patch.object(tools, "ChatVertexAI") as ChatVertexAI, patch.object(
        tools, "SQLDatabaseToolkit", return_value=toolkit
    ) as Toolkit:
        result = tools.get_text2sql_tools()

    assert result == sentinel_tools
    ChatVertexAI.assert_called_once()
    # Toolkit is wired with the cached db + the vertex LLM.
    _, kwargs = Toolkit.call_args
    assert kwargs["db"] is tools._db


def test_pp_tools_import_and_memoize(monkeypatch):
    import agent_pp_app.tools as pp_tools

    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proj-pp")
    monkeypatch.setenv("BIGQUERY_DATASET", "ds-pp")
    pp_tools._db = None
    with patch.object(pp_tools.SQLDatabase, "from_uri", return_value=MagicMock()) as f:
        pp_tools._get_db()
        pp_tools._get_db()
    f.assert_called_once_with("bigquery://proj-pp/ds-pp")
