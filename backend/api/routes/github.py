from fastapi import APIRouter

from backend.services.github_service import github_service

router = APIRouter()


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