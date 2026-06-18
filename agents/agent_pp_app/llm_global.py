"""Gemini variant that routes model calls to location="global".

See agent_aa_app/llm_global.py for the rationale.
"""
import os
from functools import cached_property

from google import genai
from google.adk.models import Gemini

GEMINI_LOCATION = "global"


class GlobalGemini(Gemini):
    @cached_property
    def api_client(self) -> genai.Client:
        return genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=GEMINI_LOCATION,
        )
