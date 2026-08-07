"""
Groq AI Provider.

Implements the BaseAIProvider interface.
"""

from backend.core.logger import logger
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
        Delegate review generation to the Groq service.
        """

        logger.debug(
            "Using Groq provider."
        )

        return groq_service.review_code(
            code,
            language,
        )

    def health_check(self) -> bool:
        """
        Provider health check.

        The Groq service is initialized during startup.
        Future implementations can perform an API health
        check here if needed.
        """

        return True


groq_provider = GroqProvider()