"""
Response schema for code review.
"""

from pydantic import BaseModel

from backend.schemas.review_common import (
    QualityResponse,
    ReviewIssue,
)


class ReviewResult(BaseModel):
    """Represents the core AI review result."""

    quality: QualityResponse
    summary: str
    issues: list[ReviewIssue]


class ReviewResponse(BaseModel):
    """Response returned by the AI reviewer."""

    success: bool
    language: str
    review: ReviewResult