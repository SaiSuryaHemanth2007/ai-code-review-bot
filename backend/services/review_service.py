"""
Business logic for code reviews.
"""

from backend.services.ai_service import ai_service


class ReviewService:
    """Coordinates the code review process."""

    def review(self, code: str, language: str) -> str:
        return ai_service.review_code(code, language)


review_service = ReviewService()