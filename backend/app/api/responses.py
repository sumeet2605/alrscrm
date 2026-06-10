from typing import Any


def api_response(
    message: str,
    data: Any = None,
    success: bool = True,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = {"success": success, "message": message, "data": data}
    if meta is not None:
        response["meta"] = meta
    return response
