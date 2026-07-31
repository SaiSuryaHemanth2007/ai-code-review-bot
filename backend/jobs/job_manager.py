import threading
import uuid
from datetime import datetime
from typing import Dict, Optional


class JobManager:
    """
    Manages background review jobs.
    """

    def __init__(self):
        self.jobs: Dict[str, dict] = {}
        self.lock = threading.Lock()

    def create_job(self, repository: str, pull_request: int) -> str:
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
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
        }

        with self.lock:
            self.jobs[job_id] = job

        return job_id

    def start_job(self, job_id: str):
        """
        Mark job as running.
        """

        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "running"
                self.jobs[job_id]["started_at"] = datetime.utcnow().isoformat()

    def update_progress(self, job_id: str, progress: int):
        """
        Update progress percentage.
        """

        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["progress"] = progress

    def complete_job(self, job_id: str, result):
        """
        Mark job as completed.
        """

        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["progress"] = 100
                self.jobs[job_id]["result"] = result
                self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()

    def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed.
        """

        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["error"] = error
                self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()

    def get_job(self, job_id: str) -> Optional[dict]:
        """
        Get a single job.
        """

        return self.jobs.get(job_id)

    def get_all_jobs(self):
        """
        Return all jobs.
        """

        return list(self.jobs.values())

    def delete_job(self, job_id: str):
        """
        Delete a completed job.
        """

        with self.lock:
            if job_id in self.jobs:
                del self.jobs[job_id]


job_manager = JobManager()