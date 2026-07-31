"""
Base interface for AI providers.
"""

from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """
    Base class for every AI provider.

    Every provider must implement review_code().
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Human-readable provider name.
        """
        pass

    @abstractmethod
    def review_code(
        self,
        code: str,
        language: str,
    ) -> dict:
        """
        Review source code.

        Returns a standardized review dictionary.

        Example:
        {
            "success": True,
            "summary": "...",
            "issues": [...]
        }
        """
        pass

    def health_check(self) -> bool:
        """
        Optional provider health check.

        Returns True if the provider is available.
        """

        return True