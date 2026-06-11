from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(_bcrypt_input(password))


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(_bcrypt_input(plain_password), password_hash)


def _bcrypt_input(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def hash_token_identifier(token_identifier: str) -> str:
    return sha256(token_identifier.encode("utf-8")).hexdigest()


def create_token(
    subject: UUID,
    token_type: str,
    expires_delta: timedelta | None = None,
    token_identifier: str | None = None,
    claims: dict[str, Any] | None = None,
) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "jti": token_identifier or str(uuid4()),
        "exp": expires_at,
    }
    if claims:
        payload.update(claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: UUID, claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    return create_token(
        subject,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
        claims=claims,
    )


def create_refresh_token(subject: UUID) -> str:
    settings = get_settings()
    return create_token(
        subject,
        "refresh",
        timedelta(minutes=settings.refresh_token_expire_minutes),
    )


def create_refresh_token_with_identifier(
    subject: UUID, token_identifier: str, claims: dict[str, Any] | None = None
) -> str:
    settings = get_settings()
    return create_token(
        subject,
        "refresh",
        timedelta(minutes=settings.refresh_token_expire_minutes),
        token_identifier=token_identifier,
        claims=claims,
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")
    if not payload.get("sub"):
        raise ValueError("Invalid token subject")
    return payload
