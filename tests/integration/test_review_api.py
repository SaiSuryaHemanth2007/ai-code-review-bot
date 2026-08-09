from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_review_endpoint_success():
    ai_review = {
        "success": True,
        "summary": "Code looks good.",
        "issues": [],
    }

    with patch(
        "backend.api.routes.review.review_service.review",
        return_value=ai_review,
    ):
        response = client.post(
            "/api/v1/review",
            json={
                "code": "print('Hello, World!')",
                "language": "Python",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["language"] == "Python"

    assert "review" in data
    assert data["review"]["summary"] == "Code looks good."
    assert data["review"]["issues"] == []

    assert "quality" in data["review"]
    assert "score" in data["review"]["quality"]
    assert "grade" in data["review"]["quality"]
    assert "stars" in data["review"]["quality"]


def test_review_endpoint_rejects_empty_code():
    response = client.post(
        "/api/v1/review",
        json={
            "code": "",
            "language": "Python",
        },
    )

    assert response.status_code == 422


def test_review_endpoint_rejects_missing_code():
    response = client.post(
        "/api/v1/review",
        json={
            "language": "Python",
        },
    )

    assert response.status_code == 422


def test_review_endpoint_rejects_missing_language():
    response = client.post(
        "/api/v1/review",
        json={
            "code": "print('Hello')",
        },
    )

    assert response.status_code == 422


def test_review_endpoint_handles_service_failure():
    with patch(
        "backend.api.routes.review.review_service.review",
        side_effect=Exception("AI service failed"),
    ):
        response = client.post(
            "/api/v1/review",
            json={
                "code": "print('Hello')",
                "language": "Python",
            },
        )

    assert response.status_code == 500

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == "Review failed."

def test_review_endpoint_calculates_quality_from_issues():
    ai_review = {
        "success": True,
        "summary": "Several issues found.",
        "issues": [
            {
                "severity": "CRITICAL",
                "category": "Security",
                "comment": "Critical security issue.",
                "file": "main.py",
                "line": 10,
                "confidence": 95,
            },
            {
                "severity": "HIGH",
                "category": "Correctness",
                "comment": "High severity issue.",
                "file": "main.py",
                "line": 20,
                "confidence": 90,
            },
        ],
    }

    with patch(
        "backend.api.routes.review.review_service.review",
        return_value=ai_review,
    ):
        response = client.post(
            "/api/v1/review",
            json={
                "code": "print('Hello')",
                "language": "Python",
            },
        )

    assert response.status_code == 200

    data = response.json()

    quality = data["review"]["quality"]

    assert quality["score"] < 100
    assert "grade" in quality
    assert "stars" in quality

    assert len(data["review"]["issues"]) == 2

def test_review_endpoint_passes_request_to_service():
    ai_review = {
        "success": True,
        "summary": "Review completed.",
        "issues": [],
    }

    with patch(
        "backend.api.routes.review.review_service.review",
        return_value=ai_review,
    ) as mock_review:

        response = client.post(
            "/api/v1/review",
            json={
                "code": "def hello():\n    return 'world'",
                "language": "Python",
            },
        )

    assert response.status_code == 200

    mock_review.assert_called_once_with(
        "def hello():\n    return 'world'",
        "Python",
    )

def test_start_review_creates_job():
    with patch(
        "backend.api.routes.review.settings.GITHUB_OWNER",
        "test-owner",
    ), patch(
        "backend.api.routes.review.settings.GITHUB_REPOSITORY",
        "test-repo",
    ), patch(
        "backend.api.routes.review.job_manager.create_job",
        return_value="test-job-123",
    ) as mock_create_job, patch(
        "backend.api.routes.review.review_worker.run_review",
    ) as mock_run_review:

        response = client.post(
            "/api/v1/review/start",
            params={"pull_number": 42},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Review job created successfully."
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "queued"

    mock_create_job.assert_called_once_with(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    mock_run_review.assert_called_once_with(
    "test-job-123",
    42,
)


def test_start_review_rejects_unconfigured_repository():
    with patch(
        "backend.api.routes.review.settings.GITHUB_OWNER",
        "",
    ), patch(
        "backend.api.routes.review.settings.GITHUB_REPOSITORY",
        "",
    ):

        response = client.post(
            "/api/v1/review/start",
            params={"pull_number": 42},
        )

    assert response.status_code == 500

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == (
        "GitHub repository is not configured."
    )


def test_get_all_review_jobs():
    jobs = [
        {
            "job_id": "job-1",
            "repository": "owner/repo",
            "pull_request": 10,
            "status": "queued",
            "progress": 0,
        },
        {
            "job_id": "job-2",
            "repository": "owner/repo",
            "pull_request": 11,
            "status": "completed",
            "progress": 100,
        },
    ]

    with patch(
        "backend.api.routes.review.job_manager.get_all_jobs",
        return_value=jobs,
    ) as mock_get_jobs:

        response = client.get(
            "/api/v1/review/jobs"
        )

    assert response.status_code == 200
    assert response.json() == jobs

    mock_get_jobs.assert_called_once()


def test_get_review_job():
    job = {
        "job_id": "job-123",
        "repository": "owner/repo",
        "pull_request": 42,
        "status": "running",
        "progress": 50,
        "created_at": "2026-08-09T10:00:00",
        "started_at": "2026-08-09T10:01:00",
        "completed_at": None,
        "error": None,
    }

    with patch(
        "backend.api.routes.review.job_manager.get_job",
        return_value=job,
    ) as mock_get_job:

        response = client.get(
            "/api/v1/review/jobs/job-123"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == "job-123"
    assert data["repository"] == "owner/repo"
    assert data["pull_request"] == 42
    assert data["status"] == "running"
    assert data["progress"] == 50

    mock_get_job.assert_called_once_with(
        "job-123"
    )


def test_get_review_job_returns_404_for_missing_job():
    with patch(
        "backend.api.routes.review.job_manager.get_job",
        return_value=None,
    ) as mock_get_job:

        response = client.get(
            "/api/v1/review/jobs/does-not-exist"
        )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == "Job not found."

    mock_get_job.assert_called_once_with(
        "does-not-exist"
    )
