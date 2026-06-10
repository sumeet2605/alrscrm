class ApplicationError(Exception):
    status_code = 500
    message = "Application error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundError(ApplicationError):
    status_code = 404
    message = "Resource not found"


class ConflictError(ApplicationError):
    status_code = 409
    message = "Resource conflict"


class ForbiddenError(ApplicationError):
    status_code = 403
    message = "Insufficient permissions"


class UnauthorizedError(ApplicationError):
    status_code = 401
    message = "Authentication required"


class ValidationError(ApplicationError):
    status_code = 422
    message = "Validation error"


class GoneError(ApplicationError):
    status_code = 410
    message = "Resource gone"


class BadRequestError(ApplicationError):
    status_code = 400
    message = "Bad request"
