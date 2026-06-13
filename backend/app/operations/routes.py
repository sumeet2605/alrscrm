from fastapi import APIRouter, Depends

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.operations.metrics import metrics_registry

router = APIRouter(prefix="/platform/health", tags=["Platform Health"])


@router.get("/metrics", response_model=APIResponse)
def get_platform_health_metrics(
    _context=Depends(require_permissions("platform:health:metrics")),
):
    return api_response("Platform health metrics retrieved", metrics_registry.snapshot())
