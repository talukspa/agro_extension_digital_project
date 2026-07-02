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
    wsp_token: str
    # HTTP client timeout (seconds) — WhatsApp API only; agent traffic now
    # goes through google-cloud-aiplatform which manages its own timeouts.
    whatsapp_http_timeout: float = 30.0

    # WhatsApp API configuration
    whatsapp_base_url: str

    # App-specific nested configurations
    aa_facebook_app_url: str
    aa_app_name: str
    # Meta App Secret for the AA app, used to validate the X-Hub-Signature-256
    # header on AA webhook POSTs. Sourced from WHATSAPP_APP_SECRET_AA. AA and PP
    # are separate Meta apps with distinct App Secrets, so each endpoint must
    # verify against its own. When unset the webhook fails closed (rejects every
    # POST for that app) — see api/webhooks.py.
    aa_app_secret: Optional[str] = None

    pp_facebook_app_url: str
    pp_app_name: str
    # Meta App Secret for the PP app. Sourced from WHATSAPP_APP_SECRET_PP.
    pp_app_secret: Optional[str] = None

    # Local-dev / runtime server settings (used by main.py __main__ block).
    host: str = "0.0.0.0"
    port: int = 8080
    environment: str = "production"

    @property
    def is_development(self) -> bool:
        """True when running in a local/dev environment."""
        return self.environment.lower() in ("development", "dev", "local")

    def app_secret_for(self, app_name: str) -> Optional[str]:
        """Return the Meta App Secret for the given app, or None if unknown.

        AA and PP are separate Meta apps; each signs its webhooks with its own
        App Secret, so signature validation must resolve per app_name.
        """
        if app_name == self.aa_app_name:
            return self.aa_app_secret
        if app_name == self.pp_app_name:
            return self.pp_app_secret
        return None

def load_config_from_env() -> AppConfig:
    """Loads the application configuration from environment variables."""
    return AppConfig(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        verify_token=os.getenv("VERIFY_TOKEN"),
        wsp_token=os.getenv("WSP_TOKEN"),
        whatsapp_http_timeout=float(os.getenv("WHATSAPP_HTTP_TIMEOUT", "30")),
        whatsapp_base_url=os.getenv("WHATSAPP_BASE_URL", "https://graph.facebook.com/v22.0"),
        aa_facebook_app_url=os.getenv("ESTANDAR_AA_FACEBOOK_APP"),
        aa_app_name=os.getenv("ESTANDAR_AA_APP_NAME"),
        aa_app_secret=os.getenv("WHATSAPP_APP_SECRET_AA"),
        pp_facebook_app_url=os.getenv("ESTANDAR_PP_FACEBOOK_APP"),
        pp_app_name=os.getenv("ESTANDAR_PP_APP_NAME"),
        pp_app_secret=os.getenv("WHATSAPP_APP_SECRET_PP"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        environment=os.getenv("ENVIRONMENT", "production"),
    )

# Singleton instance to be used across the application
config = load_config_from_env()
