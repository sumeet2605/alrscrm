from __future__ import annotations

import json
import logging
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Request, Response

from app.core.request_context import (
    branch_id_var,
    clear_request_context,
    organization_id_var,
    request_id_var,
    user_id_var,
)
from app.core.security import decode_token
from app.operations.metrics import metrics_registry

ACCESS_LOGGER = logging.getLogger("app.access")
REQUEST_ID_HEADER = "X-Request-ID"


async def request_observability_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    clear_request_context()
    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
    request_id_var.set(request_id)
    _set_auth_context(request)
    started = time.perf_counter()
    status_code = 500
    response: Response | None = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        route = request.url.path
        metrics_registry.record_api_request(route, request.method, status_code, duration_ms)
        _log_access(request, route, duration_ms, status_code)
        if response is not None:
            response.headers[REQUEST_ID_HEADER] = request_id
        clear_request_context()


def _set_auth_context(request: Request) -> None:
    header = request.headers.get("authorization")
    if not header or not header.lower().startswith("bearer "):
        return
    token = header.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token, "access")
    except ValueError:
        return
    user_id_var.set(str(payload.get("sub")) if payload.get("sub") else None)
    organization_id_var.set(
        str(payload.get("organization_id")) if payload.get("organization_id") else None
    )
    branch_id_var.set(str(payload.get("branch_id")) if payload.get("branch_id") else None)


def _log_access(request: Request, route: str, duration_ms: float, status_code: int) -> None:
    ACCESS_LOGGER.info(
        json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "request_id": request_id_var.get(),
                "organization_id": organization_id_var.get(),
                "branch_id": branch_id_var.get(),
                "user_id": user_id_var.get(),
                "method": request.method,
                "route": route,
                "duration_ms": duration_ms,
                "status_code": status_code,
            },
            separators=(",", ":"),
        )
    )
