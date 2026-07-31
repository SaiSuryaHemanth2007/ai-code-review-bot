from backend.jobs.job_manager import job_manager
from backend.services.review_service import review_service


class ReviewWorker:
    """
    Executes AI review jobs.
    """

    @staticmethod
    def run_review(
        job_id: str,
        pull_number: int,
    ):
        try:

            # Job started
            job_manager.start_job(job_id)

            job_manager.update_progress(job_id, 20)

            # Run AI Review
            result = review_service.review_pull_request(
                pull_number
            )

            job_manager.update_progress(job_id, 90)

            # Save result
            job_manager.complete_job(
                job_id,
                result,
            )

        except Exception as e:

            job_manager.fail_job(
                job_id,
                str(e),
            )


review_worker = ReviewWorker()