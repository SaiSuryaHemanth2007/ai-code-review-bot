"""
GitHub service.

Handles communication with the GitHub API.
"""

from github import Github
from github.GithubException import GithubException

from backend.core.logger import logger
from backend.core.settings import settings


class GitHubService:
    """Service for interacting with GitHub."""

    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN)

    def get_repository(self):
        """Return the configured repository."""

        repo_name = (
            f"{settings.GITHUB_OWNER}/"
            f"{settings.GITHUB_REPOSITORY}"
        )

        logger.info("Connecting to repository: %s", repo_name)

        return self.github.get_repo(repo_name)

    def get_repository_info(self):
        """Return basic repository information."""

        try:
            repo = self.get_repository()

            return {
                "name": repo.name,
                "owner": repo.owner.login,
                "description": repo.description,
                "default_branch": repo.default_branch,
                "stars": repo.stargazers_count,
                "open_pull_requests": repo.get_pulls(state="open").totalCount,
            }

        except GithubException as exc:
            logger.exception("GitHub connection failed.")
            raise Exception(str(exc))

    def get_pull_requests(self):
        """Return all open pull requests."""

        try:
            repo = self.get_repository()

            pulls = repo.get_pulls(state="open")

            result = []

            for pr in pulls:
                result.append(
                    {
                        "number": pr.number,
                        "title": pr.title,
                        "author": pr.user.login,
                        "state": pr.state,
                        "created_at": pr.created_at,
                    }
                )

            return result

        except GithubException as exc:
            logger.exception("Failed to fetch pull requests.")
            raise Exception(str(exc))

    def get_pull_request_files(self, pull_number: int):
        """Return the files changed in a pull request."""

        try:
            repo = self.get_repository()

            pull = repo.get_pull(pull_number)

            files = pull.get_files()

            result = []

            for file in files:
                result.append(
                    {
                        "filename": file.filename,
                        "status": file.status,
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "changes": file.changes,
                        "patch": file.patch,
                    }
                )

            return result

        except GithubException as exc:
            logger.exception("Failed to fetch pull request files.")
            raise Exception(str(exc))


github_service = GitHubService()