import logging

import boto3
from app.galleries.storage.provider import DigitalOceanSpacesStorageProvider


class FakeS3Client:
    def __init__(self) -> None:
        self.put_object_calls: list[dict] = []

    def put_object(self, **kwargs):
        self.put_object_calls.append(kwargs)

    def delete_object(self, **kwargs):
        return None

    def generate_presigned_url(self, *args, **kwargs):
        return "https://signed.example.test/photo.jpg"


def test_spaces_provider_uses_checksum_compatible_client_config(monkeypatch):
    captured_kwargs: dict = {}
    fake_client = FakeS3Client()

    def fake_boto3_client(*args, **kwargs):
        captured_kwargs["args"] = args
        captured_kwargs["kwargs"] = kwargs
        return fake_client

    monkeypatch.setattr(boto3, "client", fake_boto3_client)

    DigitalOceanSpacesStorageProvider(
        region="sgp1",
        bucket="alrscrm-uat",
        access_key="access-key",
        secret_key="secret-key",
    )

    config = captured_kwargs["kwargs"]["config"]
    assert captured_kwargs["args"] == ("s3",)
    assert captured_kwargs["kwargs"]["endpoint_url"] == "https://sgp1.digitaloceanspaces.com"
    assert config.request_checksum_calculation == "when_required"
    assert config.response_checksum_validation == "when_required"


def test_spaces_upload_uses_minimal_put_object_arguments(monkeypatch, caplog):
    fake_client = FakeS3Client()
    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: fake_client)
    provider = DigitalOceanSpacesStorageProvider(
        region="sgp1",
        bucket="alrscrm-uat",
        access_key="access-key",
        secret_key="secret-key",
        path_prefix="alrscrm/uat",
    )

    with caplog.at_level(logging.INFO, logger="app.galleries.storage.provider"):
        stored_file = provider.upload_file(
            "org-1/branch-1/gallery-1/photo.jpg",
            b"image-bytes",
            "image/jpeg",
        )

    assert fake_client.put_object_calls == [
        {
            "Bucket": "alrscrm-uat",
            "Key": "alrscrm/uat/org-1/branch-1/gallery-1/photo.jpg",
            "Body": b"image-bytes",
            "ContentType": "image/jpeg",
        }
    ]
    assert "ACL" not in fake_client.put_object_calls[0]
    assert "Metadata" not in fake_client.put_object_calls[0]
    assert "CacheControl" not in fake_client.put_object_calls[0]
    assert stored_file.storage_path == "alrscrm/uat/org-1/branch-1/gallery-1/photo.jpg"
    assert caplog.records[0].spaces_put_object == {
        "Bucket": "alrscrm-uat",
        "Key": "alrscrm/uat/org-1/branch-1/gallery-1/photo.jpg",
        "ContentType": "image/jpeg",
        "ACL": None,
        "Metadata": None,
        "CacheControl": None,
        "ExtraArgs": [],
        "BodyBytes": 11,
    }
