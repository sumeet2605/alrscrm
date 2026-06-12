import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.observability import request_observability_middleware
from app.identity.seeds import validate_identity_seed
from app.operations.health import liveness, readiness
from app.shared.exceptions.application import ApplicationError

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_settings()
    db = SessionLocal()
    try:
        validate_identity_seed(db)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning("Skipping identity baseline check during startup: %s", exc)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.middleware("http")(request_observability_middleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(ApplicationError)
def application_error_handler(_: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "data": {}},
    )


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/live")
def health_live():
    return liveness()


@app.get("/health/ready")
def health_ready():
    db: Session = SessionLocal()
    try:
        payload, status_code = readiness(db)
        return JSONResponse(status_code=status_code, content=payload)
    finally:
        db.close()
