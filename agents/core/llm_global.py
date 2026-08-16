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


class GlobalGemini(Gemini):
    @property
    def api_client(self) -> genai.Client:
        # NOTE: plain @property (not @cached_property): the AdkApp gets
        # deepcopy'd at engine-create time, and a cached genai.Client holds
        # a module reference that fails to pickle. ADK's own Gemini caches
        # the client; we trade a per-call client init for picklability.
        return genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=GEMINI_LOCATION,
        )
