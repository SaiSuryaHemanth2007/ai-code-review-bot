from typing import Any, Dict

from backend.jobs.job_manager import job_manager
from backend.jobs.review_worker import review_worker
from backend.services.github_event_service import github_event_service


class WebhookService:
    """
    Handles GitHub webhook requests.
    """

    def process_webhook(
        self,
        event: str,
        payload: Dict[str, Any],
        background_tasks,
    ):
        """
        Process a GitHub webhook event.
        """

        if not github_event_service.should_review(
            event,
            payload,
        ):
            return {
                "success": True,
                "message": "Event ignored.",
                "job_id": None,
            }

        repository = github_event_service.get_repository(
            payload,
        )

        pull_number = github_event_service.get_pull_request_number(
            payload,
        )

        job_id = job_manager.create_job(
            repository=repository,
            pull_request=pull_number,
        )

        background_tasks.add_task(
            review_worker.run_review,
            job_id,
            pull_number,
        )

        return {
            "success": True,
            "message": "Webhook processed successfully.",
            "job_id": job_id,
        }


webhook_service = WebhookService()