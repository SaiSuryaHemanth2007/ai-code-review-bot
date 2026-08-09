import json
from unittest.mock import MagicMock, patch

import pytest
from groq import RateLimitError

from backend.services.groq_service import GroqService


@pytest.fixture
def service():
    with patch(
        "backend.services.groq_service.Groq"
    ):
        return GroqService()


def make_response(content):
    response = MagicMock()

    response.choices = [
        MagicMock(
            message=MagicMock(
                content=content
            )
        )
    ]

    return response


def test_review_prompt_contains_sql_injection_safety_rules(
    service,
):
    prompt = service._build_prompt(
        """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return query, (user_id,)
""",
        "Python",
    )

    assert (
        "Do NOT report SQL injection when user-controlled values "
        "are safely passed through parameterized queries"
        in prompt
    )

    assert (
        "Report SQL injection only when untrusted input is directly "
        "concatenated, interpolated, or formatted into an SQL statement"
        " without parameterization"
        in prompt
    )


def test_error_response_returns_standard_structure(
    service,
):
    result = service._error_response(
        "TEST_ERROR",
        "Something went wrong.",
    )

    assert result == {
        "success": False,
        "error": "TEST_ERROR",
        "summary": "Something went wrong.",
        "issues": [],
    }


def test_build_prompt_replaces_all_placeholders(
    service,
):
    prompt = service._build_prompt(
        "print('hello')",
        "Python",
    )

    assert "{language}" not in prompt
    assert "{rules}" not in prompt
    assert "{repository_context}" not in prompt
    assert "{code}" not in prompt

    assert "Python" in prompt
    assert "print('hello')" in prompt


def test_review_code_returns_successful_review(
    service,
):
    review = {
        "issues": [
            {
                "severity": "HIGH",
                "comment": "Potential issue.",
                "confidence": 95,
                "category": "Security",
            }
        ],
        "summary": "One issue found.",
    }

    response = make_response(
        json.dumps(review)
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "dangerous_code()",
        "Python",
    )

    assert result["success"] is True
    assert result["summary"] == (
        "One issue found."
    )
    assert result["issues"][0]["confidence"] == 95
    assert result["issues"][0]["category"] == "Security"


def test_review_code_parses_markdown_json(
    service,
):
    review = {
        "issues": [],
        "summary": "No issues found.",
    }

    response = make_response(
        "```json\n"
        + json.dumps(review)
        + "\n```"
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is True
    assert result["issues"] == []
    assert result["summary"] == (
        "No issues found."
    )


def test_review_code_extracts_json_from_extra_text(
    service,
):
    review = {
        "issues": [],
        "summary": "Clean code.",
    }

    response = make_response(
        "Here is the review:\n"
        + json.dumps(review)
        + "\nEnd of review."
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is True
    assert result["summary"] == "Clean code."


def test_review_code_adds_confidence_from_severity(
    service,
):
    review = {
        "issues": [
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
            {"severity": "MEDIUM"},
            {"severity": "LOW"},
        ]
    }

    response = make_response(
        json.dumps(review)
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "some_code()",
        "Python",
    )

    issues = result["issues"]

    assert issues[0]["confidence"] == 95
    assert issues[1]["confidence"] == 90
    assert issues[2]["confidence"] == 75
    assert issues[3]["confidence"] == 60


def test_review_code_uses_default_confidence_for_unknown_severity(
    service,
):
    review = {
        "issues": [
            {"severity": "UNKNOWN"},
        ]
    }

    response = make_response(
        json.dumps(review)
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "some_code()",
        "Python",
    )

    assert result["issues"][0]["confidence"] == 60


def test_review_code_adds_default_category(
    service,
):
    review = {
        "issues": [
            {"severity": "HIGH"},
        ]
    }

    response = make_response(
        json.dumps(review)
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "some_code()",
        "Python",
    )

    assert result["issues"][0]["category"] == (
        "Best Practices"
    )


def test_review_code_returns_empty_response_error(
    service,
):
    response = MagicMock()
    response.choices = []

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "print('hello')",
        "Python",
    )

    assert result == {
        "success": False,
        "error": "EMPTY_RESPONSE",
        "summary": "Groq returned an empty response.",
        "issues": [],
    }


def test_review_code_returns_empty_content_error(
    service,
):
    response = make_response(None)

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is False
    assert result["error"] == "EMPTY_RESPONSE"


def test_review_code_handles_invalid_json(
    service,
):
    response = make_response(
        "this is not valid json"
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    result = service.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is False
    assert result["error"] == "INVALID_JSON"
    assert result["issues"] == []


def test_review_code_handles_rate_limit(
    service,
):
    service.client.chat.completions.create.side_effect = (
        RateLimitError(
            "Rate limit exceeded",
            response=MagicMock(),
            body=None,
        )
    )

    result = service.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is False
    assert result["error"] == "RATE_LIMIT"
    assert result["issues"] == []


def test_review_code_retries_after_general_exception(
    service,
):
    response = make_response(
        json.dumps(
            {
                "issues": [],
                "summary": "Recovered after retry.",
            }
        )
    )

    service.client.chat.completions.create.side_effect = [
        Exception("Temporary failure"),
        response,
    ]

    with patch(
        "backend.services.groq_service.time.sleep"
    ) as mock_sleep:

        result = service.review_code(
            "print('hello')",
            "Python",
        )

    assert result["success"] is True
    assert result["summary"] == (
        "Recovered after retry."
    )

    assert (
        service.client.chat.completions.create.call_count
        == 2
    )

    mock_sleep.assert_called_once_with(1)


def test_review_code_returns_unknown_after_all_retries_fail(
    service,
):
    service.client.chat.completions.create.side_effect = (
        Exception("Groq unavailable")
    )

    with patch(
        "backend.services.groq_service.time.sleep"
    ) as mock_sleep:

        result = service.review_code(
            "print('hello')",
            "Python",
        )

    assert result["success"] is False
    assert result["error"] == "UNKNOWN"
    assert result["summary"] == (
        "Failed to generate AI review "
        "after multiple attempts."
    )

    assert (
        service.client.chat.completions.create.call_count
        == 3
    )

    assert mock_sleep.call_count == 2
    assert mock_sleep.call_args_list[0].args == (1,)
    assert mock_sleep.call_args_list[1].args == (2,)


def test_review_code_handles_unexpected_processing_error(
    service,
):
    response = make_response(
        json.dumps(
            {
                "issues": [],
                "summary": "Valid review.",
            }
        )
    )

    service.client.chat.completions.create.return_value = (
        response
    )

    with patch(
        "backend.services.groq_service.json.loads",
        side_effect=ValueError("Unexpected error"),
    ):

        result = service.review_code(
            "print('hello')",
            "Python",
        )

    assert result["success"] is False
    assert result["error"] == "PROCESSING_ERROR"
    assert result["summary"] == (
        "Failed to generate AI review."
    )

def test_review_code_handles_generic_markdown_code_block():
    with patch("backend.services.groq_service.Groq") as mock_groq:

        service = GroqService()

        mock_response = type(
            "MockResponse",
            (),
            {
                "choices": [
                    type(
                        "MockChoice",
                        (),
                        {
                            "message": type(
                                "MockMessage",
                                (),
                                {
                                    "content": """```
{
    "issues": [],
    "summary": "Code looks good."
}
```"""
                                },
                            )(),
                        },
                    )(),
                ]
            },
        )()

        service.client.chat.completions.create.return_value = (
            mock_response
        )

        result = service.review_code(
            "print('hello')",
            "Python",
        )

        assert result["success"] is True
        assert result["issues"] == []
        assert result["summary"] == "Code looks good."