from unittest.mock import patch

from backend.jobs.job_manager import JobManager


def test_create_job_creates_queued_job():
    manager = JobManager()

    with patch(
        "backend.jobs.job_manager.uuid.uuid4",
        return_value="test-job-id",
    ):
        job_id = manager.create_job(
            repository="test-owner/test-repo",
            pull_request=42,
        )

    assert job_id == "test-job-id"

    job = manager.get_job(job_id)

    assert job is not None
    assert job["job_id"] == "test-job-id"
    assert job["repository"] == "test-owner/test-repo"
    assert job["pull_request"] == 42
    assert job["status"] == "queued"
    assert job["progress"] == 0
    assert job["result"] is None
    assert job["error"] is None
    assert job["created_at"] is not None
    assert job["started_at"] is None
    assert job["completed_at"] is None


def test_start_job_marks_job_as_running():
    manager = JobManager()

    job_id = manager.create_job(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    manager.start_job(job_id)

    job = manager.get_job(job_id)

    assert job["status"] == "running"
    assert job["started_at"] is not None


def test_start_job_ignores_missing_job():
    manager = JobManager()

    manager.start_job("missing-job")

    assert manager.get_all_jobs() == []


def test_update_progress_sets_progress():
    manager = JobManager()

    job_id = manager.create_job(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    manager.update_progress(job_id, 60)

    assert manager.get_job(job_id)["progress"] == 60


def test_update_progress_clamps_to_zero():
    manager = JobManager()

    job_id = manager.create_job(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    manager.update_progress(job_id, -20)

    assert manager.get_job(job_id)["progress"] == 0


def test_update_progress_clamps_to_hundred():
    manager = JobManager()

    job_id = manager.create_job(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    manager.update_progress(job_id, 150)

    assert manager.get_job(job_id)["progress"] == 100


def test_update_progress_ignores_missing_job():
    manager = JobManager()

    manager.update_progress("missing-job", 50)

    assert manager.get_all_jobs() == []


def test_complete_job_marks_job_completed():
    manager = JobManager()

    job_id = manager.create_job(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    result = {
        "quality_score": 95,
        "issues": [],
    }

    manager.complete_job(
        job_id,
        result,
    )

    job = manager.get_job(job_id)

    assert job["status"] == "completed"
    assert job["progress"] == 100
    assert job["result"] == result
    assert job["completed_at"] is not None


def test_complete_job_ignores_missing_job():
    manager = JobManager()

    manager.complete_job(
        "missing-job",
        {"quality_score": 95},
    )

    assert manager.get_all_jobs() == []


def test_fail_job_marks_job_failed():
    manager = JobManager()

    job_id = manager.create_job(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    manager.fail_job(
        job_id,
        "AI provider failed",
    )

    job = manager.get_job(job_id)

    assert job["status"] == "failed"
    assert job["error"] == "AI provider failed"
    assert job["completed_at"] is not None


def test_fail_job_ignores_missing_job():
    manager = JobManager()

    manager.fail_job(
        "missing-job",
        "Some error",
    )

    assert manager.get_all_jobs() == []


def test_get_job_returns_none_for_missing_job():
    manager = JobManager()

    assert manager.get_job("missing-job") is None


def test_get_all_jobs_returns_all_jobs():
    manager = JobManager()

    first_job = manager.create_job(
        repository="owner/repo-one",
        pull_request=1,
    )

    second_job = manager.create_job(
        repository="owner/repo-two",
        pull_request=2,
    )

    jobs = manager.get_all_jobs()

    assert len(jobs) == 2
    assert jobs[0]["job_id"] == first_job
    assert jobs[1]["job_id"] == second_job


def test_delete_job_removes_job():
    manager = JobManager()

    job_id = manager.create_job(
        repository="test-owner/test-repo",
        pull_request=42,
    )

    assert manager.get_job(job_id) is not None

    manager.delete_job(job_id)

    assert manager.get_job(job_id) is None


def test_delete_job_ignores_missing_job():
    manager = JobManager()

    manager.delete_job("missing-job")

    assert manager.get_all_jobs() == []