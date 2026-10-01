"""Seed placeholder env vars before any agent module is imported.

The old SQLDatabase.from_uri stub is gone — the catalog tools in
core/catalog_tools.py connect lazily (per call), so importing the agent modules
never opens a connection.

The google.auth.default stub STAYS: build_app still constructs
VertexAiSearchTool and AdkApp, which run Vertex/aiplatform initialization and
call google.auth.default(). That fails offline and on GitHub-hosted runners
with no ADC (see commit 9df46f7).
"""
import os

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("DATASTORE_AA_ID", "test-datastore-aa")
os.environ.setdefault("DATASTORE_PP_ID", "test-datastore-pp")
os.environ.setdefault("DATASTORE_GUIDES_ID", "test-datastore-guides")
os.environ.setdefault("DATASTORE_FAQ_ID", "test-datastore-faq")
os.environ.setdefault("DATASTORE_CHILEPRUNES_CL_ID", "test-datastore-chileprunes")
# El expediente: sus tools leen estas dos por llamada. Van acá por la misma
# razón que las de arriba — son obligatorias en RUNTIME_ENV_KEYS, así que sin
# ellas los tests de deploy_one revientan con un KeyError que no dice nada sobre
# lo que el test estaba probando. Valores de mentira: ninguna prueba sale a red.
os.environ.setdefault("CIRUELA_API_BASE", "http://app-de-prueba.invalid")
os.environ.setdefault("AGENT_SERVICE_TOKEN", "token-de-prueba")
# El catálogo. Un DSN que no resuelve: ninguna prueba sale a la red, y las que sí
# quieren la base real lo sobrescriben con monkeypatch.
os.environ.setdefault("CATALOG_DSN", "postgresql://falso@catalogo-de-prueba.invalid/d")

import google.auth  # noqa: E402
from google.auth.credentials import AnonymousCredentials  # noqa: E402

google.auth.default = lambda *args, **kwargs: (
    AnonymousCredentials(),
    os.environ["GOOGLE_CLOUD_PROJECT"],
)
