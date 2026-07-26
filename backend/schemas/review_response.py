"""
Response schema for code review.
"""

from typing import List, Optional

from pydantic import BaseModel


class ReviewIssue(BaseModel):
    file: Optional[str]
    line: Optional[int]
    severity: Optional[str]
    comment: Optional[str]
    suggestion: Optional[str]


class ReviewResult(BaseModel):
    summary: str
    issues: List[ReviewIssue]


class ReviewResponse(BaseModel):
    """
    Response returned by the AI reviewer.
    """

    success: bool
    language: str
    review: ReviewResult