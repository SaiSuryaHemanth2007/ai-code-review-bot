from unittest.mock import patch

from backend.services.history_service import HistoryService


def test_save_review_delegates_to_history_db():
    service = HistoryService()

    review_data = {
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.services.history_service.history_db.save_review",
        return_value=42,
    ) as mock_save:

        result = service.save_review(
            repository="owner/repo",
            pull_request=123,
            quality_score=95.0,
            provider="Groq",
            review_duration=12.5,
            total_files=3,
            total_issues=2,
            review_data=review_data,
        )

    assert result == 42

    mock_save.assert_called_once_with(
        repository="owner/repo",
        pull_request=123,
        quality_score=95.0,
        provider="Groq",
        review_duration=12.5,
        total_files=3,
        total_issues=2,
        review_data=review_data,
    )


def test_get_all_reviews_delegates_to_history_db():
    service = HistoryService()

    expected = [
        {
            "id": 1,
            "repository": "owner/repo",
        }
    ]

    with patch(
        "backend.services.history_service.history_db.get_all_reviews",
        return_value=expected,
    ) as mock_get_all:

        result = service.get_all_reviews()

    assert result == expected
    mock_get_all.assert_called_once_with()


def test_get_review_delegates_to_history_db():
    service = HistoryService()

    expected = {
        "id": 10,
        "repository": "owner/repo",
    }

    with patch(
        "backend.services.history_service.history_db.get_review",
        return_value=expected,
    ) as mock_get:

        result = service.get_review(10)

    assert result == expected
    mock_get.assert_called_once_with(10)


def test_delete_review_delegates_to_history_db():
    service = HistoryService()

    with patch(
        "backend.services.history_service.history_db.delete_review",
        return_value=True,
    ) as mock_delete:

        result = service.delete_review(10)

    assert result is True
    mock_delete.assert_called_once_with(10)


def test_get_statistics_delegates_to_history_db():
    service = HistoryService()

    expected = {
        "total_reviews": 10,
        "average_quality_score": 92.5,
    }

    with patch(
        "backend.services.history_service.history_db.get_statistics",
        return_value=expected,
    ) as mock_statistics:

        result = service.get_statistics()

    assert result == expected
    mock_statistics.assert_called_once_with()