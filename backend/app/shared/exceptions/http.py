from fastapi import HTTPException, status

from app.shared.exceptions.application import ConflictError, ForbiddenError, NotFoundError


def not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def forbidden(detail: str = "Insufficient permissions") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def application_not_found(detail: str) -> NotFoundError:
    return NotFoundError(detail)


def application_conflict(detail: str) -> ConflictError:
    return ConflictError(detail)


def application_forbidden(detail: str = "Insufficient permissions") -> ForbiddenError:
    return ForbiddenError(detail)
