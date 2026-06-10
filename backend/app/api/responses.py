from typing import Any


def api_response(message: str, data: Any = None, success: bool = True) -> dict[str, Any]:
    return {"success": success, "message": message, "data": data}
