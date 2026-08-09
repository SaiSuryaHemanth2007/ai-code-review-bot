from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_get_dashboard_summary():
    dashboard = {
        "total_reviews": 10,
        "average_quality_score": 87.5,
        "total_files_reviewed": 42,
        "total_issues_found": 18,
        "average_review_duration": 3.42,
        "repositories": 3,
        "provider_usage": {
            "groq": 7,
            "gemini": 3,
        },
    }

    with patch(
        "backend.api.routes.dashboard.dashboard_service.get_dashboard_summary",
        return_value=dashboard,
    ) as mock_get_dashboard:

        response = client.get(
            "/api/v1/dashboard"
        )

    assert response.status_code == 200
    assert response.json() == dashboard

    mock_get_dashboard.assert_called_once()


def test_get_quality_history():
    quality_history = {
        "quality_scores": [
            95.0,
            87.5,
            91.0,
            78.5,
        ],
    }

    with patch(
        "backend.api.routes.dashboard.dashboard_service.get_quality_history",
        return_value=quality_history,
    ) as mock_get_quality_history:

        response = client.get(
            "/api/v1/dashboard/quality-history"
        )

    assert response.status_code == 200
    assert response.json() == quality_history

    mock_get_quality_history.assert_called_once()


def test_get_review_trends():
    trends = {
        "dates": [
            "2026-08-07",
            "2026-08-08",
            "2026-08-09",
        ],
        "review_counts": [
            3,
            5,
            2,
        ],
    }

    with patch(
        "backend.api.routes.dashboard.dashboard_service.get_review_trends",
        return_value=trends,
    ) as mock_get_review_trends:

        response = client.get(
            "/api/v1/dashboard/trends"
        )

    assert response.status_code == 200
    assert response.json() == trends

    mock_get_review_trends.assert_called_once()


def test_get_repository_statistics():
    repositories = {
        "repositories": [
            {
                "repository": "owner/repo-one",
                "reviews": 5,
                "average_quality": 91.2,
                "files_reviewed": 20,
                "issues_found": 7,
            },
            {
                "repository": "owner/repo-two",
                "reviews": 3,
                "average_quality": 84.5,
                "files_reviewed": 12,
                "issues_found": 5,
            },
        ],
    }

    with patch(
        "backend.api.routes.dashboard.dashboard_service.get_repository_statistics",
        return_value=repositories,
    ) as mock_get_repository_statistics:

        response = client.get(
            "/api/v1/dashboard/repositories"
        )

    assert response.status_code == 200
    assert response.json() == repositories

    mock_get_repository_statistics.assert_called_once()


def test_get_provider_statistics():
    providers = {
        "providers": {
            "groq": {
                "reviews": 7,
                "average_quality": 89.4,
                "average_duration": 2.85,
            },
            "gemini": {
                "reviews": 3,
                "average_quality": 84.9,
                "average_duration": 4.17,
            },
        },
    }

    with patch(
        "backend.api.routes.dashboard.dashboard_service.get_provider_statistics",
        return_value=providers,
    ) as mock_get_provider_statistics:

        response = client.get(
            "/api/v1/dashboard/providers"
        )

    assert response.status_code == 200
    assert response.json() == providers

    mock_get_provider_statistics.assert_called_once()


def test_get_leaderboard():
    leaderboard = {
        "highest_quality_review": {
            "repository": "owner/best-repo",
            "pull_request": 42,
            "value": 99.5,
        },
        "fastest_review": {
            "repository": "owner/fast-repo",
            "pull_request": 17,
            "value": 1.25,
        },
        "largest_review": {
            "repository": "owner/large-repo",
            "pull_request": 31,
            "value": 48,
        },
        "most_issues_found": {
            "repository": "owner/issues-repo",
            "pull_request": 29,
            "value": 16,
        },
    }

    with patch(
        "backend.api.routes.dashboard.dashboard_service.get_leaderboard",
        return_value=leaderboard,
    ) as mock_get_leaderboard:

        response = client.get(
            "/api/v1/dashboard/leaderboard"
        )

    assert response.status_code == 200
    assert response.json() == leaderboard

    mock_get_leaderboard.assert_called_once()


def test_get_leaderboard_with_empty_data():
    empty_leaderboard = {
        "highest_quality_review": {
            "repository": "",
            "pull_request": 0,
            "value": 0,
        },
        "fastest_review": {
            "repository": "",
            "pull_request": 0,
            "value": 0,
        },
        "largest_review": {
            "repository": "",
            "pull_request": 0,
            "value": 0,
        },
        "most_issues_found": {
            "repository": "",
            "pull_request": 0,
            "value": 0,
        },
    }

    with patch(
        "backend.api.routes.dashboard.dashboard_service.get_leaderboard",
        return_value=empty_leaderboard,
    ) as mock_get_leaderboard:

        response = client.get(
            "/api/v1/dashboard/leaderboard"
        )

    assert response.status_code == 200
    assert response.json() == empty_leaderboard

    mock_get_leaderboard.assert_called_once()