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

    def _execute_review(
        self,
        content: str,
        language: str,
    ) -> dict:
        """
        Execute a review using the configured providers.

        Automatically falls back to the next provider
        when a provider reaches its rate limit or fails.
        """

        if not self.providers:
            return {
                "success": False,
                "error": "NO_PROVIDER_AVAILABLE",
            }

        last_response = None

        for provider in self.providers:

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

                review = {
                    "success": False,
                    "error": "PROVIDER_EXCEPTION",
                }

            if not isinstance(
                review,
                dict,
            ):
                review = {
                    "success": False,
                    "error": "INVALID_RESPONSE",
                }

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

        return last_response

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