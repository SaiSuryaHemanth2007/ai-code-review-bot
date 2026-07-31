from fastapi import APIRouter

from backend.schemas.dashboard_summary import DashboardSummary
from backend.schemas.quality_history import QualityHistory
from backend.schemas.review_trends import ReviewTrends
from backend.schemas.repository_statistics import RepositoryStatistics
from backend.schemas.provider_statistics import ProviderStatistics
from backend.schemas.leaderboard import Leaderboard

from backend.services.dashboard_service import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "",
    response_model=DashboardSummary,
    summary="Get dashboard summary",
)
def get_dashboard():
    """
    Returns dashboard summary statistics.
    """
    return dashboard_service.get_dashboard_summary()


@router.get(
    "/quality-history",
    response_model=QualityHistory,
    summary="Get quality score history",
)
def get_quality_history():
    """
    Returns historical quality scores.
    """
    return dashboard_service.get_quality_history()


@router.get(
    "/trends",
    response_model=ReviewTrends,
    summary="Get review trends",
)
def get_review_trends():
    """
    Returns review counts grouped by date.
    """
    return dashboard_service.get_review_trends()


@router.get(
    "/repositories",
    response_model=RepositoryStatistics,
    summary="Get repository statistics",
)
def get_repository_statistics():
    """
    Returns statistics for each repository.
    """
    return dashboard_service.get_repository_statistics()


@router.get(
    "/providers",
    response_model=ProviderStatistics,
    summary="Get provider statistics",
)
def get_provider_statistics():
    """
    Returns statistics for each provider.
    """
    return dashboard_service.get_provider_statistics()



@router.get(
    "/leaderboard",
    response_model=Leaderboard,
    summary="Get leaderboard statistics",
)
def get_leaderboard():
    """
    Returns leaderboard statistics.
    """
    return dashboard_service.get_leaderboard()
