from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_get_all_reviews():
    reviews = [
        {
            "id": 2,
            "repository": "owner/repo",
            "pull_request": 12,
            "quality_score": 92.5,
            "provider": "groq",
            "review_duration": 2.4,
            "total_files": 3,
            "total_issues": 1,
            "review_data": {
                "summary": "Good review.",
                "issues": [],
            },
            "created_at": "2026-08-09T10:00:00",
        },
        {
            "id": 1,
            "repository": "owner/repo",
            "pull_request": 10,
            "quality_score": 85.0,
            "provider": "gemini",
            "review_duration": 3.1,
            "total_files": 2,
            "total_issues": 2,
            "review_data": {
                "summary": "Some issues found.",
                "issues": [],
            },
            "created_at": "2026-08-09T09:00:00",
        },
    ]

    with patch(
        "backend.api.routes.history.history_service.get_all_reviews",
        return_value=reviews,
    ) as mock_get_all:

        response = client.get(
            "/api/v1/history"
        )

    assert response.status_code == 200
    assert response.json() == reviews

    mock_get_all.assert_called_once()


def test_get_all_reviews_returns_empty_list():
    with patch(
        "backend.api.routes.history.history_service.get_all_reviews",
        return_value=[],
    ) as mock_get_all:

        response = client.get(
            "/api/v1/history"
        )

    assert response.status_code == 200
    assert response.json() == []

    mock_get_all.assert_called_once()


def test_get_review():
    review = {
        "id": 42,
        "repository": "owner/repo",
        "pull_request": 42,
        "quality_score": 95.0,
        "provider": "groq",
        "review_duration": 2.1,
        "total_files": 4,
        "total_issues": 0,
        "review_data": {
            "summary": "Excellent code.",
            "issues": [],
        },
        "created_at": "2026-08-09T10:00:00",
    }

    with patch(
        "backend.api.routes.history.history_service.get_review",
        return_value=review,
    ) as mock_get_review:

        response = client.get(
            "/api/v1/history/42"
        )

    assert response.status_code == 200
    assert response.json() == review

    mock_get_review.assert_called_once_with(42)


def test_get_review_returns_404_for_missing_review():
    with patch(
        "backend.api.routes.history.history_service.get_review",
        return_value=None,
    ) as mock_get_review:

        response = client.get(
            "/api/v1/history/999"
        )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == "Review not found"

    mock_get_review.assert_called_once_with(999)


def test_get_review_rejects_invalid_review_id():
    response = client.get(
        "/api/v1/history/not-a-number"
    )

    assert response.status_code == 422


def test_delete_review():
    with patch(
        "backend.api.routes.history.history_service.delete_review",
        return_value=True,
    ) as mock_delete:

        response = client.delete(
            "/api/v1/history/42"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Review deleted successfully"
    )

    mock_delete.assert_called_once_with(42)


def test_delete_review_returns_404_for_missing_review():
    with patch(
        "backend.api.routes.history.history_service.delete_review",
        return_value=False,
    ) as mock_delete:

        response = client.delete(
            "/api/v1/history/999"
        )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == "Review not found"

    mock_delete.assert_called_once_with(999)


def test_get_review_statistics():
    statistics = {
        "total_reviews": 10,
        "average_score": 87.5,
        "highest_score": 100,
        "lowest_score": 65,
        "average_duration": 3.42,
        "most_used_provider": "groq",
    }

    with patch(
        "backend.api.routes.history.history_service.get_statistics",
        return_value=statistics,
    ) as mock_get_statistics:

        response = client.get(
            "/api/v1/history/statistics"
        )

    assert response.status_code == 200
    assert response.json() == statistics

    mock_get_statistics.assert_called_once()