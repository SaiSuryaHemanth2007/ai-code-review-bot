from fastapi import APIRouter

from backend.schemas.health_response import HealthResponse
from backend.services.health_service import health_service

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
)
def get_health():
    """
    Returns the current application health status.
    """
    return health_service.get_health()