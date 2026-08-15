"""Transcripción de audio usando Google Cloud Speech."""
import asyncio
from typing import Optional
from google.cloud import speech

from .utils.logging import get_logger

logger = get_logger("transcription")


async def transcribe_audio_file(audio_content: bytes) -> Optional[str]:
    """Transcribe audio OGG_OPUS de WhatsApp."""
    try:
        client = speech.SpeechClient()
        recognition_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=16000,
            language_code="es-CL"
        )
        audio = speech.RecognitionAudio(content=audio_content)
        # client.recognize is a blocking gRPC call — run it off the event loop.
        response = await asyncio.to_thread(
            client.recognize, config=recognition_config, audio=audio
        )

        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            # Transcript content is user PII — only expose it at DEBUG.
            logger.info("Audio transcribed successfully")
            logger.debug("Transcript content", extra={"transcript": transcript[:50]})
            return transcript.strip()

        logger.warning("Audio transcription returned no results.")
        return None
    except Exception as e:
        logger.error(f"Error during audio transcription: {e}", exc_info=True)
        return None
