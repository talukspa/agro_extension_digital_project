"""Gemini variant that routes model calls to location="global".

Gemini 3.x preview models (gemini-3.5-flash, gemini-3.1-flash-lite, ...) are
served only from the Vertex AI `global` location as of 2026-06. The Agent
Runtime engine itself must stay regional (Agent Engine resources are not
available in `global`), but the LLM client inside the engine can target
`global` for model calls. BigQuery + Vertex AI Search clients keep using
the engine's regional location.

This follows ADK's documented override pattern (see google.adk.models.Gemini
docstring).
"""
import os

from google import genai
from google.adk.models import Gemini

GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")

# Module-level client cache, keyed by (project, location). Deliberately NOT
# stored on the Gemini instance: the AdkApp (and this model) get deepcopy'd
# at engine-create time, and a genai.Client holds an unpicklable gRPC channel
# / module reference. Keeping the cache off the instance preserves the
# picklability that the previous plain @property guaranteed, while still
# reusing one client (+channel) per (project, location) across all calls on
# the hot path. First population happens lazily server-side, after deepcopy.
_CLIENT_CACHE: dict[tuple[str, str], genai.Client] = {}


class GlobalGemini(Gemini):
    @property
    def api_client(self) -> genai.Client:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        key = (project, GEMINI_LOCATION)
        client = _CLIENT_CACHE.get(key)
        if client is None:
            client = genai.Client(
                vertexai=True,
                project=project,
                location=GEMINI_LOCATION,
            )
            _CLIENT_CACHE[key] = client
        return client
