from backend.core.logger import logger
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
        """
        Execute an AI review job.
        """

        logger.info(
            "Starting AI review job: %s",
            job_id,
        )

        try:

            # Mark job as started
            job_manager.start_job(job_id)

            job_manager.update_progress(
                job_id,
                10,
            )

            logger.info(
                "Running AI review for PR #%s",
                pull_number,
            )

            # Run AI Review
            result = review_service.review_pull_request(
                pull_number
            )

            job_manager.update_progress(
                job_id,
                90,
            )

            # Save result
            job_manager.complete_job(
                job_id,
                result,
            )

            logger.info(
                "AI review job completed: %s",
                job_id,
            )

        except Exception:

            logger.exception(
                "AI review job failed: %s",
                job_id,
            )

            job_manager.fail_job(
                job_id,
                "Review execution failed.",
            )

            raise


review_worker = ReviewWorker()