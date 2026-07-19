"""
Response schema for code review.
"""

from pydantic import BaseModel


class ReviewResponse(BaseModel):
    """
    Response returned by the AI reviewer.
    """

    success: bool
    language: str
    review: str