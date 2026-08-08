from unittest.mock import MagicMock

from backend.services.providers.gemini_provider import (
    GeminiProvider,
)


def create_provider():
    provider = GeminiProvider.__new__(GeminiProvider)
    provider.client = MagicMock()

    return provider


def test_gemini_provider_name():
    provider = create_provider()

    assert provider.provider_name == "Gemini"


def test_gemini_empty_response():
    provider = create_provider()

    provider.client.models.generate_content.return_value = None

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is False
    assert result["error"] == "EMPTY_RESPONSE"
    assert result["issues"] == []


def test_gemini_invalid_json():
    provider = create_provider()

    response = MagicMock()
    response.text = "This is not valid JSON."

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is False
    assert result["error"] == "INVALID_JSON"
    assert result["issues"] == []


def test_gemini_successful_review():
    provider = create_provider()

    response = MagicMock()
    response.text = """
    {
        "summary": "Code looks good.",
        "issues": []
    }
    """

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is True
    assert result["language"] == "Python"
    assert result["summary"] == "Code looks good."
    assert result["issues"] == []