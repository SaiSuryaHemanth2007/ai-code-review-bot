from typing import Any, Dict


class GitHubEventService:
    """
    Processes GitHub webhook events.
    """

    REVIEW_ACTIONS = frozenset(
        {
            "opened",
            "reopened",
            "synchronize",
        }
    )

    def should_review(
        self,
        event: str,
        payload: Dict[str, Any],
    ) -> bool:
        """
        Determine whether the webhook should trigger an AI review.
        """

        if event != "pull_request":
            return False

        action = payload.get("action")

        return action in self.REVIEW_ACTIONS

    def get_pull_request_number(
        self,
        payload: Dict[str, Any],
    ) -> int:
        """
        Extract the pull request number.
        """

        pull_request = payload.get("pull_request")

        if not pull_request:
            raise ValueError(
                "Pull request data not found."
            )

        pull_number = pull_request.get("number")

        if pull_number is None:
            raise ValueError(
                "Pull request number not found."
            )

        return pull_number

    def get_repository(
        self,
        payload: Dict[str, Any],
    ) -> str:
        """
        Return owner/repository.
        """

        repository = payload.get("repository")

        if not repository:
            raise ValueError(
                "Repository data not found."
            )

        repository_name = repository.get(
            "full_name"
        )

        if not repository_name:
            raise ValueError(
                "Repository full_name not found."
            )

        return repository_name


github_event_service = GitHubEventService()