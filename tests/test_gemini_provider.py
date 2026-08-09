import json
from unittest.mock import MagicMock, patch

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


def test_gemini_response_without_text():
    provider = create_provider()

    response = MagicMock()
    response.text = None

    provider.client.models.generate_content.return_value = response

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


def test_gemini_parses_json_markdown_code_block():
    provider = create_provider()

    response = MagicMock()
    response.text = """```json
{
    "summary": "Found one issue.",
    "issues": [
        {
            "severity": "HIGH",
            "comment": "Potential security issue."
        }
    ]
}
```"""

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "query = user_input",
        "Python",
    )

    assert result["success"] is True
    assert result["issues"][0]["confidence"] == 90
    assert result["issues"][0]["category"] == "Best Practices"


def test_gemini_parses_generic_markdown_code_block():
    provider = create_provider()

    response = MagicMock()
    response.text = """```
{
    "summary": "Found one issue.",
    "issues": []
}
```"""

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is True
    assert result["summary"] == "Found one issue."


def test_gemini_extracts_json_from_surrounding_text():
    provider = create_provider()

    response = MagicMock()
    response.text = """
Here is the review:

{
    "summary": "Code needs improvement.",
    "issues": []
}

End of review.
"""

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is True
    assert result["summary"] == "Code needs improvement."


def test_gemini_preserves_existing_confidence():
    provider = create_provider()

    response = MagicMock()
    response.text = json.dumps(
        {
            "summary": "Review completed.",
            "issues": [
                {
                    "severity": "HIGH",
                    "confidence": 42,
                }
            ],
        }
    )

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    issue = result["issues"][0]

    assert issue["confidence"] == 42
    assert issue["category"] == "Best Practices"


def test_gemini_adds_confidence_for_all_severities():
    provider = create_provider()

    response = MagicMock()
    response.text = json.dumps(
        {
            "summary": "Multiple issues found.",
            "issues": [
                {"severity": "CRITICAL"},
                {"severity": "HIGH"},
                {"severity": "MEDIUM"},
                {"severity": "LOW"},
            ],
        }
    )

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    issues = result["issues"]

    assert issues[0]["confidence"] == 95
    assert issues[1]["confidence"] == 90
    assert issues[2]["confidence"] == 75
    assert issues[3]["confidence"] == 60


def test_gemini_uses_low_confidence_for_unknown_severity():
    provider = create_provider()

    response = MagicMock()
    response.text = json.dumps(
        {
            "summary": "Review completed.",
            "issues": [
                {
                    "severity": "UNKNOWN",
                }
            ],
        }
    )

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    issue = result["issues"][0]

    assert issue["confidence"] == 60
    assert issue["category"] == "Best Practices"


def test_gemini_preserves_existing_category():
    provider = create_provider()

    response = MagicMock()
    response.text = json.dumps(
        {
            "summary": "Security issue found.",
            "issues": [
                {
                    "severity": "HIGH",
                    "category": "Security",
                }
            ],
        }
    )

    provider.client.models.generate_content.return_value = response

    result = provider.review_code(
        "password = input()",
        "Python",
    )

    issue = result["issues"][0]

    assert issue["category"] == "Security"
    assert issue["confidence"] == 90


def test_gemini_handles_api_exception():
    provider = create_provider()

    provider.client.models.generate_content.side_effect = (
        RuntimeError("Gemini API failed")
    )

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is False
    assert result["error"] == "GEMINI_ERROR"
    assert result["summary"] == (
        "Failed to generate AI review using Gemini."
    )
    assert result["issues"] == []


def test_gemini_health_check_when_configured():
    provider = create_provider()

    with patch(
        "backend.services.providers.gemini_provider.settings.GEMINI_API_KEY",
        "test-key",
    ):
        assert provider.health_check() is True


def test_gemini_health_check_when_not_configured():
    provider = create_provider()

    with patch(
        "backend.services.providers.gemini_provider.settings.GEMINI_API_KEY",
        None,
    ):
        assert provider.health_check() is False


def test_gemini_returns_not_configured_when_client_missing():
    provider = GeminiProvider.__new__(GeminiProvider)
    provider.client = None

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is False
    assert result["error"] == "NOT_CONFIGURED"
    assert result["summary"] == (
        "Gemini API key is not configured."
    )
    assert result["issues"] == []