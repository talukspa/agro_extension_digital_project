"""Test environment setup.

`agents/agent_*_app/tools.py` does `SQLDatabase.from_uri(...)` at module import
time, which makes a live BigQuery list-datasets call. In tests we don't have a
real project, so stub the URI factory and seed placeholder env vars before any
agent module gets imported by the test collector.
"""
import os
from unittest.mock import MagicMock

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("BIGQUERY_DATASET", "test_dataset")
os.environ.setdefault("DATASTORE_AA_ID", "test-datastore-aa")
os.environ.setdefault("DATASTORE_PP_ID", "test-datastore-pp")
os.environ.setdefault("DATASTORE_GUIDES_ID", "test-datastore-guides")
os.environ.setdefault("DATASTORE_FAQ_ID", "test-datastore-faq")
os.environ.setdefault("DATASTORE_CHILEPRUNES_CL_ID", "test-datastore-chileprunes")

from langchain_community.utilities import SQLDatabase  # noqa: E402

SQLDatabase.from_uri = classmethod(lambda cls, *args, **kwargs: MagicMock(spec=SQLDatabase))
