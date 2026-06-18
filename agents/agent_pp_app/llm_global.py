"""Gemini variant that routes model calls to location="global".

See agent_aa_app/llm_global.py for the rationale.
"""
import os

from google import genai
from google.adk.models import Gemini

GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", "global")


class GlobalGemini(Gemini):
    @property
    def api_client(self) -> genai.Client:
        # See agent_aa_app/llm_global.py for why this is @property not
        # @cached_property — engine-create deepcopies the AdkApp.
        return genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=GEMINI_LOCATION,
        )
