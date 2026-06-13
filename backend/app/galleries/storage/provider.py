import logging
from abc import ABC, abstractmethod
from base64 import b64encode
from dataclasses import dataclass
from urllib.parse import quote, urlparse

from app.core.config import get_settings
from app.shared.exceptions.application import ValidationError

logger = logging.getLogger(__name__)
SPACES_INVALID_ARGUMENT_CODE = "InvalidArgument"


def _client_error_code(exc: Exception) -> str | None:
    response = getattr(exc, "response", None)
    if not isinstance(response, dict):
        return None
    error = response.get("Error")
    if not isinstance(error, dict):
        return None
    code = error.get("Code")
    return code if isinstance(code, str) else None


def _client_error_message(exc: Exception) -> str | None:
    response = getattr(exc, "response", None)
    if not isinstance(response, dict):
        return None
    error = response.get("Error")
    if not isinstance(error, dict):
        return None
    message = error.get("Message")
    return message if isinstance(message, str) else None


def _log_client_error(message: str, exc: Exception, bucket: str, key: str) -> None:
    logger.warning(
        message,
        extra={
            "spaces_error": {
                "Bucket": bucket,
                "Key": key,
                "ErrorCode": _client_error_code(exc),
                "ErrorMessage": _client_error_message(exc),
                "Exception": exc.__class__.__name__,
            }
        },
    )


def _spaces_endpoint_url(region: str, bucket: str, endpoint_url: str | None) -> str:
    default_endpoint = f"https://{region}.digitaloceanspaces.com"
    if not endpoint_url:
        return default_endpoint
    parsed = urlparse(endpoint_url)
    bucket_endpoint = f"{bucket}.{region}.digitaloceanspaces.com"
    if parsed.netloc == bucket_endpoint:
        return default_endpoint
    return endpoint_url


@dataclass(frozen=True)
class StoredFile:
    storage_path: str
    thumbnail_path: str | None = None
    file_size: int = 0
    image_width: int = 1
    image_height: int = 1


class StorageProvider(ABC):
    @abstractmethod
    def upload_file(
        self, file_name: str, content: bytes, content_type: str | None = None
    ) -> StoredFile:
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, storage_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_signed_url(self, storage_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_thumbnail_url(self, thumbnail_path: str | None) -> str | None:
        raise NotImplementedError


class LocalMetadataStorageProvider(StorageProvider):
    def upload_file(
        self, file_name: str, content: bytes, content_type: str | None = None
    ) -> StoredFile:
        media_type = content_type or "application/octet-stream"
        data_url = f"data:{media_type};base64,{b64encode(content).decode('ascii')}"
        return StoredFile(
            storage_path=f"local://gallery/{file_name}",
            thumbnail_path=data_url,
            file_size=len(content),
        )

    def delete_file(self, storage_path: str) -> None:
        return None

    def generate_signed_url(self, storage_path: str) -> str:
        return storage_path

    def generate_thumbnail_url(self, thumbnail_path: str | None) -> str | None:
        return thumbnail_path


class DigitalOceanSpacesStorageProvider(StorageProvider):
    def __init__(
        self,
        *,
        region: str,
        bucket: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str | None = None,
        cdn_url: str | None = None,
        path_prefix: str = "alrscrm",
        signed_url_expire_seconds: int = 900,
    ) -> None:
        try:
            import boto3
            from botocore.config import Config
        except ImportError as exc:
            raise ValidationError("boto3 is required for DigitalOcean Spaces storage") from exc
        self.bucket = bucket
        self.region = region
        self.cdn_url = cdn_url.rstrip("/") if cdn_url else None
        self.path_prefix = path_prefix.strip("/")
        self.signed_url_expire_seconds = signed_url_expire_seconds
        self.endpoint_url = _spaces_endpoint_url(region, bucket, endpoint_url)
        self.client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
                s3={"addressing_style": "virtual"},
            ),
        )

    def _key(self, file_name: str) -> str:
        cleaned_name = file_name.strip().lstrip("/")
        if not cleaned_name:
            raise ValidationError("Storage file name is required")
        if self.path_prefix:
            return f"{self.path_prefix}/{cleaned_name}"
        return cleaned_name

    def _public_url(self, key: str) -> str | None:
        if not self.cdn_url:
            return None
        return f"{self.cdn_url}/{quote(key)}"

    def upload_file(
        self, file_name: str, content: bytes, content_type: str | None = None
    ) -> StoredFile:
        key = self._key(file_name)
        put_object_args = {"Bucket": self.bucket, "Key": key, "Body": content}
        if content_type:
            put_object_args["ContentType"] = content_type
        logger.info(
            "Uploading file to DigitalOcean Spaces",
            extra={
                "spaces_put_object": {
                    "Bucket": self.bucket,
                    "Key": key,
                    "ContentType": content_type,
                    "ACL": None,
                    "Metadata": None,
                    "CacheControl": None,
                    "ExtraArgs": [],
                    "BodyBytes": len(content),
                }
            },
        )
        try:
            self.client.put_object(**put_object_args)
        except Exception as exc:
            error_code = _client_error_code(exc)
            _log_client_error("DigitalOcean Spaces PutObject failed", exc, self.bucket, key)
            if error_code == SPACES_INVALID_ARGUMENT_CODE and "ContentType" in put_object_args:
                fallback_args = {"Bucket": self.bucket, "Key": key, "Body": content}
                logger.warning(
                    "Retrying DigitalOcean Spaces PutObject with minimal arguments",
                    extra={
                        "spaces_put_object": {
                            "Bucket": self.bucket,
                            "Key": key,
                            "ContentType": None,
                            "ACL": None,
                            "Metadata": None,
                            "CacheControl": None,
                            "ExtraArgs": [],
                            "BodyBytes": len(content),
                        }
                    },
                )
                self.client.put_object(**fallback_args)
            else:
                raise
        return StoredFile(storage_path=key, thumbnail_path=key, file_size=len(content))

    def delete_file(self, storage_path: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=storage_path)
        except Exception as exc:
            _log_client_error(
                "DigitalOcean Spaces DeleteObject failed; continuing gallery delete",
                exc,
                self.bucket,
                storage_path,
            )

    def generate_signed_url(self, storage_path: str) -> str:
        public_url = self._public_url(storage_path)
        if public_url:
            return public_url
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": storage_path},
            ExpiresIn=self.signed_url_expire_seconds,
        )

    def generate_thumbnail_url(self, thumbnail_path: str | None) -> str | None:
        if thumbnail_path is None:
            return None
        return self.generate_signed_url(thumbnail_path)


def get_storage_provider() -> StorageProvider:
    settings = get_settings()
    if settings.storage_provider.lower() in {"digitalocean", "spaces", "do_spaces"}:
        return DigitalOceanSpacesStorageProvider(
            region=settings.do_spaces_region or "",
            bucket=settings.do_spaces_bucket or "",
            access_key=settings.do_spaces_access_key or "",
            secret_key=settings.do_spaces_secret_key or "",
            endpoint_url=settings.do_spaces_endpoint_url,
            cdn_url=settings.do_spaces_cdn_url,
            path_prefix=settings.do_spaces_path_prefix,
            signed_url_expire_seconds=settings.storage_signed_url_expire_seconds,
        )
    return LocalMetadataStorageProvider()
