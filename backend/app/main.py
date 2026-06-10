import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.identity.seeds import seed_identity

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    db = SessionLocal()
    try:
        seed_identity(db)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning("Skipping identity seed during startup: %s", exc)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    return {"status": "healthy"}
