"""Gemini variant that routes model calls to location="global".

See agent_aa_app/llm_global.py for the rationale.
"""
import os

from google import genai
from google.adk.models import Gemini

GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")

# Module-level client cache keyed by (project, location); kept OFF the Gemini
# instance so the engine-create deepcopy/pickle path never touches the
# unpicklable genai.Client, while still reusing one client per key.
# See agent_aa_app/llm_global.py for the full rationale.
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
