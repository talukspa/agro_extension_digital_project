"""Seed required env vars before any whatsapp_webhook module is imported.

`whatsapp_webhook.utils.app_config` loads + validates config at module
import time (Pydantic v2 raises on None). Cloud Run sets these from
Terraform; tests don't, so we seed placeholders here. Tests that need
real values monkeypatch them per-test.
"""
import os

# Keep Google client init hermetic offline (no ADC on CI runners): any code path
# resolving credentials gets anonymous creds + the placeholder project instead
# of raising DefaultCredentialsError.
import google.auth
from google.auth.credentials import AnonymousCredentials

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

google.auth.default = lambda *args, **kwargs: (
    AnonymousCredentials(),
    os.environ["GOOGLE_CLOUD_PROJECT"],
)
os.environ.setdefault("VERIFY_TOKEN", "test-verify-token")
# Per-app outbound access tokens (AA and PP are separate WABAs/tokens).
os.environ.setdefault("WSP_TOKEN_AA", "test-wsp-token-aa")
os.environ.setdefault("WSP_TOKEN_PP", "test-wsp-token-pp")
os.environ.setdefault("WHATSAPP_BASE_URL", "https://graph.facebook.com/v22.0")
os.environ.setdefault("ESTANDAR_AA_FACEBOOK_APP", "test-aa-fb-app")
os.environ.setdefault("ESTANDAR_AA_APP_NAME", "agent_aa")
os.environ.setdefault("ESTANDAR_PP_FACEBOOK_APP", "test-pp-fb-app")
os.environ.setdefault("ESTANDAR_PP_APP_NAME", "agent_pp")
