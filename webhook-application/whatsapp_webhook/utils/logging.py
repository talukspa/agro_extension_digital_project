"""
Logging utilities for the WhatsApp webhook application.
"""
import logging
import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


def configure_app_logging() -> logging.Logger:
    """
    Configure application-wide logging level based on environment variable.
    
    Returns:
        Logger instance configured for the application
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        log_level = "INFO"
        print(f"Warning: Invalid LOG_LEVEL provided. Using default: INFO")
    
    # Convert string to logging level
    numeric_level = getattr(logging, log_level)
    
    # Configure basic logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override any existing configuration
    )
    
    # Get application logger
    app_logger = logging.getLogger("whatsapp_webhook")
    app_logger.info(f"Logging configured with level: {log_level}")
    
    return app_logger


def mask_pii(value: Optional[str]) -> str:
    """Mask a phone number / wa_id for safe logging.

    Keeps the first 2 and last 2 chars, masks the middle. Short values are
    fully masked. Mirrors StructuredLogger._sanitize_user_id.
    """
    if not value:
        return "****"
    if len(value) <= 4:
        return "****"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


class LogContext(Enum):
    """Contextos de logging para diferentes módulos."""
    WEBHOOK = "webhook"
    MESSAGE_PARSING = "message_parsing"
    MESSAGE_PROCESSING = "message_processing"
    AGENT_COMMUNICATION = "agent_communication"
    WHATSAPP_API = "whatsapp_api"
    AUTHENTICATION = "authentication"
    GENERAL = "general"


class StructuredLogger:
    """Logger estructurado simple y pythónico."""
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        self.name = name
        self.context = context or {}
        self.logger = logging.getLogger(f"whatsapp_webhook.{name}")
        self.is_debug = os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"
        
        # Configurar handler si no existe
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
    
    def _format_extra(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea información extra para logging."""
        formatted = {**self.context, **extra}
        
        # Sanitizar información sensible
        if 'user_id' in formatted:
            formatted['user_id'] = self._sanitize_user_id(formatted['user_id'])
        
        return formatted
    
    def _sanitize_user_id(self, user_id: str) -> str:
        """Sanitiza user ID para logging seguro."""
        if len(user_id) <= 4:
            return "****"
        return user_id[:2] + "*" * (len(user_id) - 4) + user_id[-2:]
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log de información."""
        if extra:
            self.logger.info(message, extra=self._format_extra(extra))
        else:
            self.logger.info(message)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log de debug (solo en modo DEBUG)."""
        if self.is_debug:
            if extra:
                self.logger.debug(message, extra=self._format_extra(extra))
            else:
                self.logger.debug(message)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log de advertencia."""
        if extra:
            self.logger.warning(message, extra=self._format_extra(extra))
        else:
            self.logger.warning(message)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log de error."""
        if extra:
            self.logger.error(message, extra=self._format_extra(extra), exc_info=exc_info)
        else:
            self.logger.error(message, exc_info=exc_info)
    
    def log_message_received(self, message_type: str, user_id: str, app_name: str, message_data: Optional[Dict] = None):
        """Log de mensaje recibido - datos sensibles solo en DEBUG."""
        self.info(
            f"Message received",
            extra={
                "message_type": message_type,
                "user_id": user_id,
                "app_name": app_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Datos completos del mensaje solo en DEBUG
        if self.is_debug and message_data:
            self.debug(
                f"Full message data",
                extra={"message_data": message_data}
            )
    
    def log_agent_request(self, user_id: str, app_name: str, payload: Optional[Dict] = None):
        """Log de request al agente - payload solo en DEBUG."""
        self.info(
            f"Sending request to agent",
            extra={
                "user_id": user_id,
                "app_name": app_name
            }
        )
        
        if self.is_debug and payload:
            # Sanitizar payload para remover información sensible
            sanitized_payload = self._sanitize_payload(payload)
            self.debug(
                f"Agent request payload",
                extra={"payload": sanitized_payload}
            )
    
    def log_whatsapp_response(self, user_id: str, app_name: str, status_code: int, response_data: Optional[Dict] = None):
        """Log de respuesta de WhatsApp API."""
        self.info(
            f"WhatsApp API response",
            extra={
                "user_id": user_id,
                "app_name": app_name,
                "status_code": status_code
            }
        )
        
        if self.is_debug and response_data:
            self.debug(
                f"WhatsApp response data",
                extra={"response_data": response_data}
            )
    
    def log_webhook_verification(self, app_name: str, mode: str, success: bool, extra_data: Optional[Dict] = None):
        """Log de verificación de webhook."""
        level = "info" if success else "warning"
        message = f"{app_name} webhook verification {'successful' if success else 'failed'}"
        
        log_data = {
            "app_name": app_name,
            "mode": mode,
            "success": success
        }
        if extra_data:
            log_data.update(extra_data)
        
        if level == "info":
            self.info(message, extra=log_data)
        else:
            self.warning(message, extra=log_data)
    
    def log_webhook_processing(self, app_name: str, stage: str, extra_data: Optional[Dict] = None):
        """Log de procesamiento de webhook."""
        message = f"{app_name} webhook processing: {stage}"
        
        log_data = {
            "app_name": app_name,
            "stage": stage
        }
        if extra_data:
            log_data.update(extra_data)
        
        self.info(message, extra=log_data)

    def log_agent_session_creation(self, user_id: str, app_name: str, agent_app_name: str, session_url: str):
        """Log de creación de sesión con el agente."""
        self.info(
            f"Creating agent session",
            extra={
                "user_id": user_id,
                "app_name": app_name,
                "agent_app_name": agent_app_name,
                "session_url": session_url
            }
        )

    def log_agent_message_request(self, user_id: str, app_name: str, agent_app_name: str, request_url: str):
        """Log de solicitud de mensaje al agente."""
        self.info(
            f"Sending message to agent",
            extra={
                "user_id": user_id,
                "app_name": app_name,
                "agent_app_name": agent_app_name,
                "request_url": request_url
            }
        )
    
    def _sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza payload removiendo información sensible."""
        sanitized = payload.copy()
        
        # Remover o enmascarar campos sensibles
        sensitive_fields = ['token', 'password', 'secret', 'authorization']
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "***HIDDEN***"
        
        return sanitized


# Factory function para crear loggers
def get_logger(context: str, extra_context: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """
    Factory function para crear logger estructurado.
    
    Args:
        context: Contexto del logger (webhook, message_processing, etc.)
        extra_context: Contexto adicional a incluir en todos los logs
        
    Returns:
        StructuredLogger: Instancia configurada del logger
    """
    return StructuredLogger(context, extra_context)


def setup_logging():
    """Configura el sistema de logging global."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Configurar niveles específicos para librerías externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
