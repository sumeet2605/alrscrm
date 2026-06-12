import json
import logging

from app.core.config import Settings
from app.operations.metrics import metrics_registry
from app.shared.models.audit_log import AuditLog
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_liveness_and_readiness(client: TestClient) -> None:
    live_response = client.get("/health/live")
    ready_response = client.get("/health/ready")

    assert live_response.status_code == 200
    assert live_response.json() == {"status": "live"}
    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"
    assert ready_response.json()["checks"]["database"]["ok"] is True
    assert ready_response.json()["checks"]["storage"]["ok"] is True
    assert ready_response.json()["checks"]["migrations"]["ok"] is True


def test_request_id_response_header(client: TestClient) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "req-test-123"})

    assert response.headers["X-Request-ID"] == "req-test-123"


def test_structured_access_log(client: TestClient, caplog) -> None:
    caplog.set_level(logging.INFO, logger="app.access")

    response = client.get("/health/live", headers={"X-Request-ID": "req-log-123"})

    assert response.status_code == 200
    log_payload = json.loads(caplog.records[-1].message)
    assert log_payload["request_id"] == "req-log-123"
    assert log_payload["route"] == "/health/live"
    assert log_payload["status_code"] == 200
    assert "duration_ms" in log_payload


def test_request_id_is_written_to_audit_metadata(
    client: TestClient,
    db: Session,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/organizations",
        headers={**auth_headers, "X-Request-ID": "req-audit-123"},
        json={"name": "Audit Tenant", "code": "AUDIT"},
    )

    assert response.status_code == 201
    audit = db.query(AuditLog).filter(AuditLog.action == "organization.created").first()
    assert audit is not None
    assert audit.metadata_json["request_id"] == "req-audit-123"


def test_platform_health_metrics_requires_super_admin(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    metrics_registry.reset()
    client.get("/health/live")

    response = client.get("/api/v1/platform/health/metrics", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["api_request_count"] >= 1
    assert "api_average_latency_ms" in data
    assert "database_latency_ms" in data
    assert "storage_latency_ms" in data


def test_production_secret_validation_requires_strong_secrets() -> None:
    try:
        Settings(
            environment="production",
            SECRET_KEY="short",
            JWT_SECRET="change-this-secret-in-production",
            INTEGRATION_ENCRYPTION_KEY="",
        )
    except ValidationError as exc:
        assert "SECRET_KEY" in str(exc)
    else:
        raise AssertionError("Production settings accepted weak secrets")


def test_production_secret_validation_accepts_strong_secrets() -> None:
    settings = Settings(
        environment="production",
        SECRET_KEY="app-secret-1234567890-ABCDEFGH-strong",
        JWT_SECRET="jwt-secret-1234567890-ABCDEFGH-strong",
        integration_encryption_key="integration-secret-1234567890-ABCDEFGH",
    )

    assert settings.environment == "production"
