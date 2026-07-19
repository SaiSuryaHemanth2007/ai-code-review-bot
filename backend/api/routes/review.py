from fastapi import APIRouter, HTTPException

from backend.core.logger import logger
from backend.schemas.review_request import ReviewRequest
from backend.schemas.review_response import ReviewResponse
from backend.services.review_service import review_service

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