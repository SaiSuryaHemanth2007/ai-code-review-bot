from typing import List, Optional

from pydantic import BaseModel


class ReviewIssue(BaseModel):
    file: Optional[str] = None
    line: Optional[int] = None
    severity: Optional[str] = None
    comment: Optional[str] = None
    suggestion: Optional[str] = None


class QualityResponse(BaseModel):
    score: int
    grade: str
    stars: str


class PullRequestReviewResult(BaseModel):
    quality: QualityResponse
    summary: str
    issues: List[ReviewIssue]


class PullRequestReviewResponse(BaseModel):
    pull_request: int
    review: PullRequestReviewResult