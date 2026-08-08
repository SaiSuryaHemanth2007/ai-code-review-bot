"""
AI Service.

Routes AI review requests to the configured provider.
"""

from backend.core.logger import logger
from backend.prompts.review_prompt import INLINE_REVIEW_PROMPT
from backend.services.providers.gemini_provider import (
    gemini_provider,
)
from backend.services.providers.groq_provider import (
    groq_provider,
)


class AIService:
    """
    AI Router.

    Currently supports:
    - Groq
    - Gemini

    Future:
    - OpenAI
    - Ollama
    """

    def __init__(self):
        self.providers = [
            groq_provider,
            gemini_provider,
        ]

    def _error_response(
        self,
        error: str,
        provider: str | None = None,
    ) -> dict:
        """
        Return a standardized AI service error response.
        """

        response = {
            "success": False,
            "error": error,
            "issues": [],
        }

        if provider:
            response["provider"] = provider

        return response

    def _execute_review(
        self,
        content: str,
        language: str,
    ) -> dict:
        """
        Execute a review using available providers.

        Providers are checked before execution.
        If a provider fails or reaches its rate limit,
        the router attempts the next available provider.
        """

        if not self.providers:
            logger.error(
                "No AI providers are configured."
            )

            return self._error_response(
                "NO_PROVIDER_AVAILABLE",
            )

        last_response = None

        for provider in self.providers:

            logger.info(
                "Checking AI Provider: %s",
                provider.provider_name,
            )

            try:
                if not provider.health_check():
                    logger.warning(
                        "Provider %s is unhealthy. Skipping.",
                        provider.provider_name,
                    )
                    continue

            except Exception:
                logger.exception(
                    "Health check failed for provider %s.",
                    provider.provider_name,
                )
                continue

            logger.info(
                "Trying AI Provider: %s",
                provider.provider_name,
            )

            try:

                review = provider.review_code(
                    content,
                    language,
                )

            except Exception:

                logger.exception(
                    "Provider %s raised an exception.",
                    provider.provider_name,
                )

                review = self._error_response(
                    "PROVIDER_EXCEPTION",
                    provider.provider_name,
                )

            if not isinstance(review, dict):
                review = self._error_response(
                    "INVALID_RESPONSE",
                    provider.provider_name,
                )

            review["provider"] = (
                provider.provider_name
            )

            if review.get("success"):

                logger.info(
                    "Provider succeeded: %s",
                    provider.provider_name,
                )

                return review

            logger.warning(
                "%s failed (%s)",
                provider.provider_name,
                review.get("error"),
            )

            last_response = review

        if last_response is not None:
            return last_response

        return self._error_response(
            "NO_HEALTHY_PROVIDER",
        )

    def review_code(
        self,
        code: str,
        language: str,
    ) -> dict:
        """
        Review source code.
        """

        return self._execute_review(
            code,
            language,
        )

    def review_inline(
        self,
        code: str,
        language: str,
    ) -> dict:
        """
        Generate structured inline review comments.
        """

        prompt = INLINE_REVIEW_PROMPT.format(
            code=code,
        )

        return self._execute_review(
            prompt,
            language,
        )

    def available_providers(self) -> list[str]:
        """
        Return configured provider names.
        """

        return [
            provider.provider_name
            for provider in self.providers
        ]


ai_service = AIService()