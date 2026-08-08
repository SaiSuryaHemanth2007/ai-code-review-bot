from backend.services.review_service import ReviewService
from unittest.mock import patch

from backend.services.review_service import ReviewService


def test_review_file_calls_ai_on_cache_miss():
    service = ReviewService()

    review = {
        "success": True,
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.get_cached_review",
        return_value=None,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
        return_value=review,
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ) as mock_store:

        result = service.review_file(
            "main.py",
            "print('hello')",
            "Python",
        )

    mock_review.assert_called_once_with(
        "print('hello')",
        "Python",
    )

    mock_store.assert_called_once()

    assert result == {
        "filename": "main.py",
        "review": review,
    }


def test_review_file_uses_cached_review_without_ai_call():
    service = ReviewService()

    review = {
        "success": True,
        "summary": "Cached review.",
        "issues": [],
    }

    with patch(
        "backend.services.review_service.get_cached_review",
        return_value=review,
    ), patch(
        "backend.services.review_service.ai_service.review_code",
    ) as mock_review, patch(
        "backend.services.review_service.store_review",
    ) as mock_store:

        result = service.review_file(
            "main.py",
            "print('hello')",
            "Python",
        )

    mock_review.assert_not_called()
    mock_store.assert_not_called()

    assert result == {
        "filename": "main.py",
        "review": review,
    }

def test_filters_builtin_sum_function_false_positive():
    service = ReviewService()

    issue = {
        "category": "Performance",
        "comment": "This function could be simplified using the built-in sum function.",
    }

    assert service._is_false_positive_issue(issue) is True


def test_filters_timing_attack_false_positive():
    service = ReviewService()

    issue = {
        "category": "Security",
        "comment": "The password comparison is vulnerable to timing attacks.",
    }

    assert service._is_false_positive_issue(issue) is True


def test_filters_small_helper_duplication_false_positive():
    service = ReviewService()

    issue = {
        "category": "Maintainability",
        "comment": (
            "The find_user, find_admin, find_moderator, and "
            "find_reviewer functions contain duplicated logic."
        ),
    }

    assert service._is_false_positive_issue(issue) is True

def test_filters_calculate_average_sum_suggestion_false_positive():
    service = ReviewService()

    issue = {
        "category": "Performance",
        "comment": (
            "The calculate_average function can be simplified "
            "using the built-in sum function."
        ),
    }

    assert service._is_false_positive_issue(issue) is True


def test_filters_get_delete_search_helper_duplication_false_positive():
    service = ReviewService()

    issue = {
        "category": "Maintainability",
        "comment": (
            "The get_user, delete_user, and search_user functions "
            "have similar structures and could be refactored "
            "for better maintainability."
        ),
    }

    assert service._is_false_positive_issue(issue) is True