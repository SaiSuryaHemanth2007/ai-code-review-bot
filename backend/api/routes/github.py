from fastapi import APIRouter, HTTPException

from backend.core.settings import settings
from backend.schemas.pull_request_review_response import (
    PullRequestReviewResponse,
)
from backend.services.github_service import github_service
from backend.services.review_service import review_service
from backend.utils.review_cache import get_cache_statistics

router = APIRouter()


@router.get(
    "/cache",
    summary="Review Cache Statistics",
)
async def cache() -> dict:
    """
    Return review cache statistics.
    """

    return get_cache_statistics()


@router.get(
    "/debug",
    summary="Debug Environment",
)
async def debug() -> dict:
    """
    Development-only environment diagnostics.
    """

    if not settings.DEBUG:
        raise HTTPException(
            status_code=404,
            detail="Not Found",
        )

    return {
        "github_token_exists": bool(settings.GITHUB_TOKEN),
        "github_token_length": len(settings.GITHUB_TOKEN),
        "github_owner": settings.GITHUB_OWNER,
        "github_repository": settings.GITHUB_REPOSITORY,
    }


@router.get(
    "/whoami",
    summary="GitHub Authentication Test",
)
async def github_whoami() -> dict:
    """
    Development-only GitHub authentication check.
    """

    if not settings.DEBUG:
        raise HTTPException(
            status_code=404,
            detail="Not Found",
        )

    if github_service.github is None:
        raise HTTPException(
            status_code=503,
            detail="GitHub client is unavailable.",
        )

    user = github_service.github.get_user()

    return {
        "login": user.login,
        "id": user.id,
    }


@router.get(
    "/repository",
    summary="Repository Information",
)
async def repository_info() -> dict:
    """
    Return configured repository information.
    """

    return github_service.get_repository_info()


@router.get(
    "/pulls",
    summary="List Open Pull Requests",
)
async def list_pull_requests() -> list:
    """
    Return all open pull requests.
    """

    return github_service.get_pull_requests()


@router.get(
    "/pulls/{pull_number}/files",
    summary="Get Pull Request Files",
)
async def get_pull_request_files(
    pull_number: int,
) -> list:
    """
    Return files changed in a pull request.
    """

    return github_service.get_pull_request_files(
        pull_number
    )


@router.post(
    "/pulls/{pull_number}/review",
    response_model=PullRequestReviewResponse,
    summary="Review Pull Request",
)
async def review_pull_request(
    pull_number: int,
) -> PullRequestReviewResponse:
    """
    Run an AI review for the specified pull request.
    """

    return review_service.review_pull_request(
        pull_number
    )