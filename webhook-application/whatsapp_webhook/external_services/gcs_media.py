"""Uploads WhatsApp producer media (image/PDF) to the private wsp-media GCS
bucket, returning a gs:// URI the agent reads directly (multimodal message —
see agent_client.send_to_agent). Bucket is private with a short lifecycle
delete; object names are random uuids, never derived from producer data.
"""
import asyncio
import uuid

from google.cloud import storage

from ..utils.app_config import config

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_BYTES = 20 * 1024 * 1024  # align with Gemini's inline/file size guidance


class UnsupportedMediaError(ValueError):
    """Raised when mime_type is outside ALLOWED_MIME_TYPES."""


class MediaTooLargeError(ValueError):
    """Raised when content exceeds MAX_BYTES."""


_storage_client: storage.Client | None = None


def _client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client


def _upload_sync(content: bytes, *, name: str, mime_type: str) -> None:
    """Blocking GCS write — only ever called via asyncio.to_thread."""
    bucket = _client().bucket(config.wsp_media_bucket)
    bucket.blob(name).upload_from_string(content, content_type=mime_type)


async def upload_media(content: bytes, *, mime_type: str, suffix: str = "") -> str:
    """Validates and uploads media, returning its gs:// URI.

    Raises UnsupportedMediaError / MediaTooLargeError on a rejected mime_type
    or oversized payload — callers (messages.handle_media_message) turn those
    into a clear WhatsApp reply to the producer instead of a 500.
    """
    if mime_type not in ALLOWED_MIME_TYPES:
        raise UnsupportedMediaError(mime_type)
    if len(content) > MAX_BYTES:
        raise MediaTooLargeError(str(len(content)))

    name = f"{uuid.uuid4().hex}{suffix}"
    # upload_from_string is a blocking network call; keep it off the event
    # loop (see plan risk: "upload_from_string sync en path async").
    await asyncio.to_thread(_upload_sync, content, name=name, mime_type=mime_type)
    return f"gs://{config.wsp_media_bucket}/{name}"
