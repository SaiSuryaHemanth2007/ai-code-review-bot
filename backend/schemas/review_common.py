"""
Shared schemas for code review responses.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    """Represents a single issue identified during code review."""

    file: Optional[str] = None
    line: Optional[int] = Field(default=None, ge=1)
    severity: Optional[str] = None
    category: Optional[str] = None
    confidence: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )
    comment: Optional[str] = None
    suggestion: Optional[str] = None
    occurrences: Optional[int] = Field(
        default=None,
        ge=1,
    )
    files: Optional[list[str]] = None


class QualityResponse(BaseModel):
    """Represents the overall review quality score."""

    score: int = Field(ge=0, le=100)
    grade: str
    stars: str