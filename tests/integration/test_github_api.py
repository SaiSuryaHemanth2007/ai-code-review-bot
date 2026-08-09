from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_get_cache_statistics():
    statistics = {
        "hits": 10,
        "misses": 5,
        "total_requests": 15,
        "hit_rate": 66.67,
    }

    with patch(
        "backend.api.routes.github.get_cache_statistics",
        return_value=statistics,
    ) as mock_get_cache:

        response = client.get(
            "/api/v1/github/cache"
        )

    assert response.status_code == 200
    assert response.json() == statistics

    mock_get_cache.assert_called_once()


def test_debug_endpoint_returns_environment_information():
    with patch(
        "backend.api.routes.github.settings.DEBUG",
        True,
    ), patch(
        "backend.api.routes.github.settings.GITHUB_TOKEN",
        "test-token",
    ), patch(
        "backend.api.routes.github.settings.GITHUB_OWNER",
        "test-owner",
    ), patch(
        "backend.api.routes.github.settings.GITHUB_REPOSITORY",
        "test-repo",
    ):

        response = client.get(
            "/api/v1/github/debug"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["github_owner"] == "test-owner"
    assert data["github_repository"] == "test-repo"

    # Secret information must not be exposed.
    assert "github_token_exists" not in data
    assert "github_token_length" not in data


def test_debug_endpoint_returns_404_when_debug_disabled():
    with patch(
        "backend.api.routes.github.settings.DEBUG",
        False,
    ):

        response = client.get(
            "/api/v1/github/debug"
        )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == "Not Found"


def test_whoami_returns_authenticated_user():
    mock_user = type(
        "MockUser",
        (),
        {
            "login": "test-user",
            "id": 12345,
        },
    )()

    mock_github = type(
        "MockGithub",
        (),
        {
            "get_user": lambda self: mock_user,
        },
    )()

    with patch(
        "backend.api.routes.github.settings.DEBUG",
        True,
    ), patch(
        "backend.api.routes.github.github_service.github",
        mock_github,
    ):

        response = client.get(
            "/api/v1/github/whoami"
        )

    assert response.status_code == 200
    assert response.json() == {
        "login": "test-user",
        "id": 12345,
    }


def test_whoami_returns_404_when_debug_disabled():
    with patch(
        "backend.api.routes.github.settings.DEBUG",
        False,
    ):

        response = client.get(
            "/api/v1/github/whoami"
        )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == "Not Found"


def test_whoami_returns_503_when_github_client_unavailable():
    with patch(
        "backend.api.routes.github.settings.DEBUG",
        True,
    ), patch(
        "backend.api.routes.github.github_service.github",
        None,
    ):

        response = client.get(
            "/api/v1/github/whoami"
        )

    assert response.status_code == 503

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == (
        "GitHub client is unavailable."
    )


def test_get_repository_information():
    repository = {
        "name": "ai-code-review-bot",
        "owner": "test-owner",
        "description": "AI code review bot",
        "default_branch": "main",
        "stars": 25,
        "open_pull_requests": 3,
    }

    with patch(
        "backend.api.routes.github.github_service.get_repository_info",
        return_value=repository,
    ) as mock_get_repository_info:

        response = client.get(
            "/api/v1/github/repository"
        )

    assert response.status_code == 200
    assert response.json() == repository

    mock_get_repository_info.assert_called_once()


def test_list_open_pull_requests():
    pull_requests = [
        {
            "number": 42,
            "title": "Add authentication",
            "author": "developer",
            "state": "open",
        },
        {
            "number": 43,
            "title": "Improve caching",
            "author": "developer2",
            "state": "open",
        },
    ]

    with patch(
        "backend.api.routes.github.github_service.get_pull_requests",
        return_value=pull_requests,
    ) as mock_get_pull_requests:

        response = client.get(
            "/api/v1/github/pulls"
        )

    assert response.status_code == 200
    assert response.json() == pull_requests

    mock_get_pull_requests.assert_called_once()


def test_get_pull_request_files():
    files = [
        {
            "filename": "backend/main.py",
            "status": "modified",
            "additions": 10,
            "deletions": 2,
            "changes": 12,
            "patch": "@@ -1,5 +1,13 @@",
            "blob_url": "https://github.com/test/blob/main/backend/main.py",
            "raw_url": "https://github.com/test/raw/main/backend/main.py",
            "contents_url": "https://api.github.com/test",
        }
    ]

    with patch(
        "backend.api.routes.github.github_service.get_pull_request_files",
        return_value=files,
    ) as mock_get_files:

        response = client.get(
            "/api/v1/github/pulls/42/files"
        )

    assert response.status_code == 200
    assert response.json() == files

    mock_get_files.assert_called_once_with(42)


def test_review_pull_request():
    review = {
        "summary": "Code looks good.",

        "quality": {
            "score": 92,
            "grade": "A",
            "stars": "★★★★★",
        },

        "statistics": {
            "review_duration_seconds": 3.42,
            "files_reviewed": 2,
            "files_skipped": 0,
            "ai_requests": 2,
            "ai_failures": 0,
            "cache_hits": 0,
            "cache_misses": 2,
            "cache_hit_rate": 0.0,
            "cache_size": 0,
            "total_issues": 1,
            "critical": 0,
            "high": 1,
            "medium": 0,
            "low": 0,
            "average_issues_per_file": 0.5,
        },

        "analytics": {
            "issues_by_category": {
                "Correctness": 1,
            },
            "issues_by_severity": {
                "HIGH": 1,
            },
            "average_confidence": 90.0,
            "highest_confidence": 90,
            "lowest_confidence": 90,
            "most_common_category": "Correctness",
            "most_common_severity": "HIGH",
        },

        "recommendations": {
            "recommendations": [
                "Review the high-severity issue.",
            ],
        },

        "issues": [],
    }

    with patch(
        "backend.api.routes.github.review_service.review_pull_request",
        return_value=review,
    ) as mock_review:

        response = client.post(
            "/api/v1/github/pulls/42/review"
        )

    assert response.status_code == 200
    assert response.json() == review

    mock_review.assert_called_once_with(42)