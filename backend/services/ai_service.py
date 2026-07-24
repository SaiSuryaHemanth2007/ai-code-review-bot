"""
AI service.

Delegates AI code reviews to the configured provider.
"""

from backend.services.groq_service import groq_service


class AIService:
    """AI review service."""

    def review_code(self, code: str, language: str) -> str:
        return groq_service.review_code(code, language)


ai_service = AIService()