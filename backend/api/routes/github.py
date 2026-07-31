from fastapi import APIRouter

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
async def cache():
    return get_cache_statistics()


@router.get(
    "/debug",
    summary="Debug Environment",
)
async def debug():
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
async def github_whoami():
    user = github_service.github.get_user()

    return {
        "login": user.login,
        "id": user.id,
    }


@router.get(
    "/repository",
    summary="Repository Information",
)
async def repository_info():
    return github_service.get_repository_info()


@router.get(
    "/pulls",
    summary="List Open Pull Requests",
)
async def list_pull_requests():
    return github_service.get_pull_requests()


@router.get(
    "/pulls/{pull_number}/files",
    summary="Get Pull Request Files",
)
async def get_pull_request_files(pull_number: int):
    return github_service.get_pull_request_files(pull_number)


@router.post(
    "/pulls/{pull_number}/review",
    response_model=PullRequestReviewResponse,
    summary="Review Pull Request",
)
async def review_pull_request(pull_number: int):
    return review_service.review_pull_request(pull_number)