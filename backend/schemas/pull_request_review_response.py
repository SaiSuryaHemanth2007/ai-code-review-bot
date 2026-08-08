"""
Response schema for pull request code review.
"""

from backend.schemas.review_analytics import ReviewAnalytics
from backend.schemas.review_common import (
    QualityResponse,
    ReviewIssue,
)
from backend.schemas.review_recommendations import (
    ReviewRecommendations,
)
from backend.schemas.review_statistics import ReviewStatistics
from pydantic import BaseModel


class PullRequestReviewResponse(BaseModel):
    """Complete pull request review response."""

    quality: QualityResponse
    statistics: ReviewStatistics
    analytics: ReviewAnalytics
    recommendations: ReviewRecommendations
    summary: str
    issues: list[ReviewIssue]