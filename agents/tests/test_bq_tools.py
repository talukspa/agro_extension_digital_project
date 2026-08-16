"""Unit tests for core.bq_tools. The BigQuery client is mocked — no GCP creds."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _clear_caches():
    from core import bq_tools
    # Only the INNER success-caches are memoized — the public tools are plain
    # functions so a transient failure is never cached (B5).
    bq_tools._list_tables_cached.cache_clear()
    bq_tools._get_schema_cached.cache_clear()
    yield


def _fake_client():
    """A MagicMock standing in for bigquery.Client."""
    return MagicMock()


def test_list_tables_returns_table_ids():
    from core import bq_tools
    client = _fake_client()
    t1, t2 = MagicMock(), MagicMock()
    t1.table_id, t2.table_id = "estandar_aa", "otra_tabla"
    client.list_tables.return_value = [t1, t2]
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.list_tables()
    assert out == {"ok": True, "error": None, "tables": ["estandar_aa", "otra_tabla"]}


def test_list_tables_empty_dataset():
    from core import bq_tools
    client = _fake_client()
    client.list_tables.return_value = []
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.list_tables()
    assert out == {"ok": True, "error": None, "tables": []}


def test_get_schema_formats_fields():
    from core import bq_tools
    client = _fake_client()
    f1, f2 = MagicMock(), MagicMock()
    f1.name, f1.field_type, f1.description = "codigo", "STRING", "código de acción"
    f2.name, f2.field_type, f2.description = "puntos", "INTEGER", ""
    client.get_table.return_value = MagicMock(schema=[f1, f2])
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.get_schema("estandar_aa")
    assert out["ok"] is True
    assert "codigo STRING — código de acción" in out["schema"]
    assert "puntos INTEGER" in out["schema"]


def test_check_query_refuses_non_select():
    from core import bq_tools
    out = bq_tools.check_query("DELETE FROM estandar_aa")
    assert out["ok"] is False
    assert "SELECT" in out["error"]


def test_check_query_dry_run_reports_bytes():
    from core import bq_tools
    client = _fake_client()
    client.query.return_value = MagicMock(total_bytes_processed=12345)
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.check_query("SELECT 1")
    assert out == {"ok": True, "error": None, "bytes_processed": 12345}


def test_run_query_refuses_non_select():
    from core import bq_tools
    out = bq_tools.run_query("UPDATE estandar_aa SET x = 1")
    assert out["ok"] is False
    assert "SELECT" in out["error"]


def test_run_query_refuses_over_byte_cap(monkeypatch):
    from core import bq_tools
    monkeypatch.setenv("BQ_MAX_BYTES", "1000")
    client = _fake_client()
    # dry-run estimate exceeds the cap
    client.query.return_value = MagicMock(total_bytes_processed=5000)
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.run_query("SELECT * FROM estandar_aa")
    assert out["ok"] is False
    assert "exceeds" in out["error"].lower()


def test_run_query_truncates_rows():
    from core import bq_tools
    client = _fake_client()
    dry = MagicMock(total_bytes_processed=10)          # under default cap
    rows = [{"codigo": f"A{i:03d}"} for i in range(250)]
    live = MagicMock()
    live.result.return_value = [MagicMock(items=lambda r=r: r.items()) for r in rows]
    # query() is called twice: once dry-run, once for real
    client.query.side_effect = [dry, live]
    with patch.object(bq_tools, "_client", return_value=client):
        out = bq_tools.run_query("SELECT codigo FROM estandar_aa", max_rows=100)
    assert out["ok"] is True
    assert len(out["rows"]) == 100
    assert out["truncated"] is True


# --- F3: single-statement enforcement --------------------------------------

@pytest.mark.parametrize("sql", [
    "SELECT 1; DROP TABLE estandar_aa",
    "SELECT 1;DELETE FROM estandar_aa",
    "WITH t AS (SELECT 1) SELECT * FROM t; TRUNCATE TABLE x",
])
def test_multi_statement_scripts_are_refused(sql):
    """BigQuery executes scripts — a first-token guard would run the DDL."""
    from core import bq_tools
    for fn in (bq_tools.check_query, bq_tools.run_query):
        out = fn(sql)
        assert out["ok"] is False
        assert "SELECT" in out["error"]


@pytest.mark.parametrize("sql", [
    "SELECT 1",
    "SELECT 1;",
    "  select codigo from estandar_aa  ",
    "(SELECT 1)",
    "WITH t AS (SELECT 1) SELECT * FROM t",
])
def test_single_statement_selects_still_pass(sql):
    from core import bq_tools
    assert bq_tools._is_select(sql) is True
