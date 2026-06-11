import base64
import json
from hashlib import sha256
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings
from app.shared.exceptions.application import ValidationError


def _fernet() -> Fernet:
    settings = get_settings()
    secret = settings.integration_encryption_key or settings.jwt_secret_key
    key = base64.urlsafe_b64encode(sha256(secret.encode("utf-8")).digest())
    return Fernet(key)


def encrypt_json(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _fernet().encrypt(encoded).decode("utf-8")


def decrypt_json(value: str) -> dict[str, Any]:
    try:
        decoded = _fernet().decrypt(value.encode("utf-8"))
        payload = json.loads(decoded.decode("utf-8"))
    except (InvalidToken, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationError("Stored credentials could not be decrypted") from exc
    if not isinstance(payload, dict):
        raise ValidationError("Stored credentials are invalid")
    return payload
