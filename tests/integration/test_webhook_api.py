from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_github_webhook_processes_pull_request():
    payload = {
        "action": "opened",
        "repository": {
            "full_name": "test-owner/test-repo",
        },
        "pull_request": {
            "number": 42,
        },
    }

    with patch(
        "backend.api.routes.webhooks.settings.DEBUG",
        True,
    ), patch(
        "backend.api.routes.webhooks.webhook_service.process_webhook",
        return_value={
            "success": True,
            "message": "Webhook processed successfully.",
            "job_id": "test-job-123",
        },
    ) as mock_process:

        response = client.post(
            "/api/v1/webhooks/github",
            headers={
                "X-GitHub-Event": "pull_request",
            },
            json=payload,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == (
        "Webhook processed successfully."
    )
    assert data["job_id"] == "test-job-123"

    mock_process.assert_called_once()

    call_kwargs = mock_process.call_args.kwargs

    assert call_kwargs["event"] == "pull_request"
    assert call_kwargs["payload"] == payload


def test_github_webhook_ignores_non_review_event():
    payload = {
        "action": "created",
    }

    with patch(
        "backend.api.routes.webhooks.settings.DEBUG",
        True,
    ), patch(
        "backend.api.routes.webhooks.webhook_service.process_webhook",
        return_value={
            "success": True,
            "message": "Event ignored.",
            "job_id": None,
        },
    ) as mock_process:

        response = client.post(
            "/api/v1/webhooks/github",
            headers={
                "X-GitHub-Event": "issues",
            },
            json=payload,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == "Event ignored."
    assert data["job_id"] is None

    mock_process.assert_called_once()


def test_github_webhook_rejects_invalid_json():
    with patch(
        "backend.api.routes.webhooks.settings.DEBUG",
        True,
    ):

        response = client.post(
            "/api/v1/webhooks/github",
            headers={
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
            content=b"not-valid-json",
        )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == (
        "Invalid or empty JSON payload."
    )


def test_github_webhook_rejects_missing_event_header():
    payload = {
        "action": "opened",
        "repository": {
            "full_name": "test-owner/test-repo",
        },
        "pull_request": {
            "number": 42,
        },
    }

    with patch(
        "backend.api.routes.webhooks.settings.DEBUG",
        True,
    ):

        response = client.post(
            "/api/v1/webhooks/github",
            json=payload,
        )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == (
        "Missing GitHub event header."
    )


def test_github_webhook_handles_service_failure():
    payload = {
        "action": "opened",
        "repository": {
            "full_name": "test-owner/test-repo",
        },
        "pull_request": {
            "number": 42,
        },
    }

    with patch(
        "backend.api.routes.webhooks.settings.DEBUG",
        True,
    ), patch(
        "backend.api.routes.webhooks.webhook_service.process_webhook",
        side_effect=Exception("Webhook service failed"),
    ):

        response = client.post(
            "/api/v1/webhooks/github",
            headers={
                "X-GitHub-Event": "pull_request",
            },
            json=payload,
        )

    assert response.status_code == 500

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == (
        "Webhook processing failed."
    )


def test_github_webhook_verifies_signature_in_production():
    payload = {
        "action": "opened",
        "repository": {
            "full_name": "test-owner/test-repo",
        },
        "pull_request": {
            "number": 42,
        },
    }

    with patch(
        "backend.api.routes.webhooks.settings.DEBUG",
        False,
    ), patch(
        "backend.api.routes.webhooks.webhook_security.verify_signature",
        new_callable=AsyncMock,
    ) as mock_verify, patch(
        "backend.api.routes.webhooks.webhook_service.process_webhook",
        return_value={
            "success": True,
            "message": "Webhook processed successfully.",
            "job_id": "test-job-123",
        },
    ):

        response = client.post(
            "/api/v1/webhooks/github",
            headers={
                "X-GitHub-Event": "pull_request",
            },
            json=payload,
        )

    assert response.status_code == 200

    mock_verify.assert_awaited_once()


def test_github_webhook_handles_signature_failure():
    payload = {
        "action": "opened",
        "repository": {
            "full_name": "test-owner/test-repo",
        },
        "pull_request": {
            "number": 42,
        },
    }

    with patch(
        "backend.api.routes.webhooks.settings.DEBUG",
        False,
    ), patch(
        "backend.api.routes.webhooks.webhook_security.verify_signature",
        new_callable=AsyncMock,
        side_effect=Exception("Invalid signature"),
    ):

        response = client.post(
            "/api/v1/webhooks/github",
            headers={
                "X-GitHub-Event": "pull_request",
            },
            json=payload,
        )

    assert response.status_code == 500

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "HTTP Error"
    assert data["message"] == (
        "Webhook processing failed."
    )