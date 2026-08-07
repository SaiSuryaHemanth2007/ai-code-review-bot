from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend.core.settings import settings
from backend.core.logger import logger

from backend.jobs.job_manager import job_manager
from backend.jobs.review_worker import review_worker

from backend.schemas.job_response import JobResponse
from backend.schemas.job_status import JobStatusResponse

from backend.schemas.review_request import ReviewRequest
from backend.schemas.review_response import (
    ReviewResponse,
    ReviewResult,
    QualityResponse,
    ReviewIssue,
)

from backend.services.review_service import review_service

from backend.utils.quality_score import QualityScore

router = APIRouter()


@router.post(
    "/review",
    response_model=ReviewResponse,
    summary="Review source code",
)
async def review_code(
    request: ReviewRequest,
) -> ReviewResponse:
    """
    Review source code using AI.
    """

    try:

        logger.info(
            "Review request received."
        )

        ai_review = review_service.review(
            request.code,
            request.language,
        )

        issues = ai_review.get("issues", [])

        # Calculate quality score from issues
        critical = sum(
            1 for issue in issues
            if issue.get("severity", "").upper() == "CRITICAL"
        )

        high = sum(
            1 for issue in issues
            if issue.get("severity", "").upper() == "HIGH"
        )

        medium = sum(
            1 for issue in issues
            if issue.get("severity", "").upper() == "MEDIUM"
        )

        low = sum(
            1 for issue in issues
            if issue.get("severity", "").upper() == "LOW"
        )

        quality = QualityScore.calculate(
            critical=critical,
            high=high,
            medium=medium,
            low=low,
        )

        return ReviewResponse(
            success=True,
            language=request.language,
            review=ReviewResult(
                quality=QualityResponse(
                    score=quality["score"],
                    grade=quality["grade"],
                    stars=quality["stars"],
                ),
                summary=ai_review.get(
                    "summary",
                    "No summary generated.",
                ),
                issues=[
                    ReviewIssue(**issue)
                    for issue in issues
                ],
            ),
        )

    except Exception:

        logger.exception(
            "Review failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Review failed.",
        )


@router.post(
    "/review/start",
    response_model=JobResponse,
    summary="Start AI review in background",
)
async def start_review(
    pull_number: int,
    background_tasks: BackgroundTasks,
) -> JobResponse:
    """
    Starts an AI review as a background job.
    """

    try:

        if (
            not settings.GITHUB_OWNER
            or not settings.GITHUB_REPOSITORY
        ):
            raise HTTPException(
                status_code=500,
                detail="GitHub repository is not configured.",
            )

        repository = (
            f"{settings.GITHUB_OWNER}/"
            f"{settings.GITHUB_REPOSITORY}"
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

        return JobResponse(
            message="Review job created successfully.",
            job_id=job_id,
            status="queued",
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Failed to create review job."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create review job.",
        )

@router.get(
    "/review/jobs",
    summary="List all review jobs",
)
def get_all_jobs() -> list:
    """
    Returns all review jobs.
    """

    return job_manager.get_all_jobs()


@router.get(
    "/review/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get review job status",
)
def get_job(
    job_id: str,
) -> JobStatusResponse:
    """
    Returns a single review job.
    """

    job = job_manager.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return JobStatusResponse(**job)