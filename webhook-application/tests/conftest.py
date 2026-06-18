"""Seed required env vars before any whatsapp_webhook module is imported.

`whatsapp_webhook.utils.app_config` loads + validates config at module
import time (Pydantic v2 raises on None). Cloud Run sets these from
Terraform; tests don't, so we seed placeholders here. Tests that need
real values monkeypatch them per-test.
"""
import os

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("VERIFY_TOKEN", "test-verify-token")
os.environ.setdefault("WSP_TOKEN", "test-wsp-token")
os.environ.setdefault("WHATSAPP_BASE_URL", "https://graph.facebook.com/v22.0")
os.environ.setdefault("ESTANDAR_AA_FACEBOOK_APP", "test-aa-fb-app")
os.environ.setdefault("ESTANDAR_AA_APP_NAME", "agent_aa")
os.environ.setdefault("ESTANDAR_PP_FACEBOOK_APP", "test-pp-fb-app")
os.environ.setdefault("ESTANDAR_PP_APP_NAME", "agent_pp")
