import logging

import boto3
from app.galleries.storage.provider import DigitalOceanSpacesStorageProvider
from botocore.exceptions import ClientError


class FakeS3Client:
    def __init__(self) -> None:
        self.put_object_calls: list[dict] = []
        self.delete_object_calls: list[dict] = []
        self.fail_first_put = False
        self.fail_delete = False

    def put_object(self, **kwargs):
        self.put_object_calls.append(kwargs)
        if self.fail_first_put and len(self.put_object_calls) == 1:
            raise ClientError(
                {"Error": {"Code": "InvalidArgument", "Message": "None"}},
                "PutObject",
            )

    def delete_object(self, **kwargs):
        self.delete_object_calls.append(kwargs)
        if self.fail_delete:
            raise ClientError(
                {"Error": {"Code": "InvalidArgument", "Message": "None"}},
                "DeleteObject",
            )
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
    assert config.s3 == {"addressing_style": "virtual"}


def test_spaces_provider_normalizes_bucket_endpoint_url(monkeypatch):
    captured_kwargs: dict = {}

    def fake_boto3_client(*args, **kwargs):
        captured_kwargs["kwargs"] = kwargs
        return FakeS3Client()

    monkeypatch.setattr(boto3, "client", fake_boto3_client)

    provider = DigitalOceanSpacesStorageProvider(
        region="sgp1",
        bucket="alrscrm-uat",
        access_key="access-key",
        secret_key="secret-key",
        endpoint_url="https://alrscrm-uat.sgp1.digitaloceanspaces.com",
    )

    assert provider.endpoint_url == "https://sgp1.digitaloceanspaces.com"
    assert captured_kwargs["kwargs"]["endpoint_url"] == "https://sgp1.digitaloceanspaces.com"


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


def test_spaces_upload_retries_invalid_argument_with_minimal_arguments(monkeypatch):
    fake_client = FakeS3Client()
    fake_client.fail_first_put = True
    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: fake_client)
    provider = DigitalOceanSpacesStorageProvider(
        region="sgp1",
        bucket="alrscrm-uat",
        access_key="access-key",
        secret_key="secret-key",
        path_prefix="alrscrm",
    )

    stored_file = provider.upload_file("gallery/photo.jpg", b"image-bytes", "image/jpeg")

    assert fake_client.put_object_calls == [
        {
            "Bucket": "alrscrm-uat",
            "Key": "alrscrm/gallery/photo.jpg",
            "Body": b"image-bytes",
            "ContentType": "image/jpeg",
        },
        {
            "Bucket": "alrscrm-uat",
            "Key": "alrscrm/gallery/photo.jpg",
            "Body": b"image-bytes",
        },
    ]
    assert stored_file.storage_path == "alrscrm/gallery/photo.jpg"


def test_spaces_delete_logs_and_continues_on_invalid_argument(monkeypatch, caplog):
    fake_client = FakeS3Client()
    fake_client.fail_delete = True
    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: fake_client)
    provider = DigitalOceanSpacesStorageProvider(
        region="sgp1",
        bucket="alrscrm-uat",
        access_key="access-key",
        secret_key="secret-key",
    )

    with caplog.at_level(logging.WARNING, logger="app.galleries.storage.provider"):
        provider.delete_file("alrscrm/gallery/photo.jpg")

    assert fake_client.delete_object_calls == [
        {"Bucket": "alrscrm-uat", "Key": "alrscrm/gallery/photo.jpg"}
    ]
    assert caplog.records[0].spaces_error == {
        "Bucket": "alrscrm-uat",
        "Key": "alrscrm/gallery/photo.jpg",
        "ErrorCode": "InvalidArgument",
        "ErrorMessage": "None",
        "Exception": "ClientError",
    }
