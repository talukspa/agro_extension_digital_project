"""Tests for the GCS upload helper used by the WhatsApp media-to-agent path.

upload_media() takes the raw bytes downloaded from Meta, validates mime/size,
and uploads to the private wsp-media bucket, returning a gs:// URI. No real
GCP creds/network: the storage client is monkeypatched out.
"""
import pytest

from whatsapp_webhook.external_services import gcs_media


@pytest.mark.asyncio
async def test_upload_media_returns_gs_uri(monkeypatch):
    uploaded = {}

    class FakeBlob:
        def upload_from_string(self, data, content_type):
            uploaded["ct"] = content_type
            uploaded["n"] = len(data)

    class FakeBucket:
        def blob(self, name):
            uploaded["name"] = name
            return FakeBlob()

    class FakeClient:
        def bucket(self, b):
            uploaded["bucket"] = b
            return FakeBucket()

    monkeypatch.setattr(gcs_media, "_client", lambda: FakeClient())
    monkeypatch.setattr(gcs_media.config, "wsp_media_bucket", "b-prd", raising=False)

    uri = await gcs_media.upload_media(b"\xff\xd8data", mime_type="image/jpeg", suffix=".jpg")

    assert uri == f"gs://b-prd/{uploaded['name']}"
    assert uri.startswith("gs://b-prd/") and uri.endswith(".jpg")
    assert uploaded["ct"] == "image/jpeg"
    assert uploaded["bucket"] == "b-prd"
    assert uploaded["n"] == len(b"\xff\xd8data")


@pytest.mark.asyncio
async def test_upload_media_rejects_unsupported_mime():
    with pytest.raises(gcs_media.UnsupportedMediaError):
        await gcs_media.upload_media(b"x", mime_type="application/zip")


@pytest.mark.asyncio
async def test_upload_media_rejects_oversized_content():
    with pytest.raises(gcs_media.MediaTooLargeError):
        await gcs_media.upload_media(
            b"x" * (gcs_media.MAX_BYTES + 1), mime_type="application/pdf"
        )


@pytest.mark.asyncio
async def test_upload_media_name_has_no_suffix_by_default(monkeypatch):
    uploaded = {}

    class FakeBlob:
        def upload_from_string(self, data, content_type):
            pass

    class FakeBucket:
        def blob(self, name):
            uploaded["name"] = name
            return FakeBlob()

    class FakeClient:
        def bucket(self, b):
            return FakeBucket()

    monkeypatch.setattr(gcs_media, "_client", lambda: FakeClient())
    monkeypatch.setattr(gcs_media.config, "wsp_media_bucket", "b-prd", raising=False)

    await gcs_media.upload_media(b"data", mime_type="application/pdf")

    assert "." not in uploaded["name"]
