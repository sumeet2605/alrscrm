from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
organization_id_var: ContextVar[str | None] = ContextVar("organization_id", default=None)
branch_id_var: ContextVar[str | None] = ContextVar("branch_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)


def get_request_id() -> str | None:
    return request_id_var.get()


def clear_request_context() -> None:
    request_id_var.set(None)
    organization_id_var.set(None)
    branch_id_var.set(None)
    user_id_var.set(None)
