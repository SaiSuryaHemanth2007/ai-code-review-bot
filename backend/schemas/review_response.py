"""
Response schema for code review.
"""

from typing import List, Optional

from pydantic import BaseModel


class ReviewIssue(BaseModel):
    file: Optional[str] = None
    line: Optional[int] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    confidence: Optional[int] = None
    comment: Optional[str] = None
    suggestion: Optional[str] = None
    occurrences: Optional[int] = None
    files: Optional[List[str]] = None


class QualityResponse(BaseModel):
    score: int
    grade: str
    stars: str


class ReviewResult(BaseModel):
    quality: QualityResponse
    summary: str
    issues: List[ReviewIssue]


class ReviewResponse(BaseModel):
    """
    Response returned by the AI reviewer.
    """

    success: bool
    language: str
    review: ReviewResult