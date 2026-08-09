from unittest.mock import patch

from backend.services.dashboard_service import dashboard_service


REVIEWS = [
    {
        "id": 1,
        "repository": "owner/repo-a",
        "pull_request": 10,
        "quality_score": 90,
        "provider": "Groq",
        "review_duration": 4.0,
        "total_files": 3,
        "total_issues": 2,
        "review_data": {},
        "created_at": "2026-08-01T10:00:00+00:00",
    },
    {
        "id": 2,
        "repository": "owner/repo-a",
        "pull_request": 11,
        "quality_score": 80,
        "provider": "Groq",
        "review_duration": 2.0,
        "total_files": 5,
        "total_issues": 4,
        "review_data": {},
        "created_at": "2026-08-01T12:00:00+00:00",
    },
    {
        "id": 3,
        "repository": "owner/repo-b",
        "pull_request": 20,
        "quality_score": 95,
        "provider": "Gemini",
        "review_duration": 6.0,
        "total_files": 2,
        "total_issues": 1,
        "review_data": {},
        "created_at": "2026-08-02T09:00:00+00:00",
    },
]


@patch(
    "backend.services.dashboard_service.history_db.get_statistics"
)
@patch(
    "backend.services.dashboard_service.history_db.get_all_reviews"
)
def test_get_dashboard_summary(
    mock_get_all_reviews,
    mock_get_statistics,
):
    mock_get_all_reviews.return_value = REVIEWS

    mock_get_statistics.return_value = {
        "total_reviews": 3,
        "average_score": 88.33,
        "average_duration": 4.0,
    }

    result = dashboard_service.get_dashboard_summary()

    assert result == {
        "total_reviews": 3,
        "average_quality_score": 88.33,
        "total_files_reviewed": 10,
        "total_issues_found": 7,
        "average_review_duration": 4.0,
        "repositories": 2,
        "provider_usage": {
            "Groq": 2,
            "Gemini": 1,
        },
    }


@patch(
    "backend.services.dashboard_service.history_db.get_all_reviews"
)
def test_get_quality_history(mock_get_all_reviews):
    mock_get_all_reviews.return_value = REVIEWS.copy()

    result = dashboard_service.get_quality_history()

    assert result == {
        "quality_scores": [
            95,
            80,
            90,
        ]
    }


@patch(
    "backend.services.dashboard_service.history_db.get_all_reviews"
)
def test_get_review_trends(mock_get_all_reviews):
    mock_get_all_reviews.return_value = REVIEWS

    result = dashboard_service.get_review_trends()

    assert result == {
        "dates": [
            "2026-08-01",
            "2026-08-02",
        ],
        "review_counts": [
            2,
            1,
        ],
    }


@patch(
    "backend.services.dashboard_service.history_db.get_all_reviews"
)
def test_get_repository_statistics(mock_get_all_reviews):
    mock_get_all_reviews.return_value = REVIEWS

    result = dashboard_service.get_repository_statistics()

    assert result == {
        "repositories": [
            {
                "repository": "owner/repo-a",
                "reviews": 2,
                "average_quality": 85.0,
                "files_reviewed": 8,
                "issues_found": 6,
            },
            {
                "repository": "owner/repo-b",
                "reviews": 1,
                "average_quality": 95.0,
                "files_reviewed": 2,
                "issues_found": 1,
            },
        ]
    }


@patch(
    "backend.services.dashboard_service.history_db.get_all_reviews"
)
def test_get_provider_statistics(mock_get_all_reviews):
    mock_get_all_reviews.return_value = REVIEWS

    result = dashboard_service.get_provider_statistics()

    assert result == {
        "providers": {
            "Groq": {
                "reviews": 2,
                "average_quality": 85.0,
                "average_duration": 3.0,
            },
            "Gemini": {
                "reviews": 1,
                "average_quality": 95.0,
                "average_duration": 6.0,
            },
        }
    }


@patch(
    "backend.services.dashboard_service.history_db.get_all_reviews"
)
def test_get_leaderboard(mock_get_all_reviews):
    mock_get_all_reviews.return_value = REVIEWS

    result = dashboard_service.get_leaderboard()

    assert result == {
        "highest_quality_review": {
            "repository": "owner/repo-b",
            "pull_request": 20,
            "value": 95,
        },
        "fastest_review": {
            "repository": "owner/repo-a",
            "pull_request": 11,
            "value": 2.0,
        },
        "largest_review": {
            "repository": "owner/repo-a",
            "pull_request": 11,
            "value": 5,
        },
        "most_issues_found": {
            "repository": "owner/repo-a",
            "pull_request": 11,
            "value": 4,
        },
    }


@patch(
    "backend.services.dashboard_service.history_db.get_all_reviews"
)
def test_get_leaderboard_with_empty_data(mock_get_all_reviews):
    mock_get_all_reviews.return_value = []

    result = dashboard_service.get_leaderboard()

    empty = {
        "repository": "",
        "pull_request": 0,
        "value": 0,
    }

    assert result == {
        "highest_quality_review": empty,
        "fastest_review": empty,
        "largest_review": empty,
        "most_issues_found": empty,
    }