"""Seed placeholder env vars before any agent module is imported.

The old SQLDatabase.from_uri stub is gone — the BigQuery tools in
core/bq_tools.py construct their client lazily (per call), so importing the
agent modules no longer makes a live BigQuery call.

The google.auth.default stub STAYS: build_app still constructs
VertexAiSearchTool and AdkApp, which run Vertex/aiplatform initialization and
call google.auth.default(). That fails offline and on GitHub-hosted runners
with no ADC (see commit 9df46f7).
"""
import os

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("BIGQUERY_DATASET", "test_dataset")
os.environ.setdefault("DATASTORE_AA_ID", "test-datastore-aa")
os.environ.setdefault("DATASTORE_PP_ID", "test-datastore-pp")
os.environ.setdefault("DATASTORE_GUIDES_ID", "test-datastore-guides")
os.environ.setdefault("DATASTORE_FAQ_ID", "test-datastore-faq")
os.environ.setdefault("DATASTORE_CHILEPRUNES_CL_ID", "test-datastore-chileprunes")

import google.auth  # noqa: E402
from google.auth.credentials import AnonymousCredentials  # noqa: E402

google.auth.default = lambda *args, **kwargs: (
    AnonymousCredentials(),
    os.environ["GOOGLE_CLOUD_PROJECT"],
)
