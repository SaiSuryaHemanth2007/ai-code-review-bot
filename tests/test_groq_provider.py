from unittest.mock import patch

from backend.services.providers.groq_provider import (
    GroqProvider,
)


def test_groq_provider_name():
    provider = GroqProvider()

    assert provider.provider_name == "Groq"


def test_groq_provider_delegates_review_to_groq_service():
    provider = GroqProvider()

    expected = {
        "success": True,
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.providers.groq_provider.groq_service.review_code",
        return_value=expected,
    ) as mock_review:

        result = provider.review_code(
            "print('hello')",
            "Python",
        )

    assert result == expected

    mock_review.assert_called_once_with(
        "print('hello')",
        "Python",
    )


def test_groq_provider_health_check_returns_true():
    provider = GroqProvider()

    assert provider.health_check() is True