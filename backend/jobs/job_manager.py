import threading
import uuid
from datetime import datetime, UTC
from typing import Dict, Optional

from backend.core.logger import logger


class JobManager:
    """
    Manages background review jobs.
    """

    def __init__(self):
        self.jobs: Dict[str, dict] = {}
        self.lock = threading.Lock()

    def create_job(
        self,
        repository: str,
        pull_request: int,
    ) -> str:
        """
        Create a new review job.
        """

        job_id = str(uuid.uuid4())

        job = {
            "job_id": job_id,
            "repository": repository,
            "pull_request": pull_request,
            "status": "queued",
            "progress": 0,
            "result": None,
            "error": None,
            "created_at": datetime.now(UTC).isoformat(),
            "started_at": None,
            "completed_at": None,
        }

        with self.lock:
            self.jobs[job_id] = job

        logger.info(
            "Created review job: %s",
            job_id,
        )

        return job_id

    def start_job(
        self,
        job_id: str,
    ):
        """
        Mark job as running.
        """

        with self.lock:

            if job_id not in self.jobs:
                return

            self.jobs[job_id]["status"] = "running"
            self.jobs[job_id]["started_at"] = (
                datetime.now(UTC).isoformat()
            )

        logger.info(
            "Started review job: %s",
            job_id,
        )

    def update_progress(
        self,
        job_id: str,
        progress: int,
    ):
        """
        Update progress percentage.
        """

        progress = max(
            0,
            min(progress, 100),
        )

        with self.lock:

            if job_id not in self.jobs:
                return

            self.jobs[job_id]["progress"] = progress

    def complete_job(
        self,
        job_id: str,
        result,
    ):
        """
        Mark job as completed.
        """

        with self.lock:

            if job_id not in self.jobs:
                return

            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["progress"] = 100
            self.jobs[job_id]["result"] = result
            self.jobs[job_id]["completed_at"] = (
                datetime.now(UTC).isoformat()
            )

        logger.info(
            "Completed review job: %s",
            job_id,
        )

    def fail_job(
        self,
        job_id: str,
        error: str,
    ):
        """
        Mark job as failed.
        """

        with self.lock:

            if job_id not in self.jobs:
                return

            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error"] = error
            self.jobs[job_id]["completed_at"] = (
                datetime.now(UTC).isoformat()
            )

        logger.error(
            "Review job failed: %s",
            job_id,
        )

    def get_job(
        self,
        job_id: str,
    ) -> Optional[dict]:
        """
        Get a single job.
        """

        with self.lock:
            return self.jobs.get(job_id)

    def get_all_jobs(self):
        """
        Return all jobs.
        """

        with self.lock:
            return list(self.jobs.values())

    def delete_job(
        self,
        job_id: str,
    ):
        """
        Delete a completed job.
        """

        with self.lock:

            if job_id not in self.jobs:
                return

            del self.jobs[job_id]

        logger.info(
            "Deleted review job: %s",
            job_id,
        )


job_manager = JobManager()