from unittest.mock import MagicMock, patch

import pytest

from backend.services.webhook_service import WebhookService


@pytest.fixture
def service():
    return WebhookService()


def test_process_webhook_ignores_event(service):
    background_tasks = MagicMock()

    with patch(
        "backend.services.webhook_service.github_event_service.should_review",
        return_value=False,
    ) as mock_should_review:

        result = service.process_webhook(
            event="issues",
            payload={"action": "opened"},
            background_tasks=background_tasks,
        )

    assert result == {
        "success": True,
        "message": "Event ignored.",
        "job_id": None,
    }

    mock_should_review.assert_called_once_with(
        "issues",
        {"action": "opened"},
    )

    background_tasks.add_task.assert_not_called()


def test_process_webhook_processes_pull_request(
    service,
):
    background_tasks = MagicMock()

    with patch(
        "backend.services.webhook_service.github_event_service.should_review",
        return_value=True,
    ) as mock_should_review, patch(
        "backend.services.webhook_service.github_event_service.get_repository",
        return_value="test-owner/test-repo",
    ) as mock_get_repository, patch(
        "backend.services.webhook_service.github_event_service.get_pull_request_number",
        return_value=42,
    ) as mock_get_pull_number, patch(
        "backend.services.webhook_service.job_manager.create_job",
        return_value="test-job-123",
    ) as mock_create_job, patch(
        "backend.services.webhook_service.review_worker.run_review",
    ) as mock_run_review:

        result = service.process_webhook(
            event="pull_request",
            payload={
                "action": "opened",
            },
            background_tasks=background_tasks,
        )

    assert result == {
        "success": True,
        "message": "Webhook processed successfully.",
        "job_id": "test-job-123",
    }

    mock_should_review.assert_called_once_with(
        "pull_request",
        {"action": "opened"},
    )

    mock_get_repository.assert_called_once_with(
        {"action": "opened"},
    )

    mock_get_pull_number.assert_called_once_with(
        {"action": "opened"},
    )

    mock_create_job.assert_called_once_with(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    background_tasks.add_task.assert_called_once_with(
        mock_run_review,
        "test-job-123",
        42,
    )


def test_process_webhook_rejects_failed_job_creation(
    service,
):
    background_tasks = MagicMock()

    with patch(
        "backend.services.webhook_service.github_event_service.should_review",
        return_value=True,
    ), patch(
        "backend.services.webhook_service.github_event_service.get_repository",
        return_value="test-owner/test-repo",
    ), patch(
        "backend.services.webhook_service.github_event_service.get_pull_request_number",
        return_value=42,
    ), patch(
        "backend.services.webhook_service.job_manager.create_job",
        return_value=None,
    ), patch(
        "backend.services.webhook_service.logger.exception",
    ) as mock_logger:

        with pytest.raises(
            RuntimeError,
            match="Failed to create review job.",
        ):
            service.process_webhook(
                event="pull_request",
                payload={
                    "action": "opened",
                },
                background_tasks=background_tasks,
            )

    background_tasks.add_task.assert_not_called()
    mock_logger.assert_called_once_with(
        "Failed to process GitHub webhook."
    )


def test_process_webhook_handles_repository_failure(
    service,
):
    background_tasks = MagicMock()

    with patch(
        "backend.services.webhook_service.github_event_service.should_review",
        return_value=True,
    ), patch(
        "backend.services.webhook_service.github_event_service.get_repository",
        side_effect=ValueError(
            "Repository data not found."
        ),
    ), patch(
        "backend.services.webhook_service.logger.exception",
    ) as mock_logger:

        with pytest.raises(
            ValueError,
            match="Repository data not found.",
        ):
            service.process_webhook(
                event="pull_request",
                payload={
                    "action": "opened",
                },
                background_tasks=background_tasks,
            )

    mock_logger.assert_called_once_with(
        "Failed to process GitHub webhook."
    )

    background_tasks.add_task.assert_not_called()


def test_process_webhook_handles_pull_request_number_failure(
    service,
):
    background_tasks = MagicMock()

    with patch(
        "backend.services.webhook_service.github_event_service.should_review",
        return_value=True,
    ), patch(
        "backend.services.webhook_service.github_event_service.get_repository",
        return_value="test-owner/test-repo",
    ), patch(
        "backend.services.webhook_service.github_event_service.get_pull_request_number",
        side_effect=ValueError(
            "Pull request number not found."
        ),
    ), patch(
        "backend.services.webhook_service.logger.exception",
    ) as mock_logger:

        with pytest.raises(
            ValueError,
            match="Pull request number not found.",
        ):
            service.process_webhook(
                event="pull_request",
                payload={
                    "action": "opened",
                },
                background_tasks=background_tasks,
            )

    mock_logger.assert_called_once_with(
        "Failed to process GitHub webhook."
    )

    background_tasks.add_task.assert_not_called()


def test_process_webhook_handles_job_manager_exception(
    service,
):
    background_tasks = MagicMock()

    with patch(
        "backend.services.webhook_service.github_event_service.should_review",
        return_value=True,
    ), patch(
        "backend.services.webhook_service.github_event_service.get_repository",
        return_value="test-owner/test-repo",
    ), patch(
        "backend.services.webhook_service.github_event_service.get_pull_request_number",
        return_value=42,
    ), patch(
        "backend.services.webhook_service.job_manager.create_job",
        side_effect=RuntimeError(
            "Database unavailable."
        ),
    ), patch(
        "backend.services.webhook_service.logger.exception",
    ) as mock_logger:

        with pytest.raises(
            RuntimeError,
            match="Database unavailable.",
        ):
            service.process_webhook(
                event="pull_request",
                payload={
                    "action": "opened",
                },
                background_tasks=background_tasks,
            )

    mock_logger.assert_called_once_with(
        "Failed to process GitHub webhook."
    )

    background_tasks.add_task.assert_not_called()