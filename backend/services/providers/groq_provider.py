"""
Groq AI Provider.

Implements the BaseAIProvider interface.
"""

from backend.services.groq_service import groq_service
from backend.services.providers.base_provider import (
    BaseAIProvider,
)


class GroqProvider(BaseAIProvider):
    """
    Groq implementation of BaseAIProvider.
    """

    @property
    def provider_name(self) -> str:
        return "Groq"

    def review_code(
        self,
        code: str,
        language: str,
    ) -> dict:
        """
        Delegate review generation to the existing Groq service.
        """

        return groq_service.review_code(
            code,
            language,
        )

    def health_check(self) -> bool:
        """
        Provider health check.

        Since the Groq client is initialized during startup,
        we'll assume it's healthy if initialization succeeded.
        """

        return True


groq_provider = GroqProvider()