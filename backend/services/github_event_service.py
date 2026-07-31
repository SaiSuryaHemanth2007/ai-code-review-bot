from typing import Any, Dict


class GitHubEventService:
    """
    Processes GitHub webhook events.
    """

    REVIEW_ACTIONS = {
        "opened",
        "reopened",
        "synchronize",
    }

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
            raise ValueError("Pull request data not found.")

        return pull_request["number"]

    def get_repository(
        self,
        payload: Dict[str, Any],
    ) -> str:
        """
        Return owner/repository.
        """

        repository = payload.get("repository")

        if not repository:
            raise ValueError("Repository data not found.")

        return repository["full_name"]


github_event_service = GitHubEventService()


class GitHubEventService:
    """
    Processes GitHub webhook events.
    """

    REVIEW_ACTIONS = {
        "opened",
        "reopened",
        "synchronize",
    }

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
            raise ValueError("Pull request data not found.")

        return pull_request["number"]

    def get_repository(
        self,
        payload: Dict[str, Any],
    ) -> str:
        """
        Return owner/repository.
        """

        repository = payload.get("repository")

        if not repository:
            raise ValueError("Repository data not found.")

        return repository["full_name"]


github_event_service = GitHubEventService()