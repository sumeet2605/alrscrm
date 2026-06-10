from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Any
    meta: dict[str, Any] | None = None
