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
        summary: str,
    ) -> dict:
        """
        Return a standardized AI service error response.
        """

        return {
            "success": False,
            "error": error,
            "summary": summary,
            "issues": [],
        }

    def _execute_review(
        self,
        content: str,
        language: str,
    ) -> dict:
        """
        Execute a review using the configured providers.

        Automatically falls back to the next provider
        when a provider is unavailable, reaches its
        rate limit, or fails.
        """

        if not self.providers:
            return self._error_response(
                "NO_PROVIDER_AVAILABLE",
                "No AI provider is currently available.",
            )

        last_response = None

        for provider in self.providers:

            logger.info(
                "Trying AI Provider: %s",
                provider.provider_name,
            )

            # Check provider availability before making
            # an AI request.
            try:

                if not provider.health_check():

                    logger.warning(
                        "Provider %s is unhealthy. Skipping.",
                        provider.provider_name,
                    )

                    last_response = self._error_response(
                        "PROVIDER_UNAVAILABLE",
                        (
                            f"{provider.provider_name} "
                            "provider is currently unavailable."
                        ),
                    )

                    continue

            except Exception:

                logger.exception(
                    "Health check failed for provider %s.",
                    provider.provider_name,
                )

                last_response = self._error_response(
                    "HEALTH_CHECK_FAILED",
                    (
                        f"{provider.provider_name} "
                        "provider health check failed."
                    ),
                )

                continue

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
                    (
                        f"{provider.provider_name} "
                        "provider raised an unexpected exception."
                    ),
                )

            if not isinstance(
                review,
                dict,
            ):
                review = self._error_response(
                    "INVALID_RESPONSE",
                    (
                        f"{provider.provider_name} "
                        "returned an invalid response."
                    ),
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

            if review.get("error") != "RATE_LIMIT":
                break

        if last_response is not None:
            return last_response

        return self._error_response(
            "ALL_PROVIDERS_FAILED",
            "All configured AI providers failed.",
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

    def available_providers(self):
        """
        Return provider names.
        """

        return [
            provider.provider_name
            for provider in self.providers
        ]


ai_service = AIService()