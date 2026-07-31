from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend.core.logger import logger
from backend.schemas.review_request import ReviewRequest
from backend.schemas.review_response import ReviewResponse
from backend.services.review_service import review_service
from backend.jobs.job_manager import job_manager
from backend.jobs.review_worker import review_worker
from backend.schemas.job_response import JobResponse
from backend.schemas.job_status import JobStatusResponse
from backend.core.settings import settings

router = APIRouter()


@router.post(
    "/review",
    response_model=ReviewResponse,
    summary="Review source code",
)
async def review_code(request: ReviewRequest):
    try:
        logger.info("Review request received.")

        review = review_service.review(
            request.code,
            request.language,
        )

        return ReviewResponse(
            success=True,
            language=request.language,
            review=review,
        )

    except Exception as exc:
        logger.exception("Review failed.")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

@router.post(
    "/review/start",
    response_model=JobResponse,
    summary="Start AI review in background",
)
def start_review(
    pull_number: int,
    background_tasks: BackgroundTasks,
):
    """
    Starts an AI review as a background job.
    """

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


@router.get(
    "/review/jobs",
    summary="List all review jobs",
)
def get_all_jobs():
    """
    Returns all review jobs.
    """
    return job_manager.get_all_jobs()


@router.get(
    "/review/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get review job status",
)
def get_job(job_id: str):
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

@router.get("/review/jobs")
def get_all_jobs():
    """
    Returns all review jobs.
    """
    return job_manager.get_all_jobs()