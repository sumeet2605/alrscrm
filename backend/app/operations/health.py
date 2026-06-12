from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.galleries.storage.provider import DigitalOceanSpacesStorageProvider, get_storage_provider
from app.operations.metrics import metrics_registry


def liveness() -> dict[str, str]:
    return {"status": "live"}


def readiness(db: Session) -> tuple[dict[str, Any], int]:
    checks = {
        "database": _database_check(db),
        "storage": _storage_check(),
        "migrations": _migration_check(db),
    }
    ready = all(item["ok"] for item in checks.values())
    return {"status": "ready" if ready else "not_ready", "checks": checks}, 200 if ready else 503


def _database_check(db: Session) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return {"ok": False, "error": exc.__class__.__name__}
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    metrics_registry.record_database_latency(duration_ms)
    return {"ok": True, "duration_ms": duration_ms}


def _storage_check() -> dict[str, Any]:
    started = time.perf_counter()
    try:
        provider = get_storage_provider()
        if isinstance(provider, DigitalOceanSpacesStorageProvider):
            provider.client.head_bucket(Bucket=provider.bucket)
        else:
            provider.generate_signed_url("local://health")
    except Exception as exc:  # noqa: BLE001 - readiness must report dependency failures.
        return {"ok": False, "error": exc.__class__.__name__}
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    metrics_registry.record_storage_latency(duration_ms)
    return {"ok": True, "duration_ms": duration_ms}


def _migration_check(db: Session) -> dict[str, Any]:
    if db.bind is not None and db.bind.dialect.name == "sqlite":
        return {"ok": True, "current": "sqlite-test", "head": "sqlite-test"}
    try:
        current = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
        head = _migration_head()
    except Exception as exc:  # noqa: BLE001 - readiness must report dependency failures.
        return {"ok": False, "error": exc.__class__.__name__}
    return {"ok": current == head, "current": current, "head": head}


def _migration_head() -> str:
    backend_root = Path(__file__).resolve().parents[2]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(config)
    head = script.get_current_head()
    if head is None:
        raise RuntimeError("Alembic head could not be resolved")
    return head
