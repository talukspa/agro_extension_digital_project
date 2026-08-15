import asyncio
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .external_services.agent_client import create_agent_session, send_to_agent
from .external_services.whatsapp_client import (
    create_text_message,
    download_whatsapp_media,
    send_whatsapp_message,
)
from .models.messages import WhatsAppWebhookPayload
from .transcription import transcribe_audio_file
from .utils.app_config import config
from .utils.logging import get_logger, mask_pii
from .utils.model_utils import parse_webhook_payload

if TYPE_CHECKING:
    from .models.messages import WhatsAppMessage

# Retain references to background tasks so they aren't garbage-collected mid-run
# (asyncio only keeps weak references to running tasks).
_background_tasks: set[asyncio.Task] = set()


async def send_message_to_agent(user: str, app_name: str, session_id: str, message: str) -> str:
    """Sends a message to the internal agent service and parses the response."""
    logger = get_logger("agent_communication", {"app_name": app_name})

    try:
        response_data = await send_to_agent(app_name, user, session_id, message)
        return response_data.get(
            "response", "Error: No se pudo extraer el texto de la respuesta."
        )
    except ValueError as e:
        logger.error(f"Configuration error: {e}", exc_info=True)
        return "Error: Servicio de agente no configurado."
    except Exception as e:
        logger.error(f"Error communicating with agent: {e}", exc_info=True)
        return "Error: Fallo la comunicación con el servicio del agente."


async def _send_whatsapp_acknowledgment(
    user_wa_id: str, message_text: str, app_name: str
) -> bool:
    """Send acknowledgment message to WhatsApp user."""
    logger = get_logger("whatsapp_ack", {"app_name": app_name})
    
    # Get the appropriate configuration based on app name
    if app_name == config.aa_app_name:
        facebook_app_url = config.aa_facebook_app_url
    elif app_name == config.pp_app_name:
        facebook_app_url = config.pp_facebook_app_url
    else:
        logger.error(f"Unknown app name: {app_name}")
        return False

    # AA and PP send from different numbers with different access tokens; resolve
    # the token for THIS app (see config.token_for).
    wsp_token = config.token_for(app_name)
    if not facebook_app_url or not wsp_token:
        logger.error("WhatsApp API URL or token is not configured.")
        return False

    try:
        message = create_text_message(message_text)
        await send_whatsapp_message(
            user_wa_id, message, f"{facebook_app_url}/messages", wsp_token
        )
        logger.info(f"Acknowledgment sent successfully to {mask_pii(user_wa_id)}")
        return True
    except Exception as e:
        logger.error(f"Failed to send acknowledgment: {e}", exc_info=True)
        return False

async def _process_webhook_in_background(body: dict, app_name: str) -> None:
    """Process webhook in the background after sending an ACK."""
    webhook_payload = parse_webhook_payload(body)
    if not webhook_payload:
        logging.error("Failed to parse webhook payload.")
        return

    for sender_wa_id, message in webhook_payload.get_all_messages():
        try:
            await process_message(sender_wa_id, message, app_name)
        except Exception as e:
            logging.error(f"Error processing message {message.id}: {e}", exc_info=True)
            await _send_whatsapp_acknowledgment(
                sender_wa_id, "Error procesando mensaje.", app_name
            )

async def process_incoming_webhook_payload(body: dict, app_name: str) -> bool:
    """Core logic to process incoming webhook events from WhatsApp."""
    logging.info(f"Received webhook for {app_name} - sending immediate ACK.")
    task = asyncio.create_task(_process_webhook_in_background(body, app_name))
    _background_tasks.add(task)

    def _on_done(t: asyncio.Task) -> None:
        _background_tasks.discard(t)
        # A cancelled task (e.g. Cloud Run evicting the worker mid-message)
        # makes t.exception() itself raise CancelledError out of this
        # callback, which asyncio then logs as a spurious "Exception in
        # callback". Cancellation is not a processing failure — skip it.
        if t.cancelled():
            return
        exc = t.exception()
        if exc is not None:
            logging.error(
                f"Background webhook processing failed for {app_name}: {exc}",
                exc_info=exc,
            )

    task.add_done_callback(_on_done)
    return True

async def receive_message_aa(body: dict) -> bool:
    """Handles incoming messages for the AA application."""
    return await process_incoming_webhook_payload(body, config.aa_app_name)

async def receive_message_pp(body: dict) -> bool:
    """Handles incoming messages for the PP application."""
    return await process_incoming_webhook_payload(body, config.pp_app_name)

async def process_message(
    sender_wa_id: str, message: "WhatsAppMessage", app_name: str
) -> None:
    """Processes a single message from WhatsApp."""
    await create_agent_session(sender_wa_id, app_name, sender_wa_id)
    if message.type == "text":
        await _process_single_text_message(sender_wa_id, message, app_name)
    elif message.type == "audio" and message.audio:
        await handle_audio_message(sender_wa_id, message.audio.id, app_name)
    else:
        await _send_whatsapp_acknowledgment(
            sender_wa_id,
            "Solo puedo procesar mensajes de texto y audio. ¿En qué puedo ayudarte?",
            app_name,
        )

async def _process_single_text_message(
    sender_wa_id: str, message: "WhatsAppMessage", app_name: str
) -> None:
    """Process a single text message from WhatsApp."""
    message_text = message.get_message_content() or ""
    agent_response = await send_message_to_agent(
        sender_wa_id, app_name, sender_wa_id, message_text
    )
    response_text = agent_response or "No pude procesar tu mensaje. Intenta de nuevo."
    await _send_whatsapp_acknowledgment(sender_wa_id, response_text, app_name)

async def handle_audio_message(
    phone: str, audio_id: str, app_name: str
) -> None:
    """Processes an audio message: downloads, transcribes, and responds."""
    # Get the appropriate configuration based on app name
    if app_name == config.aa_app_name:
        facebook_app_url = config.aa_facebook_app_url
    elif app_name == config.pp_app_name:
        facebook_app_url = config.pp_facebook_app_url
    else:
        logging.error(f"Unknown app name: {app_name}")
        return

    # Per-app token: AA and PP use different numbers/tokens (see config.token_for).
    wsp_token = config.token_for(app_name)
    if not facebook_app_url or not wsp_token:
        logging.error(
            f"Incomplete WhatsApp config for audio in {app_name}"
        )
        return

    try:
        audio_content = await download_whatsapp_media(audio_id, config.whatsapp_base_url, wsp_token)
        if not audio_content:
            await send_whatsapp_message(
                phone, create_text_message("No pude descargar tu audio."), f"{facebook_app_url}/messages", wsp_token
            )
            return

        transcript = await transcribe_audio_file(audio_content)
        if not transcript:
            await send_whatsapp_message(
                phone, create_text_message("No pude entender tu audio."), f"{facebook_app_url}/messages", wsp_token
            )
            return

        response = await send_message_to_agent(phone, app_name, phone, transcript)
        await send_whatsapp_message(
            phone, create_text_message(response), f"{facebook_app_url}/messages", wsp_token
        )
    except Exception as e:
        logging.error(f"Error processing audio: {e}", exc_info=True)
        await send_whatsapp_message(
            phone, create_text_message("Error procesando tu audio."), f"{facebook_app_url}/messages", wsp_token
        )
