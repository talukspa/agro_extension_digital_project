"""
FastAPI router for WhatsApp webhook endpoints.
"""

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.datastructures import QueryParams
import hashlib
import hmac
import json

from ..models.api_models import WebhookSuccessResponse
from ..utils.app_config import config
from ..utils.logging import get_logger
from ..messages import receive_message_aa, receive_message_pp

router = APIRouter(prefix="", tags=["webhooks"])
logger = get_logger("webhook_router")


async def _verify_webhook(app_name: str, params: QueryParams) -> PlainTextResponse:
    """Generic webhook verification handler (Meta GET subscription challenge)."""
    verify_token = config.verify_token

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    log_extra = {"token_provided": bool(token), "challenge_provided": bool(challenge)}

    if (
        mode == "subscribe"
        and token is not None
        # Compare on bytes: token is attacker-controlled and a non-ASCII value
        # would make str-operand compare_digest raise TypeError (500) instead
        # of failing verification cleanly.
        and hmac.compare_digest(token.encode("utf-8"), verify_token.encode("utf-8"))
    ):
        if not challenge or not challenge.isdigit():
            logger.log_webhook_verification(app_name, mode or "None", False, log_extra)
            logger.warning(f"{app_name} Webhook verification failed: Invalid challenge")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid challenge")

        logger.log_webhook_verification(app_name, mode, True, {"challenge": challenge})
        # Meta expects the raw challenge value echoed back verbatim as text.
        return PlainTextResponse(challenge)

    logger.log_webhook_verification(app_name, mode or "None", False, log_extra)
    logger.warning(f"{app_name} Webhook verification failed: Token or mode mismatch")
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Webhook verification failed")


def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Validate Meta's X-Hub-Signature-256 header against the raw request body.

    Fails closed: if no app secret is configured, every POST is rejected so a
    misconfiguration can never silently disable signature validation.
    """
    app_secret = config.app_secret
    if not app_secret:
        logger.error(
            "WHATSAPP_APP_SECRET is not configured; rejecting webhook POST "
            "(fail-closed signature validation)."
        )
        return False
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        app_secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    # Compare on bytes: hmac.compare_digest raises TypeError on str operands
    # containing non-ASCII, and signature_header is attacker-controlled. On
    # bytes it stays constant-time and simply returns False for a mismatch.
    return hmac.compare_digest(expected.encode("utf-8"), signature_header.encode("utf-8"))


async def _handle_webhook_post(app_name: str, handler_func, request: Request) -> JSONResponse:
    """Generic webhook POST handler.

    Validates the Meta signature over the raw body BEFORE scheduling any
    background work, then parses JSON from the same bytes.
    """
    logger.info(f"Processing webhook for {app_name}", extra={"endpoint": str(request.url)})

    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not _verify_signature(raw_body, signature):
        logger.warning(f"{app_name} Webhook signature validation failed")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid signature")

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received for {app_name}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON format")

    try:
        await handler_func(body)
        logger.info(f"Webhook for {app_name} processed successfully")
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook for {app_name}: {e}", exc_info=True)
        # Always return 200 OK to WhatsApp to prevent retries
        return JSONResponse({"status": "ok"})


# AA Webhook endpoints
@router.get("/estandar_aa_webhook")
async def verify_aa_webhook(request: Request):
    """Verify AA webhook subscription."""
    return await _verify_webhook(config.aa_app_name, request.query_params)


@router.post("/estandar_aa_webhook", response_model=WebhookSuccessResponse)
async def handle_estandar_aa_webhook(request: Request):
    """Handle incoming AA webhook messages."""
    return await _handle_webhook_post(config.aa_app_name, receive_message_aa, request)


# PP Webhook endpoints
@router.get("/estandar_pp_webhook")
async def verify_pp_webhook(request: Request):
    """Verify PP webhook subscription."""
    return await _verify_webhook(config.pp_app_name, request.query_params)


@router.post("/estandar_pp_webhook", response_model=WebhookSuccessResponse)
async def handle_estandar_pp_webhook(request: Request):
    """Handle incoming PP webhook messages."""
    return await _handle_webhook_post(config.pp_app_name, receive_message_pp, request)
