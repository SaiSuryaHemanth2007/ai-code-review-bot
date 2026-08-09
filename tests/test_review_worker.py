from unittest.mock import patch

import pytest

from backend.jobs.review_worker import review_worker


def test_run_review_completes_job_successfully():
    job_id = "test-job-123"
    pull_number = 42

    review_result = {
        "quality": {
            "score": 92,
            "grade": "A",
            "stars": "★★★★★",
        },
        "summary": "Code looks good.",
        "issues": [],
    }

    with patch(
        "backend.jobs.review_worker.job_manager.start_job"
    ) as mock_start_job, patch(
        "backend.jobs.review_worker.job_manager.update_progress"
    ) as mock_update_progress, patch(
        "backend.jobs.review_worker.review_service.review_pull_request",
        return_value=review_result,
    ) as mock_review, patch(
        "backend.jobs.review_worker.job_manager.complete_job"
    ) as mock_complete_job, patch(
        "backend.jobs.review_worker.job_manager.fail_job"
    ) as mock_fail_job:

        result = review_worker.run_review(
            job_id,
            pull_number,
        )

    assert result is None

    mock_start_job.assert_called_once_with(
        job_id
    )

    assert mock_update_progress.call_count == 2

    mock_update_progress.assert_any_call(
        job_id,
        10,
    )

    mock_update_progress.assert_any_call(
        job_id,
        90,
    )

    mock_review.assert_called_once_with(
        pull_number
    )

    mock_complete_job.assert_called_once_with(
        job_id,
        review_result,
    )

    mock_fail_job.assert_not_called()


def test_run_review_handles_review_failure():
    job_id = "test-job-456"
    pull_number = 99

    review_error = RuntimeError(
        "Review service failed."
    )

    with patch(
        "backend.jobs.review_worker.job_manager.start_job"
    ) as mock_start_job, patch(
        "backend.jobs.review_worker.job_manager.update_progress"
    ) as mock_update_progress, patch(
        "backend.jobs.review_worker.review_service.review_pull_request",
        side_effect=review_error,
    ) as mock_review, patch(
        "backend.jobs.review_worker.job_manager.complete_job"
    ) as mock_complete_job, patch(
        "backend.jobs.review_worker.job_manager.fail_job"
    ) as mock_fail_job:

        with pytest.raises(
            RuntimeError,
            match="Review service failed.",
        ):
            review_worker.run_review(
                job_id,
                pull_number,
            )

    mock_start_job.assert_called_once_with(
        job_id
    )

    mock_update_progress.assert_called_once_with(
        job_id,
        10,
    )

    mock_review.assert_called_once_with(
        pull_number
    )

    mock_complete_job.assert_not_called()

    mock_fail_job.assert_called_once_with(
        job_id,
        "Review execution failed.",
    )


def test_run_review_does_not_complete_job_when_review_fails():
    job_id = "test-job-789"
    pull_number = 123

    with patch(
        "backend.jobs.review_worker.review_service.review_pull_request",
        side_effect=Exception("AI provider failure"),
    ), patch(
        "backend.jobs.review_worker.job_manager.complete_job"
    ) as mock_complete_job, patch(
        "backend.jobs.review_worker.job_manager.fail_job"
    ) as mock_fail_job:

        with pytest.raises(
            Exception,
            match="AI provider failure",
        ):
            review_worker.run_review(
                job_id,
                pull_number,
            )

    mock_complete_job.assert_not_called()

    mock_fail_job.assert_called_once_with(
        job_id,
        "Review execution failed.",
    )