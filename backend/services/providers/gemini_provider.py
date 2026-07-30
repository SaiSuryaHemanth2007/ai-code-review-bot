"""
Gemini AI Provider.

Implements the BaseAIProvider interface.
"""

from backend.services.providers.base_provider import (
    BaseAIProvider,
)


class GeminiProvider(BaseAIProvider):
    """
    Gemini implementation of BaseAIProvider.

    This is a placeholder implementation.
    Replace review_code() with the Gemini SDK call.
    """

    @property
    def provider_name(self) -> str:
        return "Gemini"

    def review_code(
        self,
        code: str,
        language: str,
    ) -> dict:
        """
        Review code using Gemini.

        TODO:
        Replace this placeholder with the Gemini API.
        """

        return {
            "success": False,
            "error": "NOT_IMPLEMENTED",
            "summary": (
                "Gemini provider has not been configured."
            ),
            "issues": [],
        }

    def health_check(self) -> bool:
        """
        Health check.
        """

        return True


gemini_provider = GeminiProvider()