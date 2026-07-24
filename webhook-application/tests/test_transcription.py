"""Tests for audio transcription (whatsapp_webhook.transcription).

The Google Cloud Speech client is fully mocked; we assert that recognize runs
off the event loop (via asyncio.to_thread), that the transcript is extracted &
stripped, and that empty/error results yield None.
"""
from unittest.mock import MagicMock, patch

import pytest

from whatsapp_webhook import transcription


def _fake_response(transcript):
    alt = MagicMock()
    alt.transcript = transcript
    result = MagicMock()
    result.alternatives = [alt]
    resp = MagicMock()
    resp.results = [result]
    return resp


@pytest.mark.asyncio
async def test_transcribe_extracts_and_strips_transcript():
    client = MagicMock()
    client.recognize = MagicMock(return_value=_fake_response("  hola mundo  "))
    with patch.object(transcription.speech, "SpeechClient", return_value=client):
        out = await transcription.transcribe_audio_file(b"oggbytes")
    assert out == "hola mundo"
    # recognize called with our config + audio (keyword args).
    assert client.recognize.call_count == 1
    kwargs = client.recognize.call_args.kwargs
    assert kwargs["audio"].content == b"oggbytes"


@pytest.mark.asyncio
async def test_transcribe_no_results_returns_none():
    resp = MagicMock()
    resp.results = []
    client = MagicMock()
    client.recognize = MagicMock(return_value=resp)
    with patch.object(transcription.speech, "SpeechClient", return_value=client):
        out = await transcription.transcribe_audio_file(b"oggbytes")
    assert out is None


@pytest.mark.asyncio
async def test_transcribe_client_error_returns_none():
    client = MagicMock()
    client.recognize = MagicMock(side_effect=RuntimeError("grpc down"))
    with patch.object(transcription.speech, "SpeechClient", return_value=client):
        out = await transcription.transcribe_audio_file(b"oggbytes")
    assert out is None


@pytest.mark.asyncio
async def test_transcribe_runs_off_event_loop():
    """recognize must be dispatched through asyncio.to_thread, not called inline."""
    client = MagicMock()
    client.recognize = MagicMock(return_value=_fake_response("x"))
    with patch.object(transcription.speech, "SpeechClient", return_value=client), \
         patch("whatsapp_webhook.transcription.asyncio.to_thread") as to_thread:
        async def _run(fn, *a, **kw):
            return fn(*a, **kw)
        to_thread.side_effect = _run
        out = await transcription.transcribe_audio_file(b"oggbytes")
    assert out == "x"
    to_thread.assert_called_once()
