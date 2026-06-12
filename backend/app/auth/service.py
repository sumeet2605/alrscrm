from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import RefreshTokenSession
from app.auth.rate_limit import check_login_rate_limit
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token_with_identifier,
    decode_token,
    hash_password,
    hash_token_identifier,
    verify_password,
)
from app.identity.models import Organization, User
from app.identity.services.user_service import get_user, get_user_by_organization_email
from app.shared.exceptions.application import UnauthorizedError
from app.shared.services.audit_service import record_audit_event


def _normalize_organization_code(organization_code: str) -> str:
    return organization_code.strip().upper()


def _token_claims(user: User) -> dict[str, str | None]:
    return {
        "organization_id": str(user.organization_id),
        "branch_id": str(user.branch_id) if user.branch_id else None,
    }


def authenticate_user(
    db: Session,
    organization_code: str,
    email: str,
    password: str,
    ip_address: str | None = None,
) -> User:
    normalized_code = _normalize_organization_code(organization_code)
    check_login_rate_limit(email, ip_address, normalized_code)
    organization = (
        db.query(Organization)
        .filter(Organization.code == normalized_code, Organization.is_active.is_(True))
        .one_or_none()
    )
    user = (
        get_user_by_organization_email(db, organization.id, email)
        if organization is not None
        else None
    )
    if user is None or not verify_password(password, user.password_hash):
        record_audit_event(
            db,
            "auth.login_failed",
            None,
            "User",
            metadata={"email": email, "organization_code": normalized_code},
            organization_id=organization.id if organization else None,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    record_audit_event(
        db,
        "auth.login_succeeded",
        user.id,
        "User",
        user.id,
        organization_id=user.organization_id,
        branch_id=user.branch_id,
    )
    db.commit()
    return user


def issue_token_pair(
    db: Session,
    user_id: UUID,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict[str, str]:
    settings = get_settings()
    token_identifier = str(uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.refresh_token_expire_minutes)
    refresh_session = RefreshTokenSession(
        user_id=user_id,
        token_hash=hash_token_identifier(token_identifier),
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent[:255] if user_agent else None,
    )
    db.add(refresh_session)
    db.commit()
    claims = _token_claims(get_user(db, user_id))
    return {
        "access_token": create_access_token(user_id, claims),
        "refresh_token": create_refresh_token_with_identifier(user_id, token_identifier, claims),
        "token_type": "bearer",
    }


def refresh_access_token(
    db: Session,
    refresh_token: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict[str, str]:
    try:
        payload = decode_token(refresh_token, "refresh")
        token_identifier = payload["jti"]
        user = get_user(db, UUID(payload["sub"]))
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc
    refresh_session = (
        db.query(RefreshTokenSession)
        .filter(RefreshTokenSession.token_hash == hash_token_identifier(token_identifier))
        .one_or_none()
    )
    if refresh_session is None:
        raise UnauthorizedError("Invalid refresh token")
    now = datetime.now(UTC)
    expires_at = refresh_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if (
        refresh_session.revoked_at is not None
        or refresh_session.replaced_by_token_id is not None
        or expires_at <= now
    ):
        _revoke_all_user_sessions(db, user.id)
        db.commit()
        raise UnauthorizedError("Invalid refresh token")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    tokens = issue_token_pair(db, user.id, ip_address, user_agent)
    replacement = (
        db.query(RefreshTokenSession)
        .filter(RefreshTokenSession.user_id == user.id)
        .order_by(RefreshTokenSession.created_at.desc())
        .first()
    )
    refresh_session.replaced_by_token_id = replacement.id if replacement else None
    refresh_session.revoked_at = now
    record_audit_event(db, "auth.refresh_rotated", user.id, "User", user.id)
    db.commit()
    return tokens


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token, "refresh")
        token_identifier = payload["jti"]
    except (ValueError, KeyError) as exc:
        raise UnauthorizedError("Invalid refresh token") from exc
    refresh_session = (
        db.query(RefreshTokenSession)
        .filter(RefreshTokenSession.token_hash == hash_token_identifier(token_identifier))
        .one_or_none()
    )
    if refresh_session is None:
        raise UnauthorizedError("Invalid refresh token")
    refresh_session.revoked_at = datetime.now(UTC)
    record_audit_event(db, "auth.logout", refresh_session.user_id, "User", refresh_session.user_id)
    db.commit()


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict[str, str]:
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    if verify_password(new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password must be different from current password",
        )
    user.password_hash = hash_password(new_password)
    user.password_reset_required = False
    _revoke_all_user_sessions(db, user.id)
    record_audit_event(
        db,
        "auth.password_changed",
        user.id,
        "User",
        user.id,
        organization_id=user.organization_id,
        branch_id=user.branch_id,
    )
    db.commit()
    return issue_token_pair(db, user.id, ip_address, user_agent)


def _revoke_all_user_sessions(db: Session, user_id: UUID) -> None:
    db.query(RefreshTokenSession).filter(
        RefreshTokenSession.user_id == user_id,
        RefreshTokenSession.revoked_at.is_(None),
    ).update({"revoked_at": datetime.now(UTC)})
