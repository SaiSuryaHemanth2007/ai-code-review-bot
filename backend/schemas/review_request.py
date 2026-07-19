"""
Request schema for code review.
"""

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    """
    Request model for AI code review.
    """

    code: str = Field(
        ...,
        min_length=1,
        description="Source code to review",
        examples=["print('Hello, World!')"],
    )

    language: str = Field(
        ...,
        description="Programming language",
        examples=["Python"],
    )