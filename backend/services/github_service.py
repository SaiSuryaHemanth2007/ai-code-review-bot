"""
GitHub service.

Handles communication with the GitHub API.
"""

from github import Auth, Github
from github.GithubException import GithubException

from backend.core.logger import logger
from backend.core.settings import settings
from backend.utils.retry import retry


class GitHubService:
    """Service for interacting with the GitHub API."""

    AI_REVIEW_HEADER = "# 🤖 AI Code Review Report"

    def __init__(self):
        """
        Initialize GitHub client.

        During GitHub Actions tests there may be no
        GITHUB_TOKEN configured, so avoid crashing.
        """

        if settings.GITHUB_TOKEN:

            auth = Auth.Token(settings.GITHUB_TOKEN)
            self.github = Github(auth=auth)

            logger.info(
                "GitHub client initialized successfully."
            )

        else:

            logger.warning(
                "GitHub token not configured. "
                "GitHub client disabled."
            )

            self.github = None

    @retry(retries=3, delay=1, backoff=2)
    def get_repository(self):
        """Return the configured repository."""

        if self.github is None:
            raise RuntimeError(
                "GitHub client is not initialized."
            )

        repo_name = (
            f"{settings.GITHUB_OWNER}/"
            f"{settings.GITHUB_REPOSITORY}"
        )

        logger.info(
            "Connecting to repository: %s",
            repo_name,
        )

        return self.github.get_repo(repo_name)

    @retry(retries=3, delay=1, backoff=2)
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
                "open_pull_requests": repo.get_pulls(
                    state="open"
                ).totalCount,
            }

        except GithubException:

            logger.exception(
                "GitHub connection failed."
            )

            raise

    @retry(retries=3, delay=1, backoff=2)
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

        except GithubException:

            logger.exception(
                "Failed to fetch pull requests."
            )

            raise

    @retry(retries=3, delay=1, backoff=2)
    def get_pull_request_files(
        self,
        pull_number: int,
    ):
        """Return the files changed in a pull request."""

        try:

            repo = self.get_repository()

            pull = repo.get_pull(
                pull_number
            )

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
                        "blob_url": file.blob_url,
                        "raw_url": file.raw_url,
                        "contents_url": file.contents_url,
                    }
                )

            return result

        except GithubException:

            logger.exception(
                "Failed to fetch pull request files."
            )

            raise

    @retry(retries=3, delay=1, backoff=2)
    def upsert_pull_request_comment(
        self,
        pull_number: int,
        comment: str,
    ):
        """
        Create or update the AI review comment.
        """

        try:

            repo = self.get_repository()

            pull = repo.get_pull(
                pull_number
            )

            comments = pull.get_issue_comments()

            for existing_comment in comments:

                if existing_comment.body.startswith(
                    self.AI_REVIEW_HEADER
                ):

                    logger.info(
                        "Updating AI review comment (ID=%s)",
                        existing_comment.id,
                    )

                    existing_comment.edit(
                        comment
                    )

                    logger.info(
                        "Updated existing AI review comment."
                    )

                    return

            created_comment = pull.create_issue_comment(
                comment
            )

            logger.info(
                "Created new AI review comment (ID=%s).",
                created_comment.id,
            )

        except GithubException:

            logger.exception(
                "Failed to create/update PR comment."
            )

            raise

    @retry(retries=3, delay=1, backoff=2)
    def create_inline_review_comment(
        self,
        pull_number: int,
        file_path: str,
        line: int,
        comment: str,
    ):
        """
        Post an inline review comment.
        """

        try:

            repo = self.get_repository()

            pull = repo.get_pull(
                pull_number
            )

            commits = list(
                pull.get_commits()
            )

            if not commits:
                raise RuntimeError(
                    "No commits found for pull request."
                )

            latest_commit = commits[-1]

            review_comment = pull.create_review_comment(
                body=comment,
                commit=latest_commit,
                path=file_path,
                line=line,
                side="RIGHT",
            )

            logger.info(
                "Successfully posted inline review to %s (line %s). Review ID=%s",
                file_path,
                line,
                review_comment.id,
            )

        except GithubException:

            logger.exception(
                "Failed to post inline review."
            )

            raise


github_service = GitHubService()