"""
Simplified and centralized configuration management for the WhatsApp webhook application.
"""

import os
from typing import Optional
from pydantic import BaseModel

class AppConfig(BaseModel):
    """Main application configuration, loaded directly from environment variables."""
    log_level: str
    verify_token: str
    # HTTP client timeout (seconds) — WhatsApp API only; agent traffic now
    # goes through google-cloud-aiplatform which manages its own timeouts.
    whatsapp_http_timeout: float = 30.0

    # WhatsApp API configuration
    whatsapp_base_url: str

    # Meta App Secret used to validate the X-Hub-Signature-256 header on webhook
    # POSTs. Sourced from WHATSAPP_APP_SECRET. The AA and PP numbers live under
    # the SAME Meta app, so both endpoints verify against this one secret; the
    # earlier per-app split (WHATSAPP_APP_SECRET_AA/_PP) 403'd every AA message
    # in prd because Meta only ever signs with the one app's secret. When unset
    # the webhook fails closed (rejects every POST) — see api/webhooks.py.
    app_secret: Optional[str] = None

    # App-specific nested configurations
    aa_facebook_app_url: str
    aa_app_name: str
    # WhatsApp Cloud API access token (Bearer) for OUTBOUND sends as the AA app.
    # Sourced from WSP_TOKEN_AA. AA and PP are separate Meta apps / WABAs with
    # distinct numbers and distinct access tokens, so outbound must use the
    # token of the app the message belongs to — a token for one app returns 401
    # against the other's number. When unset, that app's outbound send is
    # skipped (see messages.py). Distinct from app_secret (inbound HMAC key).
    aa_wsp_token: Optional[str] = None

    pp_facebook_app_url: str
    pp_app_name: str
    # WhatsApp Cloud API access token for OUTBOUND sends as the PP app.
    # Sourced from WSP_TOKEN_PP.
    pp_wsp_token: Optional[str] = None

    # Local-dev / runtime server settings (used by main.py __main__ block).
    host: str = "0.0.0.0"
    port: int = 8080
    environment: str = "production"

    @property
    def is_development(self) -> bool:
        """True when running in a local/dev environment."""
        return self.environment.lower() in ("development", "dev", "local")

    def token_for(self, app_name: str) -> Optional[str]:
        """Return the outbound WhatsApp access token for the given app.

        AA and PP are separate Meta apps / WABAs with distinct access tokens;
        the token of one app is rejected (401) by the other's number, so
        outbound sends must resolve per app_name. None if unknown/unset.
        """
        if app_name == self.aa_app_name:
            return self.aa_wsp_token
        if app_name == self.pp_app_name:
            return self.pp_wsp_token
        return None

def load_config_from_env() -> AppConfig:
    """Loads the application configuration from environment variables."""
    return AppConfig(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        verify_token=os.getenv("VERIFY_TOKEN"),
        whatsapp_http_timeout=float(os.getenv("WHATSAPP_HTTP_TIMEOUT", "30")),
        whatsapp_base_url=os.getenv("WHATSAPP_BASE_URL", "https://graph.facebook.com/v22.0"),
        app_secret=os.getenv("WHATSAPP_APP_SECRET"),
        aa_facebook_app_url=os.getenv("ESTANDAR_AA_FACEBOOK_APP"),
        aa_app_name=os.getenv("ESTANDAR_AA_APP_NAME"),
        aa_wsp_token=os.getenv("WSP_TOKEN_AA"),
        pp_facebook_app_url=os.getenv("ESTANDAR_PP_FACEBOOK_APP"),
        pp_app_name=os.getenv("ESTANDAR_PP_APP_NAME"),
        pp_wsp_token=os.getenv("WSP_TOKEN_PP"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        environment=os.getenv("ENVIRONMENT", "production"),
    )

# Singleton instance to be used across the application
config = load_config_from_env()
