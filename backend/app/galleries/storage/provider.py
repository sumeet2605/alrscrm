from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class StoredFile:
    storage_path: str
    thumbnail_path: str | None = None
    file_size: int = 0
    image_width: int = 1
    image_height: int = 1


class StorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_name: str, content: bytes) -> StoredFile:
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
    def upload_file(self, file_name: str, content: bytes) -> StoredFile:
        return StoredFile(storage_path=f"local://gallery/{file_name}", file_size=len(content))

    def delete_file(self, storage_path: str) -> None:
        return None

    def generate_signed_url(self, storage_path: str) -> str:
        return storage_path

    def generate_thumbnail_url(self, thumbnail_path: str | None) -> str | None:
        return thumbnail_path


def get_storage_provider() -> StorageProvider:
    return LocalMetadataStorageProvider()
