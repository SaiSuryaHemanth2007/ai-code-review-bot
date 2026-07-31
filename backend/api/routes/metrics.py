from fastapi import APIRouter

from backend.schemas.metrics_response import MetricsResponse
from backend.services.metrics_service import metrics_service

router = APIRouter()


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Application Metrics",
)
def get_metrics():
    """
    Returns application metrics.
    """

    return metrics_service.get_metrics()