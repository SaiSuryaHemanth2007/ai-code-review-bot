from typing import List, Optional
from backend.schemas.review_statistics import ReviewStatistics
from backend.schemas.review_analytics import ReviewAnalytics

from pydantic import BaseModel


class ReviewIssue(BaseModel):
    file: Optional[str] = None
    line: Optional[int] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    comment: Optional[str] = None
    suggestion: Optional[str] = None

    occurrences: Optional[int] = None
    files: Optional[list[str]] = None
    confidence: Optional[int] = None


class QualityResponse(BaseModel):
    score: int
    grade: str
    stars: str


class PullRequestReviewResult(BaseModel):
    quality: QualityResponse
    summary: str
    issues: List[ReviewIssue]


class PullRequestReviewResponse(BaseModel):
    quality: QualityResponse
    statistics: ReviewStatistics
    analytics: ReviewAnalytics
    summary: str
    issues: list[ReviewIssue]