from unittest.mock import Mock

from backend.services.ai_service import AIService


def create_provider(
    name="TestProvider",
    healthy=True,
    review=None,
):
    provider = Mock()

    provider.provider_name = name
    provider.health_check.return_value = healthy

    if review is None:
        review = {
            "success": True,
            "summary": "Review completed.",
            "issues": [],
        }

    provider.review_code.return_value = review

    return provider


def test_healthy_provider_is_used():
    provider = create_provider()

    service = AIService()
    service.providers = [provider]

    result = service.review_code(
        "print('hello')",
        "python",
    )

    provider.health_check.assert_called_once()
    provider.review_code.assert_called_once()

    assert result["success"] is True
    assert result["provider"] == "TestProvider"


def test_unhealthy_provider_is_skipped():
    unhealthy = create_provider(
        name="UnhealthyProvider",
        healthy=False,
    )

    healthy = create_provider(
        name="HealthyProvider",
        healthy=True,
    )

    service = AIService()
    service.providers = [
        unhealthy,
        healthy,
    ]

    result = service.review_code(
        "print('hello')",
        "python",
    )

    unhealthy.review_code.assert_not_called()
    healthy.review_code.assert_called_once()

    assert result["success"] is True
    assert result["provider"] == "HealthyProvider"


def test_provider_failure_falls_back_to_next_provider():
    first = create_provider(
        name="FirstProvider",
        review={
            "success": False,
            "error": "RATE_LIMIT",
        },
    )

    second = create_provider(
        name="SecondProvider",
        review={
            "success": True,
            "summary": "Fallback review.",
            "issues": [],
        },
    )

    service = AIService()
    service.providers = [
        first,
        second,
    ]

    result = service.review_code(
        "print('hello')",
        "python",
    )

    first.review_code.assert_called_once()
    second.review_code.assert_called_once()

    assert result["success"] is True
    assert result["provider"] == "SecondProvider"


def test_no_healthy_provider_returns_error():
    first = create_provider(
        name="FirstProvider",
        healthy=False,
    )

    second = create_provider(
        name="SecondProvider",
        healthy=False,
    )

    service = AIService()
    service.providers = [
        first,
        second,
    ]

    result = service.review_code(
        "print('hello')",
        "python",
    )

    first.review_code.assert_not_called()
    second.review_code.assert_not_called()

    assert result["success"] is False
    assert result["error"] == "NO_HEALTHY_PROVIDER"